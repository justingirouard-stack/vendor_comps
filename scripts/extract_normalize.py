#!/usr/bin/env python3
"""
Invoice Extraction and Normalization Pipeline

Orchestrates parsing vendor invoices, normalizing units and prices,
fuzzy-matching items to a master product list, and producing a 
comparison Excel workbook.

Usage:
    python scripts/extract_normalize.py --input-dir tests/fixtures \
                                         --output-dir output \
                                         --master-products master_products.csv
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Import custom modules
try:
    from normalize_units import parse_quantity_unit, normalize_unit
    from xlsx_writer import create_vendor_comparison_workbook
except ImportError:
    # If running from scripts directory
    sys.path.insert(0, os.path.dirname(__file__))
    from normalize_units import parse_quantity_unit, normalize_unit
    from xlsx_writer import create_vendor_comparison_workbook

# Try to import vendor parsers
try:
    from parsers.example_vendor_parser import ExampleVendorParser
except ImportError:
    # If parsers not available, use a simple CSV parser
    ExampleVendorParser = None


def load_master_products(master_csv_path: str) -> List[str]:
    """Load the canonical product list from CSV."""
    products = []
    if not os.path.exists(master_csv_path):
        print(f"Warning: Master products file not found: {master_csv_path}")
        return products
    
    with open(master_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'product_name' in row:
                products.append(row['product_name'])
    
    return products


def parse_invoice_file(filepath: str) -> List[Dict[str, Any]]:
    """Parse a vendor invoice CSV file into line items."""
    items = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract item details - handle various column name variations
            item_name = row.get('Item', row.get('item', row.get('Product', '')))
            qty_str = row.get('Qty', row.get('qty', row.get('Quantity', '1')))
            unit_price_str = row.get('Unit Price', row.get('unit_price', 
                                     row.get('Price', '0.00')))
            
            # Parse quantity and unit
            quantity, unit = parse_quantity_unit(qty_str)
            
            # Parse unit price
            try:
                unit_price = float(str(unit_price_str).replace('$', '').replace(',', '').strip())
            except (ValueError, AttributeError):
                unit_price = 0.0
            
            items.append({
                'item_name': item_name,
                'quantity': quantity,
                'unit': unit,
                'normalized_unit': normalize_unit(unit),
                'unit_price': unit_price,
                'total_price': quantity * unit_price
            })
    
    return items


def fuzzy_match_to_master(item_name: str, master_products: List[str]) -> str:
    """Simple fuzzy matching to find best match in master product list."""
    if not master_products:
        return item_name
    
    # Try exact match first (case insensitive)
    item_lower = item_name.lower().strip()
    for product in master_products:
        if product.lower().strip() == item_lower:
            return product
    
    # Try substring matching
    for product in master_products:
        if item_lower in product.lower() or product.lower() in item_lower:
            return product
    
    # No match found, return original
    return item_name


def process_invoices(input_dir: str, master_products: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Process all invoice files in the input directory."""
    vendor_data = {}
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return vendor_data
    
    # Process all CSV files in input directory
    for filepath in input_path.glob('*.csv'):
        print(f"Processing: {filepath.name}")
        
        # Extract vendor name from filename (e.g., "vendorname_invoice_001.csv" -> "vendorname")
        vendor_name = filepath.stem.split('_')[0]
        
        # Parse invoice
        items = parse_invoice_file(str(filepath))
        
        # Apply fuzzy matching to master products
        for item in items:
            item['matched_product'] = fuzzy_match_to_master(item['item_name'], master_products)
        
        # Store vendor data
        if vendor_name not in vendor_data:
            vendor_data[vendor_name] = []
        vendor_data[vendor_name].extend(items)
    
    return vendor_data


def main():
    """Main entry point for the extraction pipeline."""
    parser = argparse.ArgumentParser(
        description='Extract and normalize vendor invoices'
    )
    parser.add_argument('--input-dir', required=True,
                        help='Directory containing vendor invoice CSV files')
    parser.add_argument('--output-dir', required=True,
                        help='Directory to write output files')
    parser.add_argument('--master-products', required=True,
                        help='Path to master products CSV file')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load master products
    print(f"Loading master products from: {args.master_products}")
    master_products = load_master_products(args.master_products)
    print(f"Loaded {len(master_products)} master products")
    
    # Process all invoices
    print(f"Processing invoices from: {args.input_dir}")
    vendor_data = process_invoices(args.input_dir, master_products)
    
    if not vendor_data:
        print("Warning: No invoice data found")
        return
    
    print(f"Processed {len(vendor_data)} vendor(s)")
    
    # Generate comparison workbook
    output_file = output_path / 'vendor_price_comparison.xlsx'
    print(f"Creating output workbook: {output_file}")
    create_vendor_comparison_workbook(vendor_data, str(output_file))
    
    print("Done!")


if __name__ == '__main__':
    main()
