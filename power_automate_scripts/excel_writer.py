from excel_formats import (
    dict_header_format,
    dict_number_format,
    dict_currency_format,
    dict_percent_format,
    dict_index_format,
    dict_totals_index_format,
    dict_total_currency_format,
    dict_total_percent_format,
    dict_merge_format,
    dict_total_number_format
)

import pandas as pd
from io import BytesIO

def export_report_to_excel(df, month, year, og_df):
    output = BytesIO()
    date_str = f"{month} {year}"
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet = workbook.add_worksheet('Sales Report')
        
        # 1. Define Formats
        # Header 1 (Top): No bottom border
        dict_header0 = dict_header_format.copy()
        dict_header0.update({'bottom': 0}) 
        
        # Header 2 (Bottom): Keep the thick bottom border (6)
        dict_header1 = dict_header_format.copy()
        
        fmts = {k: workbook.add_format(v) for k, v in {
            'header0': dict_header0,
            'header1': dict_header1,
            'num': dict_number_format,
            'curr': dict_currency_format,
            'unit': dict_index_format,
            'total_unit': dict_totals_index_format,
            'total_num': dict_total_number_format,
            'total_curr': dict_total_currency_format,
            'title': dict_merge_format
        }.items()}

        raw_sheet = workbook.add_worksheet('RawData')
        og_df.to_excel(writer, sheet_name='RawData', index=False)

        # 2. Setup Offsets (Start at Column B, Row 3)
        start_row = 2  # Row 3
        start_col = 1  # Column B

        # 3. Write Title (Merged across the table width)
        sheet.merge_range(start_row - 1, start_col, start_row - 1, start_col + 8, 
                          f'USC RTCC Sales and Patron Count Report - {date_str}', fmts['title'])

        # 4. Write Headers with Merging
        # We manually define the merge ranges for the top level
        # Units, Total Items, and Total Sales are vertically merged
        sheet.merge_range(start_row, start_col, start_row + 1, start_col, 'Units', fmts['header1'])
        
        # Meal Periods: Merged horizontally across 2 columns
        sheet.merge_range(start_row, start_col + 1, start_row, start_col + 2, 'Breakfast', fmts['header0'])
        sheet.merge_range(start_row, start_col + 3, start_row, start_col + 4, 'Lunch', fmts['header0'])
        sheet.merge_range(start_row, start_col + 5, start_row, start_col + 6, 'Dinner', fmts['header0'])
        
        # Totals: Vertically merged
        sheet.merge_range(start_row, start_col + 7, start_row + 1, start_col + 7, 'Total Items Sold', fmts['header1'])
        sheet.merge_range(start_row, start_col + 8, start_row + 1, start_col + 8, 'Total Sales', fmts['header1'])

        # Write Second Level (Sub-headers)
        sub_headers = ['Items Sold', 'Sales', 'Items Sold', 'Sales', 'Items Sold', 'Sales']
        for i, text in enumerate(sub_headers):
            sheet.write(start_row + 1, start_col + 1 + i, text, fmts['header1'])

        # 5. Write Data
        for i, row in enumerate(df.values):
            curr_row = start_row + 2 + i
            is_grand_total = "Grand Total" in str(row)
            
            for j, value in enumerate(row):
                # Check if 'Sales' appears in either the top level or sub level of the column header
                col_tuple = df.columns[j]
                is_currency = any("Sales" in str(level) for level in col_tuple)
                
                # # Check if column should be currency
                # is_currency = "Sales" in df.columns[j] or "Sales" in df.columns[j]
                
                if is_grand_total:
                    fmt = fmts['total_curr'] if is_currency else fmts['total_num']
                    if j == 0: fmt = fmts['total_unit']
                else:
                    fmt = fmts['curr'] if is_currency else fmts['num']
                    if j == 0: fmt = fmts['unit']
                
                sheet.write(curr_row, start_col + j, value, fmt)

        # 6. Set Column Widths (Adjusting for the offset)
        sheet.set_column(start_col, start_col, 25) 
        sheet.set_column(start_col + 1, start_col + 8, 15)

    output.seek(0)
    return output