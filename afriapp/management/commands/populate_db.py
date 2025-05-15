from django.core.management.base import BaseCommand
from afriapp.views import populate_db

class Command(BaseCommand):
    help = 'Populates the database with initial data if it is empty'

    def handle(self, *args, **options):
        result = populate_db()
        if result:
            self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Database already contains data. No changes made.'))
