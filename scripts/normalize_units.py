#!/usr/bin/env python3
"""
Unit Normalization Helpers

Provides utilities to parse quantity/unit text and normalize units
to standard forms for comparison.
"""

import re
from typing import Tuple


# Unit normalization mappings
UNIT_NORMALIZATIONS = {
    # Weight units
    'lb': 'pound',
    'lbs': 'pound',
    'pound': 'pound',
    'pounds': 'pound',
    'oz': 'ounce',
    'ounce': 'ounce',
    'ounces': 'ounce',
    'kg': 'kilogram',
    'kilogram': 'kilogram',
    'kilograms': 'kilogram',
    'g': 'gram',
    'gram': 'gram',
    'grams': 'gram',
    
    # Volume units
    'gal': 'gallon',
    'gallon': 'gallon',
    'gallons': 'gallon',
    'qt': 'quart',
    'quart': 'quart',
    'quarts': 'quart',
    'pt': 'pint',
    'pint': 'pint',
    'pints': 'pint',
    'fl oz': 'fluid_ounce',
    'fl. oz': 'fluid_ounce',
    'fluid ounce': 'fluid_ounce',
    'fluid ounces': 'fluid_ounce',
    'l': 'liter',
    'liter': 'liter',
    'liters': 'liter',
    'ml': 'milliliter',
    'milliliter': 'milliliter',
    'milliliters': 'milliliter',
    
    # Count units
    'ea': 'each',
    'each': 'each',
    'pc': 'piece',
    'pcs': 'piece',
    'piece': 'piece',
    'pieces': 'piece',
    'ct': 'count',
    'count': 'count',
    'case': 'case',
    'cases': 'case',
    'box': 'box',
    'boxes': 'box',
    'bag': 'bag',
    'bags': 'bag',
    'pk': 'pack',
    'pack': 'pack',
    'packs': 'pack',
}


def parse_quantity_unit(qty_str: str) -> Tuple[float, str]:
    """
    Parse a quantity string that may contain both number and unit.
    
    Examples:
        "10" -> (10.0, "")
        "10 lbs" -> (10.0, "lbs")
        "2.5 kg" -> (2.5, "kg")
        "5" -> (5.0, "")
    
    Args:
        qty_str: Quantity string to parse
        
    Returns:
        Tuple of (quantity as float, unit as string)
    """
    if not qty_str:
        return (1.0, "")
    
    qty_str = str(qty_str).strip()
    
    # Try to extract number and unit using regex
    # Matches patterns like "10", "10.5", "10 lbs", "2.5kg", etc.
    match = re.match(r'^([\d.]+)\s*(.*)$', qty_str)
    
    if match:
        try:
            quantity = float(match.group(1))
            unit = match.group(2).strip()
            return (quantity, unit)
        except ValueError:
            pass
    
    # If no number found, try to parse as just a number
    try:
        return (float(qty_str), "")
    except ValueError:
        # Default to 1 if cannot parse
        return (1.0, qty_str)


def normalize_unit(unit: str) -> str:
    """
    Normalize a unit string to a standard form.
    
    Args:
        unit: Unit string to normalize (e.g., "lbs", "lb", "pounds")
        
    Returns:
        Normalized unit string (e.g., "pound")
    """
    if not unit:
        return ""
    
    # Clean up the unit string
    unit_clean = unit.lower().strip()
    
    # Remove periods
    unit_clean = unit_clean.replace('.', '')
    
    # Look up in normalization table
    return UNIT_NORMALIZATIONS.get(unit_clean, unit_clean)


def convert_to_base_unit(quantity: float, unit: str) -> Tuple[float, str]:
    """
    Convert quantity to base unit for the unit type.
    
    This is a placeholder for future unit conversion logic.
    Currently just returns the normalized form.
    
    Args:
        quantity: Numeric quantity
        unit: Unit string
        
    Returns:
        Tuple of (converted quantity, base unit)
    """
    normalized = normalize_unit(unit)
    
    # Future: Add conversion factors here
    # For now, just return normalized
    return (quantity, normalized)
