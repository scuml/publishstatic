
from .s3 import S3Storage
from .local import LocalStorage

class Storage(object):

    @staticmethod
    def factory(type, bucket_name):
        """
        Return a storage object. Call with Storage.factory('S3')
        """
        if type == "S3": return S3Storage(bucket_name)
        if type == "local": return LocalStorage(bucket_name)
        assert 0, "Invalid Storage Type: " + type
