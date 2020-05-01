import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Takes a database dump file and puts it on remote storage"

    def add_arguments(self, parser):
        parser.add_argument('backup_path', type=str, help='Name of backup to upload, relative to /backups/')

    def handle(self, *args, **options):
        backup_file_name = options['backup_path']
        backup_path = os.path.join("/backups", options['backup_path'])

        print(f"Uploading backup: {backup_path}")
        default_storage.save(f'backups/{backup_file_name}', ContentFile(open(backup_path, 'rb').read()))

        # Clean up
        print(f"Removing local dump file: {backup_path}")
        os.remove(backup_path)
