import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURATION ---
FILE_INTERNAL = 'internal_ledger.csv'
FILE_BANK = 'bank_statement.csv'
REPORT_FILE = f'Recon_Report_{datetime.now().strftime("%Y%m%d")}.xlsx'

print("--- STARTING TRADE RECONCILIATION PROCESS ---")

# 1. Load Data
try:
    df_int = pd.read_csv(FILE_INTERNAL)
    df_bank = pd.read_csv(FILE_BANK)
    print(f"Loaded {len(df_int)} Internal trades and {len(df_bank)} Bank lines.")
except FileNotFoundError:
    print("Error: Input files not found. Run 'generate_trades.py' first.")
    exit()

# 2. Data Cleaning 
df_int['Trade_ID'] = df_int['Trade_ID'].astype(str).str.strip()
df_bank['Trade_ID'] = df_bank['Trade_ID'].astype(str).str.strip()

# 3. Perform Matching (Outer Join)
# 'Outer' join ensures we keep trades that are missing in one side
df_recon = pd.merge(df_int, df_bank, on='Trade_ID', how='outer', suffixes=('_Int', '_Bank'))

# 4. The "Brain" (Categorization Logic)
def categorize_break(row):
    # Case 1: Trade exists internally but NOT in bank
    if pd.isna(row['Price_Bank']):
        return "MISSING IN BANK"
    
    # Case 2: Trade exists in bank but NOT internally
    elif pd.isna(row['Price_Int']):
        return "MISSING INTERNAL"
    
    # Case 3: Quantity Mismatch
    elif row['Qty_Int'] != row['Qty_Bank']:
        return "QTY MISMATCH"
    
    # Case 4: Price Mismatch (Allow 0.01 tolerance for float math)
    elif abs(row['Price_Int'] - row['Price_Bank']) > 0.01:
        return "PRICE MISMATCH"
    
    # Case 5: Perfect Match
    else:
        return "MATCH"

# Apply Logic
print("Running matching algorithms...")
df_recon['Recon_Status'] = df_recon.apply(categorize_break, axis=1)

# 5. Export to Excel with Formatting
print(f"Generating Report: {REPORT_FILE}")

writer = pd.ExcelWriter(REPORT_FILE, engine='xlsxwriter')
df_recon.to_excel(writer, sheet_name='Reconciliation', index=False)

# Get workbook objects for formatting
workbook  = writer.book
worksheet = writer.sheets['Reconciliation']

# Define Formats
red_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
green_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
yellow_fmt = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

# Apply Conditional Formatting to Status Column
# Find the column index for 'Recon_Status'
status_col_idx = df_recon.columns.get_loc('Recon_Status')
end_row = len(df_recon)

# Green for MATCH
worksheet.conditional_format(1, status_col_idx, end_row, status_col_idx,
                             {'type': 'cell', 'criteria': '==', 'value': '"MATCH"', 'format': green_fmt})

# Red for MISSING
worksheet.conditional_format(1, status_col_idx, end_row, status_col_idx,
                             {'type': 'text', 'criteria': 'containing', 'value': 'MISSING', 'format': red_fmt})

# Yellow for MISMATCH (Price/Qty)
worksheet.conditional_format(1, status_col_idx, end_row, status_col_idx,
                             {'type': 'text', 'criteria': 'containing', 'value': 'MISMATCH', 'format': yellow_fmt})

# Auto-adjust column widths
for i, col in enumerate(df_recon.columns):
    max_len = max(df_recon[col].astype(str).map(len).max(), len(col)) + 2
    worksheet.set_column(i, i, max_len)

writer.close()

print("✅ Process Complete.")
