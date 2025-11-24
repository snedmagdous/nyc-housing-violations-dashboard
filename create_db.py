"""
Temporary script to create the database.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server (not a specific database)
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="4853"
)

# Set autocommit mode (required for CREATE DATABASE)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create cursor
cursor = conn.cursor()

try:
    # Create database
    cursor.execute("CREATE DATABASE nyc_housing_violations;")
    print("[SUCCESS] Database 'nyc_housing_violations' created successfully!")
except psycopg2.errors.DuplicateDatabase:
    print("[INFO] Database 'nyc_housing_violations' already exists.")
except Exception as e:
    print(f"[ERROR] Error creating database: {e}")
finally:
    cursor.close()
    conn.close()
