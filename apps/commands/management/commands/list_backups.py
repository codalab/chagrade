from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Lists database dumps, optionally search through them by passing a search keyword"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('search', nargs='?', type=str)

    def handle(self, *args, **options):
        # Get backups, filtering by search if exists
        _, backups = default_storage.listdir('backups/')
        search = options.get('search')
        available_backups = []

        for backup in backups:
            if search and search not in backup:
                continue
            available_backups.append(backup)

        if available_backups:
            header_string = f"Backups ({len(available_backups)} found)"
            print(header_string)

            print("=" * len(header_string))
            for backup in available_backups:
                print(f"  {backup}")
        else:
            print("No backups found.")
        print()


