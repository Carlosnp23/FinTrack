# db_connection.py
"""
DatabaseConnection Class
Handles connecting to PostgreSQL on Railway and retrieving business transaction data.
"""

import psycopg2
import pandas as pd
import config

class DatabaseConnection:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=config.DB_HOST,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASS,
                port=config.DB_PORT
            )
            print("✅ Connected to Railway Database")
        except Exception as e:
            print("❌ Database connection failed:", e)
            raise

    def fetch_transactions(self):
        """Fetch all records from 'business' table as pandas DataFrame."""
        if not self.conn:
            self.connect()

        query = """
        SELECT date, month, transaction_type, category, description,
               vendor_client, amount_cad, tax_rate, tax_amount_cad, total_cad
        FROM business
        ORDER BY date;
        """

        df = pd.read_sql_query(query, self.conn)
        return df

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("🔒 Database connection closed")
