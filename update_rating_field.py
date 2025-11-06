import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check the current rating field type
cursor.execute("PRAGMA table_info(product)")
columns = cursor.fetchall()
for column in columns:
    if column[1] == 'rating':
        print(f"Current rating field: {column[1]}, Type: {column[2]}, Nullable: {column[3]}")

# Create a temporary column with the correct type
try:
    print("Creating temporary rating_decimal column...")
    cursor.execute("ALTER TABLE product ADD COLUMN rating_decimal DECIMAL(3,1) DEFAULT 0")
    
    # Copy data from rating to rating_decimal, converting as needed
    print("Copying and converting data...")
    cursor.execute("UPDATE product SET rating_decimal = CAST(CASE WHEN rating = '' OR rating IS NULL THEN '0' ELSE rating END AS DECIMAL(3,1))")
    
    # Rename columns (SQLite doesn't support direct column renaming, so we need to create a new table)
    print("Creating new table with correct schema...")
    cursor.execute("""
    CREATE TABLE product_new (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        price DECIMAL(10,2),
        image VARCHAR(100),
        description TEXT,
        featured BOOLEAN,
        latest BOOLEAN,
        available BOOLEAN,
        min INTEGER,
        max INTEGER,
        stock_quantity INTEGER UNSIGNED,
        options TEXT,
        date_created DATETIME,
        rating DECIMAL(3,1),
        category_id BIGINT,
        slug TEXT,
        sale_price DECIMAL(10,2),
        cultural_significance TEXT,
        last_updated DATETIME,
        min_purchase INTEGER,
        max_purchase INTEGER
    )
    """)
    
    # Copy data to the new table
    print("Copying data to new table...")
    cursor.execute("""
    INSERT INTO product_new (
        id, name, price, image, description, featured, latest, available, 
        min, max, stock_quantity, options, date_created, rating, category_id, 
        slug, sale_price, cultural_significance, last_updated, min_purchase, max_purchase
    )
    SELECT 
        id, name, price, image, description, featured, latest, available, 
        min, max, stock_quantity, options, date_created, rating_decimal, category_id, 
        slug, sale_price, cultural_significance, last_updated, min_purchase, max_purchase
    FROM product
    """)
    
    # Drop the old table and rename the new one
    print("Replacing old table with new table...")
    cursor.execute("DROP TABLE product")
    cursor.execute("ALTER TABLE product_new RENAME TO product")
    
    # Commit changes
    conn.commit()
    print("Changes committed successfully!")
    
except sqlite3.OperationalError as e:
    print(f"Error updating rating field: {e}")
    conn.rollback()

# Verify the changes
cursor.execute("PRAGMA table_info(product)")
columns = cursor.fetchall()
for column in columns:
    if column[1] == 'rating':
        print(f"Updated rating field: {column[1]}, Type: {column[2]}, Nullable: {column[3]}")

# Close the connection
conn.close()

print("\nRating field update complete!")
