# db_test.py
"""
Simple script to test PostgreSQL connection to Railway.
"""

import psycopg2
from psycopg2 import OperationalError
import config  # Import your config.py

def test_connection():
    try:
        # Attempt to connect to PostgreSQL using config.py settings
        connection = psycopg2.connect(
            host=config.DB_HOST,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASS,
            port=config.DB_PORT,
            sslmode="require"   # Railway requires SSL for public connections
        )
        print("✅ Connection to PostgreSQL on Railway was successful!")

        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")  # Get current database time
        current_time = cursor.fetchone()
        print(f"🕒 Database server time: {current_time[0]}")

        # Close connection
        cursor.close()
        connection.close()
        print("🔌 Connection closed.")

    except OperationalError as e:
        print("❌ Failed to connect to the database.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_connection()
