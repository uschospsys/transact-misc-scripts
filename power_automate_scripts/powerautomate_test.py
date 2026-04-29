import pandas as pd
import sys
import os
from excel_writer import export_report_to_excel

def unit_selection(row):
    item_num = str(row.get('item_number', ''))
    item_cat = str(row.get('item_cat_name', ''))
    if 'DISCOUNT' in item_num: return 'DISCOUNT'
    
    mapping = {
        'C&G': 'C&G', 'Taco Taco': 'Taco Taco', 'Burger Crush': 'Burger Crush',
        'Chicken Tenders': 'Chicken Tenders', 'Panda Express': 'Panda Express',
        'Filones': 'Filones', 'Slice Shop': 'Slice Shop',
        'RTCC Bowls Express': 'Bowls Express', 'RTCC Bowls': 'Bowls',
        'RTCC Upstairs': 'Upstairs', 'RTCC Pop Up': 'Pop Up'
    }
    for key, val in mapping.items():
        if key in item_cat: return val
    return 'Other'


def build_report_df(final_df):
    # 1. Define the exact columns in the report df
    target_columns = [
        ('Units', ''), 
        ('Breakfast', 'Items Sold'), ('Breakfast', 'Sales'),
        ('Lunch', 'Items Sold'), ('Lunch', 'Sales'),
        ('Dinner', 'Items Sold'), ('Dinner', 'Sales'),
        ('Total Items Sold', ''),
        ('Total Sales', '')
    ]
    multi_col = pd.MultiIndex.from_tuples(target_columns)
    
    # 2. Extract data safely from final_df
    # We use .get() so if a column is missing (like Lunch), it doesn't crash
    units = final_df.index.values
    brk_qty = final_df.get(('Breakfast', 'item_qty'), 0)
    brk_price = final_df.get(('Breakfast', 'item_price'), 0)
    
    lch_qty = final_df.get(('Lunch', 'item_qty'), 0)
    lch_price = final_df.get(('Lunch', 'item_price'), 0)
    
    din_qty = final_df.get(('Dinner', 'item_qty'), 0)
    din_price = final_df.get(('Dinner', 'item_price'), 0)
    
    total_qty = final_df.get(('Sum of item_qty', 'Total'), 0)
    total_sales = final_df.get(('Sum of item_price', 'Total'), 0)
    
    # 3. Create a dictionary mapping the NEW columns to the data
    data_map = {
        ('Units', ''): units,
        ('Breakfast', 'Items Sold'): brk_qty,
        ('Breakfast', 'Sales'): brk_price,
        ('Lunch', 'Items Sold'): lch_qty,
        ('Lunch', 'Sales'): lch_price,
        ('Dinner', 'Items Sold'): din_qty,
        ('Dinner', 'Sales'): din_price,
        ('Total Items Sold', ''): total_qty,
        ('Total Sales', ''): total_sales
    }
    
    # 4. Build the final report
    report_df = pd.DataFrame(data_map, columns=multi_col)

    return report_df


def process_data(file_path):
    # 1. Load and Clean
    df = pd.read_csv(file_path)
    df['tdatetime'] = pd.to_datetime(df['tdatetime'])
    df = df[(df["location_name"] == "RTCC Food Court") & (df["item_number"] != "DISCOUNT")].copy()

    # 2. Add Categorical Columns
    df['Meal Period'] = pd.cut(df['tdatetime'].dt.hour, bins=[0, 11, 16, 24], 
                               labels=['Breakfast', 'Lunch', 'Dinner'], right=False)
    df['Unit'] = df.apply(unit_selection, axis=1)
    
    # 3. Build the Manual Pivot Structure
    # Grouping by Unit and Meal Period
    grouped = df.groupby(['Unit', 'Meal Period'], observed=False)[['item_qty', 'item_price']].sum().unstack()

    # 4. Add "Grand Totals" for Rows (Across Meal Periods)
    grouped[('Total', 'Sum of item_qty')] = grouped['item_qty'].sum(axis=1)
    grouped[('Total', 'Sum of item_price')] = grouped['item_price'].sum(axis=1)

    # 5. Add "Grand Totals" for Columns (Across all Units)
    # We create a final row by summing the columns
    total_row = grouped.sum()
    total_row.name = 'Grand Total'
    final_df = pd.concat([grouped, total_row.to_frame().T])

    # 6. Formatting the Headers
    # Currently, columns are (item_qty, Breakfast), (item_qty, Lunch), etc.
    # We swap levels to get (Meal Period, Measure) to match your requirement
    final_df = final_df.swaplevel(0, 1, axis=1).sort_index(axis=1, level=0)

    # 7. Build a report_df according to the multi level column indexes
    report_df = build_report_df(final_df)
    
    # 8. Write to Excel
    output_path = r'C:\Users\mprasanna\Desktop\misc\Final_Report.xlsx'
    excel_file = export_report_to_excel(report_df, "April", "2026", df)
    
    with open(output_path, "wb") as f:
        f.write(excel_file.getbuffer())
        
    print(f"File created successfully at: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_data(sys.argv[1])