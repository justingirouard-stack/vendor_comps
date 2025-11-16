#!/usr/bin/env python3
"""
Helper for writing vendor price comparison data to Excel format.
"""
import pandas as pd
from pathlib import Path

def write_comparison_excel(df, output_path):
    """
    Write the vendor price comparison DataFrame to an Excel file.
    
    Args:
        df: pandas DataFrame containing comparison data
        output_path: Path object or string for output file
    """
    output_path = Path(output_path)
    
    # Write to Excel with some basic formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Vendor Comparison')
        
        # Get the worksheet
        worksheet = writer.sheets['Vendor Comparison']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
