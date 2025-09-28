"""
PDFReport Class
Generates PDF report including title, chart, and monthly summary table
based on 'business' table data.
Saves PDF in 'reports/' folder.
"""

# pdf_report.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch # Import for using relative units
import config
import os

class PDFReport:
    def __init__(self, monthly_summary):
        self.monthly_summary = monthly_summary
        os.makedirs('reports', exist_ok=True)
        # Ensure config.PDF_FILE is defined with the correct path
        if not hasattr(config, 'PDF_FILE'):
             config.PDF_FILE = 'fintrack_report.pdf' 
        config.PDF_FILE = os.path.join('reports', config.PDF_FILE)

    def generate_pdf(self):
        doc = SimpleDocTemplate(
            config.PDF_FILE, 
            pagesize=letter,
            title=config.REPORT_TITLE if hasattr(config, 'REPORT_TITLE') else "Financial Report"
        )
        styles = getSampleStyleSheet()
        elements = []

        # --- Main Title ---
        elements.append(Paragraph(config.REPORT_TITLE, styles['Title']))
        elements.append(Spacer(1, 0.25 * inch))

        # --- Chart (Improved size) ---
        elements.append(Paragraph("Monthly Income vs Expenses Chart", styles['h2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        if os.path.exists(config.CHART_FILE):
            # Use a size that fills the page well (approx 6.5 x 3.5 inches)
            elements.append(Image(config.CHART_FILE, width=6.5 * inch, height=3.5 * inch))
            elements.append(Spacer(1, 0.5 * inch))
        else:
            elements.append(Paragraph("⚠️ Chart file not found, skipping chart in PDF.", styles['Normal']))

        # --- Monthly Summary Table ---
        elements.append(Paragraph("Monthly Summary by Category", styles['h2']))
        elements.append(Spacer(1, 0.1 * inch))

        # 1. Prepare table data
        # The table headers should be the column names of the summary DataFrame
        
        # Table Header
        column_names = self.monthly_summary.columns.tolist()
        table_data = [column_names]
        
        # Data: Iterate over DataFrame rows
        for index, row in self.monthly_summary.iterrows():
            row_values = []
            for col_name, value in row.items():
                if col_name in ['Income', 'Expense']:
                    # Currency format with thousand separator and two decimals
                    # Use Python f-string with comma for thousand separator (locale-aware)
                    formatted_value = f"${value:,.2f}"
                else:
                    # 'month' and 'category' are text
                    formatted_value = str(value)
                row_values.append(formatted_value)
            table_data.append(row_values)
            
        # 2. Create and apply styles
        table = Table(table_data)
        
        # Define the professional table style
        table_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')), # Dark background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # White text
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # Bold
            
            # Lines
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Alignment for currency data (Income, Expense columns)
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'), 
            ('ALIGN', (0, 0), (1, -1), 'LEFT'), # Alignment for text (Month, Category)
            
            # Alternating background (zebra-striping) for data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')), # Light background default
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eeeeee')]),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))

        # --- Build the PDF ---
        doc.build(elements)
        print(f"✅ PDF report generated: {config.PDF_FILE}")
