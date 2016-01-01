from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from utils import gzip_content, minify

from fnmatch import fnmatch
from io import BytesIO
import json
import mimetypes
import os
import sys

from storage import Storage

# The list of content types to gzip.
COMPRESSIBLE = [
    'text/plain',
    'text/csv',
    'application/xml',
    'application/javascript',
    'text/css'
]


class Command(BaseCommand):

    help = 'Compresses and uploads data to S3'
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--bucket',
            action='store',
            dest='bucket',
            default=None,
            help='Bucket name if not set in settings.AWS_BUCKET_NAME')

        parser.add_argument('--directory',
            action='store',
            dest='prefix',
            default=None,
            help='Subfolder to prepend to each file path')

        parser.add_argument('--minify',
            action='store_true',
            dest='minify',
            default=True,
            help='Minify css and js files.')

        parser.add_argument('--gzip',
            action='store_true',
            dest='gzip',
            default=False,
            help='Gzip the uploaded files.')

        parser.add_argument('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Silence output')

        parser.add_argument('--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Force upload all static files.')

        parser.add_argument('--pattern',
            action='store',
            dest='pattern',
            default='',
            help='Only upload files that match this pattern.')

    @property
    def publishfiles_path(self):
        from django.conf import settings
        return os.path.join(
            settings.STATIC_ROOT, 'publishfiles.{}.json'.format(self.storage_name))


    def determine_files_to_upload(self):
        """
        Returns a list of all files that should be uploaded to the server by
        checking staticfiles.json against publishfiles.json.
        """
        from django.conf import settings
        static_root = settings.STATIC_ROOT


        # Load static files
        static_files_json = os.path.join(static_root, 'staticfiles.json')
        if not os.path.isfile(static_files_json):
            raise Exception("Could not find staticfiles.json in {}.  "
                "Please make sure STATICFILES_STORAGE is set to "
                "'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'"
                " and you have run collectstatic.".format(static_root))

        static_handle = open(static_files_json)
        static_files = json.load(static_handle)

        # Get list of files that need uploading.
        all_files = list()
        for original, hashed in static_files['paths'].items():
            all_files.extend([original, hashed])

        published_files = self.load_json()

        all_files = set(all_files).difference(published_files)
        return all_files


    def load_json(self):
        """
        Returns thet set of all currently published files.
        """

        publish_files_json = self.publishfiles_path

        published_files = set()
        if os.path.isfile(publish_files_json):
            with open(publish_files_json, 'r') as publish_handle:
                try:
                    published_files = set(json.load(publish_handle)['published_files'])
                except ValueError:
                    pass
        return published_files

    def save_json(self, published_files):
        """
        Exports the list of published files to the publishfiles_path
        """

        publish_files_json = self.publishfiles_path

        with open(publish_files_json, 'w') as publish_handle:
            json.dump({"published_files": list(published_files)}, publish_handle)


    def delete_json(self):
        """
        Deletes the contents of the published files.
        """

        publish_files_json = self.publishfiles_path
        with open(publish_files_json, 'w') as publish_handle:
            json.dump({"published_files": list()}, publish_handle)


    def handle(self, *args, **options):

        from django.conf import settings
        static_root = settings.STATIC_ROOT

        if settings.STATICFILES_STORAGE != 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage':
            raise ImproperlyConfigured("The publishstatic command only works "
                "properly if STATICFILES_STORAGE is set to "
                "'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'."
        )

        # Get config
        self.storage_name = settings.PUBLISH_STORAGE_ENGINE
        if not self.storage_name:
            raise ImproperlyConfigured("Please set PUBLISH_STORAGE_ENGINE in "
                "your settings file.")

        if options['quiet']:
            sys.stdout = BytesIO()
        if options['bucket']:
            bucket_name = options['bucket']
        else:
            bucket_name = settings.PUBLISH_BUCKET_NAME or settings.PUBLISH_ROOT

        if not bucket_name:
            raise ImproperlyConfigured("Please set a bucket name for the static"
                " files with either --bucket or the setting AWS_BUCKET_NAME")


        if options['overwrite']:
            self.delete_json()

        storage = Storage.factory(self.storage_name, bucket_name)
        self.stdout.write("Using storage engine: {}".format(storage))

        directory = options.get('directory') or ''

        files_to_upload = self.determine_files_to_upload()
        published_files = self.load_json()

        for filename in files_to_upload:
            if options['pattern'] and not fnmatch(filename, options['pattern']):
                continue

            filetype, encoding = mimetypes.guess_type(filename)
            filetype = filetype or 'application/octet-stream'

            full_path = os.path.join(static_root, filename)
            states = set()

            with open(full_path, 'rb') as handle:
                stream = BytesIO(handle.read())

            if options['minify']:
                stream, state = minify(filename, filetype, stream)
                if state != '':
                    states.add(state)

            # Set default headers
            headers = {
                'Content-Type': filetype,
                'Cache-Control': 'max-age=%d' % (3600 * 24 * 365)
            }

            # Gzip if compressable
            if options['gzip'] is True and filetype in COMPRESSIBLE:
                headers, stream = gzip_content(headers, stream)
                states.add('gzipped')

            self.stdout.write("{} {}".format(
                filename, list(states) if states else ''))

            # Send to S3
            storage.upload(stream, os.path.join(directory, filename), headers)

            published_files.add(filename)


        self.save_json(published_files)

        if len(files_to_upload) == 0:
            self.stdout.write('No files changed on {} storage.'.format(
                self.storage_name
            ))
        else:
            self.stdout.write('Successfully uploaded {} files to {} bucket {}.'.format(
                len(files_to_upload), self.storage_name, bucket_name
            ))
