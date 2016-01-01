#!/usr/bin/env python

"""
A local stand-in for S3. For testing.
"""

from os.path import join, dirname, exists, isfile
from os import errno
from os import makedirs
from logging import getLogger


class LocalStorage(object):
    """
    A local replacement for S3.
    """
    def __init__(self, path):
        """
        Establish connections.

        Assume credentials are in environment or
        in a config file.
        """
        self.logger = getLogger(__name__)
        self.path = path
        try:
            makedirs(path)
        except OSError as ex:
            if ex.errno == errno.EEXIST:
                # Path already exists. All is good.
                return
            self.logger.critical(
                "LocalStore can't create '{0}', '{1}".format(path, ex))

    def upload(self, stream, filename, headers=None):
        """
        'Upload' a file to a path by writing to it.
        Don't overwrite existing files.
        """
        location = join(self.path, filename)
        if not exists(dirname(location)):
            makedirs(dirname(location))
        if isfile(location):
            return location
        local_handle = open(location, 'wb')
        content = stream.read()
        local_handle.write(content)
        local_handle.close()
        return location


    def close(self):
        """
        Close connection.
        """
        # pylint: disable=no-self-use
        # This is a mock object, so it needs to implement close().
        return None
