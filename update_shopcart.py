import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check the current shopcart table schema
cursor.execute("PRAGMA table_info(shopcart)")
columns = cursor.fetchall()
print("Current shopcart table columns:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}, Nullable: {column[3]}")

# Add customer_id column
try:
    print("\nAdding customer_id column...")
    cursor.execute("ALTER TABLE shopcart ADD COLUMN customer_id INTEGER NULL REFERENCES customer(id)")
    print("Column added successfully!")
except sqlite3.OperationalError as e:
    print(f"Error adding customer_id: {e}")

# Add date_added column
try:
    print("\nAdding date_added column...")
    cursor.execute("ALTER TABLE shopcart ADD COLUMN date_added DATETIME NULL")
    # Set default value for existing rows
    cursor.execute("UPDATE shopcart SET date_added = CURRENT_TIMESTAMP")
    print("Column added successfully!")
except sqlite3.OperationalError as e:
    print(f"Error adding date_added: {e}")

# Add last_updated column
try:
    print("\nAdding last_updated column...")
    cursor.execute("ALTER TABLE shopcart ADD COLUMN last_updated DATETIME NULL")
    # Set default value for existing rows
    cursor.execute("UPDATE shopcart SET last_updated = CURRENT_TIMESTAMP")
    print("Column added successfully!")
except sqlite3.OperationalError as e:
    print(f"Error adding last_updated: {e}")

# Commit changes
conn.commit()
print("\nChanges committed successfully!")

# Verify the changes
cursor.execute("PRAGMA table_info(shopcart)")
columns = cursor.fetchall()
print("\nUpdated shopcart table columns:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}, Nullable: {column[3]}")

# Close the connection
conn.close()

print("\nShopcart table update complete!")
