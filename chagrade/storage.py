from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class PublicStorage(S3Boto3Storage):
    default_acl = "public-read"


if settings.TEST:
    PublicStorage = FileSystemStorage
