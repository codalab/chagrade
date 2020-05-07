import os

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Grabs a database dump from remote storage"

    def add_arguments(self, parser):
        parser.add_argument('backup_path', type=str, help='Name of backup to download, relative to /backups/')

    def handle(self, *args, **options):
        backup_path = options['backup_path']
        local_path = f'/backups/{backup_path}'
        if not os.path.exists(local_path):
            print(f"Didn't find dump locally, downloading to {local_path}..")
            with open(local_path, "wb") as f:
                dump = default_storage.open(f'backups/{backup_path}').read()
                f.write(dump)
            print("..done!")
        else:
            print("Dump found locally already.")

        print()
        print(f"Now you may run ./bin/pg_restore.sh {backup_path}")
        print()
