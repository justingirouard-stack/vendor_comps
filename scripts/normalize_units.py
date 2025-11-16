"""
Helpers for parsing and normalizing quantity + unit into canonical units and numeric quantity.
"""
import re
from typing import Tuple

UNIT_ALIASES = {
    "lb": ["lb", "lbs", "pound", "pounds"],
    "kg": ["kg", "kilogram", "kilograms"],
    "g": ["g", "gram", "grams"],
    "oz": ["oz", "ounce", "ounces"],
    "ea": ["ea", "each", "unit", "units"],
    "case": ["case", "cs", "c/s"],
    "pack": ["pack", "pkg", "pk"],
}

def normalize_unit_name(raw: str) -> str:
    if not raw:
        return "ea"
    raw = raw.strip().lower().replace(".", "")
    for k, aliases in UNIT_ALIASES.items():
        for a in aliases:
            if raw == a or raw.startswith(a) or a in raw:
                return k
    return raw

def parse_quantity_unit(qs: str) -> Tuple[float, str]:
    if qs is None:
        return 1.0, "ea"
    s = str(qs).strip()
    if s == "":
        return 1.0, "ea"
    num_match = re.search(r"([\d,.]+)", s)
    if not num_match:
        return 1.0, normalize_unit_name(s)
    num = num_match.group(1).replace(",", "")
    try:
        quantity = float(num)
    except Exception:
        quantity = 1.0
    rest = s[num_match.end():].strip()
    if rest == "":
        return quantity, "ea"
    if "x" in rest or "*" in rest:
        parts = re.split(r"[x\*]", rest)
        if len(parts) >= 2:
            subnum = re.search(r"([\d,.]+)", parts[1])
            if subnum:
                # parse multiplicative form like "2 x 6 pack" -> quantity * per
                per = None
                try:
                    per = float(subnum.group(1).replace(",", ""))
                except Exception:
                    per = None
                if per is not None:
                    unit = normalize_unit_name(parts[1])
                    return quantity * per, unit
                except Exception:
                    # If parsing fails, fall back to the generic unit handling below
                    pass
    unit = normalize_unit_name(rest)
    return quantity, unit

def normalize_unit_quantity(quantity, unit):
    try:
        qty = float(quantity)
    except Exception:
        qty = 1.0
    unit = normalize_unit_name(unit)
    return qty, unit
