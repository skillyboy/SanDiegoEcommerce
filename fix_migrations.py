"""
Script to fix migration issues in the SanDiegoEcommerce project.
This will mark all migrations as applied without actually running them.
"""

import os
import django
from django.core.management import call_command

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Fake all migrations
print("Faking all migrations...")
call_command('migrate', 'afriapp', fake=True)
call_command('migrate', 'logistics', fake=True)
call_command('migrate', 'agro_linker', fake=True)
call_command('migrate', 'admin', fake=True)
call_command('migrate', 'auth', fake=True)
call_command('migrate', 'contenttypes', fake=True)
call_command('migrate', 'sessions', fake=True)

print("All migrations faked successfully. Now you can run the server normally.")
