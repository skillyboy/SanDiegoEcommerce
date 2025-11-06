"""
Script to fake the initial migration for the logistics app.
This will mark the migration as applied without actually running it.
"""

import os
import django
from django.core.management import call_command

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Fake the initial migration
print("Faking initial migration for logistics app...")
call_command('migrate', 'logistics', '0001_initial', fake=True)

print("Migration faked successfully. Now you can run migrations normally.")
