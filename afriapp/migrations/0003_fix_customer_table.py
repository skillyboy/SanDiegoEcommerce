from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration replaces the problematic 0003_alter_customer_table.py migration.
    """

    dependencies = [
        ('afriapp', '0002_product_fields'),
    ]

    operations = [
        # No operations needed, this is just to fix the migration graph
    ]
