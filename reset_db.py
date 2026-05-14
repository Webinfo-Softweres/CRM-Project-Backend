import pymysql
from core.config import settings


def reset_database():
    # Connect to MySQL server (without specifying database)
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='160309',
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # Drop database if exists
            cursor.execute("DROP DATABASE IF EXISTS crm_db")
            print("Database dropped (if it existed)")
            
            # Create database
            cursor.execute("CREATE DATABASE crm_db")
            print("Database created: crm_db")
            
        connection.commit()
        print("\nDatabase reset complete. Now run: venv\\Scripts\\python init_db.py")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    reset_database()
