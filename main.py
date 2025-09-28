"""
main.py
FinTrack - Business Finance Report Generator
Generates Excel, PDF, and charts based on 'business' table from PostgreSQL (Railway).
"""

from db_connection import DatabaseConnection
from excel_report import ExcelReport
from pdf_report import PDFReport
import config
import os

def main():
    # 1️⃣ Connect to the database and fetch data
    db = DatabaseConnection()
    df = db.fetch_transactions()
    db.close()

    if df.empty:
        print("⚠️ No data found in the database.")
        return

    # 2️⃣ Generate Excel report and monthly summary DataFrame
    excel = ExcelReport(df)
    monthly_summary_df = excel.generate_excel()  # returns pivot DataFrame

    # 3️⃣ Generate chart from monthly summary
    excel.generate_chart(monthly_summary_df)

    # 4️⃣ Generate PDF report directly from monthly_summary_df
    pdf = PDFReport(monthly_summary_df)
    pdf.generate_pdf()

if __name__ == "__main__":
    os.makedirs('reports', exist_ok=True)
    main()
