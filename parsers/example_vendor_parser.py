#!/usr/bin/env python3
"""
Example Vendor Parser Template

This module provides a template for creating vendor-specific parsers.
Each vendor may have a different invoice format, so extend this class
to handle specific vendor invoice structures.

Usage:
    from parsers.example_vendor_parser import ExampleVendorParser
    
    parser = ExampleVendorParser()
    items = parser.parse('path/to/vendor_invoice.csv')
"""

import csv
from typing import List, Dict, Any


class ExampleVendorParser:
    """
    Template parser for vendor invoices.
    
    Extend this class for vendor-specific parsing logic.
    """
    
    def __init__(self):
        """Initialize the parser."""
        self.vendor_name = "example_vendor"
    
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse a vendor invoice file.
        
        Args:
            filepath: Path to the invoice file
            
        Returns:
            List of item dictionaries with keys:
                - item_name: Product name
                - quantity: Numeric quantity
                - unit: Unit of measure
                - unit_price: Price per unit
                - total_price: Total line item price
        """
        items = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                item = self._parse_row(row)
                if item:
                    items.append(item)
        
        return items
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse a single row from the invoice.
        
        This method should be overridden in vendor-specific parsers
        to handle specific column names and formats.
        
        Args:
            row: Dictionary representing one row from the CSV
            
        Returns:
            Item dictionary or None if row should be skipped
        """
        # Example: generic column name mapping
        # Override this method for vendor-specific logic
        
        item_name = row.get('Item', row.get('Product', ''))
        if not item_name:
            return None
        
        # Parse quantity
        try:
            quantity = float(row.get('Qty', row.get('Quantity', '1')))
        except ValueError:
            quantity = 1.0
        
        # Parse unit
        unit = row.get('Unit', row.get('UOM', ''))
        
        # Parse unit price
        try:
            unit_price_str = row.get('Unit Price', row.get('Price', '0'))
            unit_price = float(str(unit_price_str).replace('$', '').replace(',', ''))
        except ValueError:
            unit_price = 0.0
        
        # Calculate total
        total_price = quantity * unit_price
        
        return {
            'item_name': item_name,
            'quantity': quantity,
            'unit': unit,
            'unit_price': unit_price,
            'total_price': total_price
        }


class VendorAParser(ExampleVendorParser):
    """
    Example: Parser for Vendor A's specific format.
    
    Vendor A uses columns: "Product Name", "Qty Ordered", "Price Each"
    """
    
    def __init__(self):
        super().__init__()
        self.vendor_name = "vendor_a"
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse Vendor A's specific format."""
        item_name = row.get('Product Name', '')
        if not item_name:
            return None
        
        try:
            quantity = float(row.get('Qty Ordered', '1'))
        except ValueError:
            quantity = 1.0
        
        unit = row.get('Unit of Measure', '')
        
        try:
            unit_price_str = row.get('Price Each', '0')
            unit_price = float(str(unit_price_str).replace('$', '').replace(',', ''))
        except ValueError:
            unit_price = 0.0
        
        return {
            'item_name': item_name,
            'quantity': quantity,
            'unit': unit,
            'unit_price': unit_price,
            'total_price': quantity * unit_price
        }


class VendorBParser(ExampleVendorParser):
    """
    Example: Parser for Vendor B's specific format.
    
    Vendor B uses columns: "Description", "Amount", "Unit Cost"
    """
    
    def __init__(self):
        super().__init__()
        self.vendor_name = "vendor_b"
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse Vendor B's specific format."""
        item_name = row.get('Description', '')
        if not item_name:
            return None
        
        try:
            quantity = float(row.get('Amount', '1'))
        except ValueError:
            quantity = 1.0
        
        unit = ''  # Vendor B doesn't specify units
        
        try:
            unit_price_str = row.get('Unit Cost', '0')
            unit_price = float(str(unit_price_str).replace('$', '').replace(',', ''))
        except ValueError:
            unit_price = 0.0
        
        return {
            'item_name': item_name,
            'quantity': quantity,
            'unit': unit,
            'unit_price': unit_price,
            'total_price': quantity * unit_price
        }
