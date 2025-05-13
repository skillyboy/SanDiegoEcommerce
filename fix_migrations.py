"""
Script to fix the migration issue with the logistics app.
This will:
1. Check if the tables already exist
2. Fake the initial migration if needed
3. Apply any remaining migrations
"""

import os
import django
import sqlite3
from django.conf import settings
from django.core.management import call_command

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Connect to the database
db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_partner';")
delivery_partner_exists = cursor.fetchone() is not None

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_zone';")
delivery_zone_exists = cursor.fetchone() is not None

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shipment';")
shipment_exists = cursor.fetchone() is not None

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shipment_update';")
shipment_update_exists = cursor.fetchone() is not None

# Check if django_migrations table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';")
django_migrations_exists = cursor.fetchone() is not None

# Create django_migrations table if it doesn't exist
if not django_migrations_exists:
    print("Creating django_migrations table...")
    cursor.execute("""
    CREATE TABLE django_migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        applied DATETIME NOT NULL
    );
    """)
    conn.commit()

# Check if the logistics migration is already recorded
if django_migrations_exists:
    cursor.execute("SELECT id FROM django_migrations WHERE app='logistics' AND name='0001_initial';")
    migration_recorded = cursor.fetchone() is not None
else:
    migration_recorded = False

# Close the database connection
conn.close()

# If any of the tables exist but the migration is not recorded, fake the migration
if (delivery_partner_exists or delivery_zone_exists or shipment_exists or shipment_update_exists) and not migration_recorded:
    print("Tables exist but migration is not recorded. Faking initial migration...")
    call_command('migrate', 'logistics', '0001_initial', fake=True)
    print("Initial migration faked successfully.")
else:
    print("No need to fake migrations.")

# Apply any remaining migrations
print("Applying remaining migrations...")
call_command('migrate')
print("Migrations applied successfully.")
