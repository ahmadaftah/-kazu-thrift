import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'thrift_db'
}

def add_image_column():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Adding image_url column to inventory table...")
        
        # Add image_url column if not exists
        try:
            cursor.execute("""
                ALTER TABLE inventory 
                ADD COLUMN image_url VARCHAR(255) DEFAULT 'default-product.png'
            """)
            print("- Added 'image_url' column to inventory table")
        except mysql.connector.Error as e:
            if e.errno == 1060:  # Duplicate column name
                print("- Column 'image_url' already exists")
            else:
                raise
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\nDatabase schema updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_image_column()
