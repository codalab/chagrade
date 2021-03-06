import os

from .base import *


# =============================================================================
# Cloudcube storage
# =============================================================================
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

cloudcube_url = os.environ.get('CLOUDCUBE_URL')
cloudcube_bucket = os.path.basename(cloudcube_url)   # "bucketname"
cloudcube_base_url = os.path.dirname(cloudcube_url)

AWS_S3_ENDPOINT_URL = cloudcube_base_url
AWS_ACCESS_KEY_ID = os.environ.get('CLOUDCUBE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('CLOUDCUBE_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = cloudcube_bucket
AWS_STORAGE_PRIVATE_BUCKET_NAME = cloudcube_bucket
AWS_DEFAULT_ACL = os.environ.get('AWS_DEFAULT_ACL', 'private')
AWS_QUERYSTRING_AUTH = False

#STATICFILES_STORAGE = 'chagrade.storage.PublicStorage'
