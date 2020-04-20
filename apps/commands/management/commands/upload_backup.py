import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, get_storage_class
from django.core.management.base import BaseCommand


StorageClass = get_storage_class(settings.DEFAULT_FILE_STORAGE)
PrivateStorage = StorageClass(bucket=settings.AWS_STORAGE_PRIVATE_BUCKET_NAME)


class Command(BaseCommand):
    help = "Takes a database dump file and puts it on remote storage"

    def add_arguments(self, parser):
        parser.add_argument('backup_path', type=str, help='Path to backup to upload, relative to /backups/')

    def handle(self, *args, **options):
        backup_file_name = options['backup_path']
        backup_path = os.path.join("/backups", options['backup_path'])

        print(f"Uploading backup: {backup_path}")
        PrivateStorage.save(f'backups/{backup_file_name}', ContentFile(open(backup_path, 'rb').read()))

        # Clean up
        print(f"Removing local dump file: {backup_path}")
        os.remove(backup_path)
