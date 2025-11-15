#!/usr/bin/env python3
"""
Excel Workbook Writer

Creates multi-sheet Excel workbooks for vendor price comparisons.
Each vendor gets its own sheet, plus a summary sheet for comparison.
"""

from typing import Dict, List, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def create_vendor_comparison_workbook(vendor_data: Dict[str, List[Dict[str, Any]]], 
                                       output_path: str):
    """
    Create an Excel workbook with vendor price comparisons.
    
    Args:
        vendor_data: Dictionary mapping vendor names to lists of item dictionaries
        output_path: Path where the Excel file should be saved
    """
    # Create a new workbook
    wb = openpyxl.Workbook()
    
    # Remove default sheet
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
    
    # Create summary sheet
    create_summary_sheet(wb, vendor_data)
    
    # Create a sheet for each vendor
    for vendor_name, items in vendor_data.items():
        create_vendor_sheet(wb, vendor_name, items)
    
    # Save workbook
    wb.save(output_path)


def create_summary_sheet(wb: openpyxl.Workbook, vendor_data: Dict[str, List[Dict[str, Any]]]):
    """Create a summary sheet comparing all vendors."""
    ws = wb.create_sheet("Summary", 0)
    
    # Headers
    headers = ['Product', 'Vendor', 'Quantity', 'Unit', 'Unit Price', 'Total Price']
    ws.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Collect all products across vendors
    all_products = {}
    for vendor_name, items in vendor_data.items():
        for item in items:
            product = item.get('matched_product', item.get('item_name', ''))
            if product not in all_products:
                all_products[product] = []
            all_products[product].append({
                'vendor': vendor_name,
                'quantity': item.get('quantity', 0),
                'unit': item.get('normalized_unit', item.get('unit', '')),
                'unit_price': item.get('unit_price', 0),
                'total_price': item.get('total_price', 0)
            })
    
    # Add data rows
    for product, vendor_entries in sorted(all_products.items()):
        for entry in vendor_entries:
            ws.append([
                product,
                entry['vendor'],
                entry['quantity'],
                entry['unit'],
                entry['unit_price'],
                entry['total_price']
            ])
    
    # Format currency columns
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=5, max_col=6):
        for cell in row:
            cell.number_format = '$#,##0.00'
    
    # Auto-size columns
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Freeze header row
    ws.freeze_panes = 'A2'


def create_vendor_sheet(wb: openpyxl.Workbook, vendor_name: str, 
                        items: List[Dict[str, Any]]):
    """Create a sheet for a specific vendor."""
    # Sanitize sheet name (Excel has restrictions)
    sheet_name = vendor_name[:31]  # Max 31 characters
    ws = wb.create_sheet(sheet_name)
    
    # Headers
    headers = ['Item Name', 'Matched Product', 'Quantity', 'Unit', 
               'Normalized Unit', 'Unit Price', 'Total Price']
    ws.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Add data rows
    for item in items:
        ws.append([
            item.get('item_name', ''),
            item.get('matched_product', ''),
            item.get('quantity', 0),
            item.get('unit', ''),
            item.get('normalized_unit', ''),
            item.get('unit_price', 0),
            item.get('total_price', 0)
        ])
    
    # Format currency columns
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=6, max_col=7):
        for cell in row:
            cell.number_format = '$#,##0.00'
    
    # Auto-size columns
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Freeze header row
    ws.freeze_panes = 'A2'
