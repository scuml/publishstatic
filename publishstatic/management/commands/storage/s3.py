import boto
from ..common import get_required_env_variable

class S3Storage(object):

    def __init__(self, bucket=None):
        """
        Establish connections.

        Assume credentials are in environment or
        in a config file.
        """
        self.s3_conn = boto.connect_s3()

        # Have a default bucket, so individual function calls don't
        # need to query global settings and pass the bucket each time.
        # self.bucket will only be used in common utility functions, such
        # an download_file and upload_file, nothing "dangerous" like
        # "empty_bucket" or "delete_bucket."
        if bucket is not None:
            self.bucket = bucket

        get_required_env_variable('AWS_ACCESS_KEY_ID')
        get_required_env_variable('AWS_SECRET_ACCESS_KEY')


    def upload_contents(self, content, key, headers):
        headers['x-amz-acl'] = 'public-read'
        key = self.bucket.new_key(key)
        key.set_contents_from_file(content, headers)
        return key

    def close(self):
        """
        Close connection.
        """
        self.s3_conn.close()
