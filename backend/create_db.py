import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to default 'postgres' database
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Hrick.06@481",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'stylesense'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("CREATE DATABASE stylesense")
        print("Database 'stylesense' created successfully.")
    else:
        print("Database 'stylesense' already exists.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
