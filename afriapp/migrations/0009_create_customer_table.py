from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('afriapp', '0008_ensure_customer_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS "afriapp_customer" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "first_name" varchar(100) NULL,
                "last_name" varchar(100) NULL,
                "email" varchar(254) NOT NULL UNIQUE,
                "phone_number" varchar(15) NULL,
                "address" text NULL,
                "city" varchar(100) NULL,
                "state" varchar(100) NULL,
                "postal_code" varchar(10) NULL,
                "country" varchar(100) NULL,
                "date_joined" datetime NOT NULL,
                "is_guest" bool NOT NULL DEFAULT 0,
                "user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            "SELECT 1;"  # No-op for backwards migration
        ),
    ]
