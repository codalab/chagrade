from django.conf import settings
from django.core.files.storage import get_storage_class


StorageClass = get_storage_class(settings.DEFAULT_FILE_STORAGE)


class PublicStorage(StorageClass):
    default_acl = "public-read"
