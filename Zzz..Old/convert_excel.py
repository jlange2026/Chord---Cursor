#!/usr/bin/env python3
"""Convert Excel file to CSV for analysis"""

try:
    import pandas as pd
    import openpyxl
    
    # Read the Excel file
    df = pd.read_excel('Data_2026-01-21-dental.prod.xlsx')
    
    # Save as CSV
    df.to_csv('Data_2026-01-21-dental.prod.csv', index=False)
    
    # Print summary
    print(f"Successfully converted! Shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:\n{df.head()}")
    
except ImportError as e:
    print(f"Error: {e}")
    print("\nRequired packages not installed. Let me show you the alternative approach...")
    print("\nPlease export the Excel file to CSV format from Excel/Numbers/Google Sheets")
    print("Or we can try using a different method to analyze the data.")
