import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'thrift_db'
}

def update_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Updating database schema...")
        
        # 1. Add role column to users table if not exists
        try:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN role ENUM('Admin', 'Staff') DEFAULT 'Staff'
            """)
            print("✓ Added 'role' column to users table")
        except mysql.connector.Error as e:
            if e.errno == 1060:  # Duplicate column name
                print("✓ Column 'role' already exists")
            else:
                raise
        
        # 2. Update existing admin user to have Admin role
        cursor.execute("""
            UPDATE users SET role = 'Admin' WHERE username = 'admin'
        """)
        print("✓ Updated admin user role")
        
        # 3. Insert staff user if not exists
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, full_name, role) 
            VALUES ('staff', 'staff123', 'Staff Toko', 'Staff')
        """)
        print("✓ Added staff user")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Database updated successfully!")
        print("\nUser accounts:")
        print("  Admin: admin / admin123")
        print("  Staff: staff / staff123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_database()
