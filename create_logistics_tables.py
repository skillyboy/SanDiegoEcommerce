import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import necessary modules
from django.db import connection

# SQL statements to create the tables
create_delivery_zone_table = """
CREATE TABLE IF NOT EXISTS delivery_zone (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    base_fee DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
"""

create_delivery_partner_table = """
CREATE TABLE IF NOT EXISTS delivery_partner (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
"""

create_shipment_table = """
CREATE TABLE IF NOT EXISTS shipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    estimated_delivery DATETIME NULL,
    actual_delivery DATETIME NULL,
    shipping_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_id INTEGER NOT NULL,
    delivery_partner_id INTEGER NULL,
    delivery_zone_id INTEGER NULL,
    FOREIGN KEY (order_id) REFERENCES afriapp_order(id) ON DELETE CASCADE,
    FOREIGN KEY (delivery_partner_id) REFERENCES delivery_partner(id) ON DELETE SET NULL,
    FOREIGN KEY (delivery_zone_id) REFERENCES delivery_zone(id) ON DELETE SET NULL
);
"""

create_shipment_update_table = """
CREATE TABLE IF NOT EXISTS shipment_update (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(20) NOT NULL,
    location VARCHAR(100) NULL,
    notes TEXT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipment_id INTEGER NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipment(id) ON DELETE CASCADE
);
"""

# Execute the SQL statements
with connection.cursor() as cursor:
    print("Creating delivery_zone table...")
    cursor.execute(create_delivery_zone_table)

    print("Creating delivery_partner table...")
    cursor.execute(create_delivery_partner_table)

    print("Creating shipment table...")
    cursor.execute(create_shipment_table)

    print("Creating shipment_update table...")
    cursor.execute(create_shipment_update_table)

print("All tables created successfully!")
