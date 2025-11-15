"""
Template vendor parser.

Implement parse_invoice(path: str) -> list[dict]
Return item dicts with keys:
  - raw_description (str)
  - quantity (float or str)
  - unit (str)
  - unit_cost (float)  # optional
  - total_cost (float) # optional
  - currency (str)
  - vendor (str)
"""
from pathlib import Path
import pandas as pd

def parse_invoice(path: str):
    p = Path(path)
    if "examplevendor" not in p.name.lower():
        return []
    items = []
    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p)
    elif p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        return []
    for _, r in df.iterrows():
        try:
            desc = r.get("Item", r.get("Description", ""))
            qty = r.get("Qty", 1)
            price = r.get("Unit Price", None)
            items.append({
                "raw_description": str(desc).strip(),
                "quantity": float(qty) if qty not in (None, "") else 1.0,
                "unit": "ea",
                "unit_cost": float(price) if price not in (None, "") else None,
                "currency": "USD",
                "vendor": "examplevendor"
            })
        except Exception:
            continue
    return items
