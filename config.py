# config.py
"""
Configuration file for FinTrack - Business Finance Reports.
PostgreSQL connection details from Railway (public URL).
"""

# ==========================
# 🔸 PostgreSQL Database Info (Railway)
# ==========================
DB_HOST = "turntable.proxy.rlwy.net"
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASS = "xuXDkLvkosfrWKUEtfduCEBDMhoWeehz"
DB_PORT = 15268   # 👈 importante: no es el 5432 por defecto

# ==========================
# 📁 File Output Paths
# ==========================
EXCEL_FILE = "fintrack_report.xlsx"
PDF_FILE = "fintrack_report.pdf"
CHART_FILE = "fintrack_chart.png"

# ==========================
# ⚙️ Optional Settings
# ==========================
REPORT_TITLE = "📈 Business Monthly Financial Report"
COMPANY_NAME = "My Company Inc."
