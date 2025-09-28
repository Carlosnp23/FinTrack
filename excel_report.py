"""
ExcelReport Class
Generates Excel file with business transaction details and monthly summary.
Saves files in 'reports/' folder.
"""

# excel_report.py
import pandas as pd
import matplotlib.pyplot as plt
import config
import os
import matplotlib.ticker as mticker 
from matplotlib.ticker import FuncFormatter # Import FuncFormatter for safe currency display

class ExcelReport:
    def __init__(self, dataframe):
        self.df = dataframe.copy()
        os.makedirs('reports', exist_ok=True)
        # Assuming config.EXCEL_FILE and config.CHART_FILE are defined in config.py
        if hasattr(config, 'EXCEL_FILE'):
            config.EXCEL_FILE = os.path.join('reports', config.EXCEL_FILE)
        if hasattr(config, 'CHART_FILE'):
            config.CHART_FILE = os.path.join('reports', config.CHART_FILE)

    def normalize_months(self):
        """Ensure the month column has full month names (e.g., '1' becomes 'January')."""
        month_map = {
            '1': 'January', '2': 'February', '3': 'March', '4': 'April',
            '5': 'May', '6': 'June', '7': 'July', '8': 'August',
            '9': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        # Map month numbers (as string) to full month names
        self.df['month'] = self.df['month'].astype(str).map(lambda x: month_map.get(x, x))

    def preprocess(self):
        self.normalize_months()
        df = self.df.copy()

        # Define month order for final reindexing and sorting
        month_order = ['January','February','March','April','May','June',
                       'July','August','September','October','November','December']
        
        # 1. Pivot table: Group by both 'month' and 'category' for rows (the index), 
        #    and pivot on 'transaction_type' (income/expense) for columns.
        monthly_summary = df.pivot_table(
            index=['month', 'category'],
            columns='transaction_type',
            values='total_cad',
            aggfunc='sum',
            fill_value=0
        )
        
        # 2. Flatten the index to bring 'month' and 'category' back as columns
        monthly_summary = monthly_summary.reset_index()

        # 3. Rename columns and ensure Income/Expense columns exist
        rename_map = {}
        if 'income' in monthly_summary.columns:
            rename_map['income'] = 'Income'
        if 'expense' in monthly_summary.columns:
            rename_map['expense'] = 'Expense'
            
        monthly_summary.rename(columns=rename_map, inplace=True)
        
        if 'Income' not in monthly_summary.columns:
            monthly_summary['Income'] = 0
        if 'Expense' not in monthly_summary.columns:
            monthly_summary['Expense'] = 0

        # 4. Fill in missing Month-Category combinations (e.g., January has no 'Office Supplies')
        
        all_categories = self.df['category'].unique()
        # Create a complete index of all possible Month-Category combinations
        complete_index = pd.MultiIndex.from_product([month_order, all_categories], names=['month', 'category'])
        
        # Reindex against the complete index to add missing zeros
        monthly_summary = monthly_summary.set_index(['month', 'category']).reindex(complete_index, fill_value=0).reset_index()
        
        # 5. Sort by month (using the correct calendar order) and then by category
        monthly_summary['month'] = pd.Categorical(monthly_summary['month'], categories=month_order, ordered=True)
        monthly_summary.sort_values(by=['month', 'category'], inplace=True)
        
        # Select and reorder final columns
        monthly_summary = monthly_summary[['month', 'category', 'Income', 'Expense']]

        return monthly_summary

    def generate_excel(self):
        monthly_summary = self.preprocess()
        
        # Use xlsxwriter engine to apply number formatting
        with pd.ExcelWriter(config.EXCEL_FILE, engine='xlsxwriter') as writer:
            
            self.df.to_excel(writer, sheet_name='Business Data', index=False)
            monthly_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
            
            workbook = writer.book
            currency_format = workbook.add_format({'num_format': '#,##0.00'}) # Example: 1,234.56
            
            # Format 'Business Data' sheet
            business_sheet = writer.sheets['Business Data']
            business_cols = ['amount_cad', 'tax_amount_cad', 'total_cad']
            for col_name in business_cols:
                if col_name in self.df.columns:
                    col_idx = self.df.columns.get_loc(col_name)
                    business_sheet.set_column(col_idx, col_idx, None, currency_format)

            # Format 'Monthly Summary' sheet
            summary_sheet = writer.sheets['Monthly Summary']
            summary_cols = ['Income', 'Expense']
            for col_name in summary_cols:
                if col_name in monthly_summary.columns:
                    col_idx = monthly_summary.columns.get_loc(col_name)
                    summary_sheet.set_column(col_idx, col_idx, None, currency_format)
            
        print(f"✅ Excel report generated: {config.EXCEL_FILE}")
        return monthly_summary

    def generate_chart(self, monthly_summary):
        # Aggregate the detailed summary back to just month totals for the chart
        # FIX: Added observed=False to suppress the FutureWarning
        plot_df = monthly_summary.groupby('month', observed=False)[['Income', 'Expense']].sum()
        
        month_order = ['January','February','March','April','May','June',
                       'July','August','September','October','November','December']
        plot_df = plot_df.reindex(month_order, fill_value=0)
        
        plot_df_nonzero = plot_df[plot_df.sum(axis=1) != 0]

        if plot_df_nonzero.empty:
            print("⚠️ No data to plot. Skipping chart.")
            return

        # --- Professional Charting Improvements ---
        
        # Set a style for a cleaner look
        plt.style.use('seaborn-v0_8-darkgrid') 
        
        fig, ax = plt.subplots(figsize=(12, 6)) # Larger figure for better readability

        # Plot the bars
        plot_df_nonzero.plot(kind='bar', ax=ax, width=0.7) # Adjust bar width

        # Title and Labels
        ax.set_title('Monthly Income vs Expenses', fontsize=16, fontweight='bold', color='#333333')
        ax.set_xlabel('Month', fontsize=12, color='#555555')
        ax.set_ylabel('Total (CAD)', fontsize=12, color='#555555')

        # X-axis ticks
        ax.tick_params(axis='x', rotation=45, labelsize=10, colors='#555555')
        
        # Y-axis ticks and formatting 
        ax.tick_params(axis='y', labelsize=10, colors='#555555')
        
        # FIX: Replaced FormatStrFormatter with FuncFormatter to safely handle thousand separators (comma)
        def currency_formatter(x, pos):
            """Formats a number as currency with thousand separator."""
            # Use f-string formatting to safely add comma separators and the dollar sign
            return f'${x:,.0f}' 

        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        ax.grid(axis='y', linestyle='--', alpha=0.7) # Lighter grid lines

        # Customize the legend
        ax.legend(title='Transaction Type', title_fontsize='11', fontsize='10',
                  loc='upper left', bbox_to_anchor=(1, 1), # Place legend outside the plot
                  frameon=True, shadow=True, fancybox=True, edgecolor='gray')

        # Remove the top and right spines for a cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')

        plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for the legend
        
        # Save the chart
        plt.savefig(config.CHART_FILE, dpi=300, bbox_inches='tight') # High resolution, tight bounding box
        plt.close()
        print(f"📊 Chart saved as {config.CHART_FILE}")
