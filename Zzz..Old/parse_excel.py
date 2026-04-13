#!/usr/bin/env python3
"""Parse Excel file by extracting and parsing the internal XML"""

import zipfile
import xml.etree.ElementTree as ET
import csv
import re

# Open the Excel file as a zip
with zipfile.ZipFile('Data_2026-01-21-dental.prod.xlsx', 'r') as zip_ref:
    # Read shared strings
    shared_strings_xml = zip_ref.read('xl/sharedStrings.xml')
    shared_strings_root = ET.fromstring(shared_strings_xml)
    
    # Extract shared strings (text values)
    ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    shared_strings = []
    for si in shared_strings_root.findall('x:si', ns):
        t = si.find('x:t', ns)
        if t is not None:
            shared_strings.append(t.text if t.text else '')
        else:
            # Handle rich text
            texts = si.findall('.//x:t', ns)
            shared_strings.append(''.join(t.text if t.text else '' for t in texts))
    
    print(f"Found {len(shared_strings)} shared strings")
    
    # Read worksheet data
    sheet_xml = zip_ref.read('xl/worksheets/sheet1.xml')
    sheet_root = ET.fromstring(sheet_xml)
    
    # Parse rows and cells
    rows_data = []
    for row in sheet_root.findall('.//x:row', ns):
        row_data = {}
        for cell in row.findall('x:c', ns):
            # Get cell reference (e.g., 'A1', 'B2')
            cell_ref = cell.get('r')
            # Extract column letter
            col = re.match(r'([A-Z]+)', cell_ref).group(1)
            
            # Get cell type and value
            cell_type = cell.get('t')
            value_elem = cell.find('x:v', ns)
            
            if value_elem is not None:
                value = value_elem.text
                # If type is 's', it's a shared string reference
                if cell_type == 's':
                    value = shared_strings[int(value)]
                row_data[col] = value
            else:
                row_data[col] = ''
        
        rows_data.append(row_data)
    
    print(f"Found {len(rows_data)} rows")
    
    # Get all columns (sorted)
    all_columns = set()
    for row in rows_data:
        all_columns.update(row.keys())
    
    def col_to_num(col):
        """Convert column letter to number (A=1, B=2, ..., AA=27, etc.)"""
        num = 0
        for c in col:
            num = num * 26 + (ord(c) - ord('A') + 1)
        return num
    
    columns = sorted(all_columns, key=col_to_num)
    
    print(f"Columns: {columns}")
    print(f"\nFirst row (headers):")
    if rows_data:
        for col in columns:
            print(f"  {col}: {rows_data[0].get(col, '')}")
    
    # Convert to list of lists for CSV
    csv_data = []
    for row in rows_data:
        csv_row = [row.get(col, '') for col in columns]
        csv_data.append(csv_row)
    
    # Save as CSV
    with open('Data_2026-01-21-dental.prod.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    print(f"\n✓ Successfully converted to CSV!")
    print(f"\nFirst 5 data rows:")
    for i, row in enumerate(csv_data[1:6], start=2):
        print(f"Row {i}: {row[:5]}...")  # Show first 5 columns
