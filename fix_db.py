import mysql.connector
import os

db_config_no_db = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

def fix_database():
    try:
        # 1. Connect to MySQL without specifying database
        conn = mysql.connector.connect(**db_config_no_db)
        cursor = conn.cursor()
        
        # 2. Create database if not exists
        print("Using database 'thrift_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS thrift_db")
        cursor.execute("USE thrift_db")
        
        # 3. Read and execute SQL file
        sql_path = os.path.join(os.path.dirname(__file__), 'database.sql')
        if os.path.exists(sql_path):
            print(f"Executing {sql_path}...")
            with open(sql_path, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute one by one
            statements = sql_content.split(';')
            for statement in statements:
                if statement.strip():
                    print(f"Executing statement...")
                    cursor.execute(statement)
            
            conn.commit()
            print("Database initialized successfully!")
        else:
            print("Error: database.sql not found!")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database()
