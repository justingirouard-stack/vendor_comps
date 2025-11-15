#!/usr/bin/env python3
"""
Main extraction & normalization pipeline.
Usage:
  python scripts/extract_normalize.py --input-dir tests/fixtures --output-dir output --master-products master_products.csv
"""

import argparse
import os
import sys
import importlib
import glob
import logging
from pathlib import Path
import pandas as pd
from scripts.normalize_units import normalize_unit_quantity, parse_quantity_unit
from scripts.xlsx_writer import write_comparison_excel
from rapidfuzz import process, fuzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# plugin namespace: parsers.* modules must implement parse_invoice(path) -> list[dict]
# item dict: { "raw_description","quantity","unit","unit_cost","currency", "vendor", ... }

PARSERS_MODULE = "parsers"

def discover_parsers():
    parsers = {}
    pars_path = Path("parsers")
    if not pars_path.exists():
        return pars
    for py in pars_path.glob("*.py"):
        if py.name == "__init__.py":
            continue
        name = py.stem
        try:
            mod = importlib.import_module(f"parsers.{name}")
            if hasattr(mod, "parse_invoice"):
                parsers[name] = mod.parse_invoice
                logger.info("Loaded parser: %s", name)
        except Exception as e:
            logger.warning("Failed to load parser %s: %s", name, e)
    return parsers

def generic_parse(path):
    """
    Fallback generic parser: attempt table extraction (pdf/xlsx/csv). Returns list of items.
    This is intentionally simple; extend with layout-parser or ML based extraction.
    """
    logger.info("Generic parsing for %s", path)
    items = []
    p = Path(path)
    suffix = p.suffix.lower()
    try:
        if suffix in [".csv"]:
            df = pd.read_csv(path)
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        elif suffix in [".pdf"]:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                tables = []
                for page in pdf.pages:
                    tbl = page.extract_table()
                    if tbl:
                        tables.append(pd.DataFrame(tbl[1:], columns=tbl[0]))
                if tables:
                    df = pd.concat(tables, ignore_index=True)
                else:
                    df = pd.DataFrame()
        else:
            df = pd.DataFrame()
    except Exception as e:
        logger.warning("Generic parser failed for %s: %s", path, e)
        df = pd.DataFrame()

    if df.empty:
        return items

    # Heuristic: find columns that look like description, qty, unit price
    cols = {c.lower(): c for c in df.columns}
    def find_candidate(*keys):
        for k in keys:
            for col in cols:
                if k in col:
                    return cols[col]
        return None

    desc_col = find_candidate("description", "item", "product", "detail")
    qty_col = find_candidate("qty", "quantity", "amount")
    price_col = find_candidate("price", "unit price", "unitprice", "cost")
    total_col = find_candidate("total", "ext", "extended")

    for _, row in df.iterrows():
        desc = row.get(desc_col, "") if desc_col else ""
        qty_raw = row.get(qty_col, 1) if qty_col else 1
        price_raw = row.get(price_col, None) if price_col else None
        total_raw = row.get(total_col, None) if total_col else None

        # parse qty into quantity + unit if possible
        quantity, unit = parse_quantity_unit(str(qty_raw))
        if price_raw is None and total_raw is not None and quantity:
            try:
                price_raw = float(total_raw) / float(quantity)
            except Exception:
                price_raw = None

        item = {
            "raw_description": str(desc).strip(),
            "quantity": float(quantity) if quantity else 1.0,
            "unit": unit or "ea",
            "unit_cost": float(price_raw) if price_raw not in (None, "", "nan") else None,
            "currency": "USD",
            "vendor": None,
        }
        items.append(item)
    return items

def load_master_products(path):
    if not path or not os.path.exists(path):
        return []
    df = pd.read_csv(path)
    if "product_name" in df.columns:
        return df["product_name"].astype(str).tolist()
    return df.iloc[:,0].astype(str).tolist()

def match_product_name(name, master_list, threshold=80):
    if not master_list:
        return name, 100
    match, score, _ = process.extractOne(name, master_list, scorer=fuzz.WRatio, score_cutoff=threshold) or (None, 0, None)
    return (match or name), score

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--master-products", required=False, default="")
    args = ap.parse_args()

    parsers = discover_parsers()
    master_products = load_master_products(args.master_products)
    all_items = []

    for file_path in sorted(Path(args.input_dir).glob("*")):
        if file_path.is_dir():
            continue
        logger.info("Processing %s", file_path)
        vendor = None
        parsed = []
        # vendor-specific parser pick by filename convention: vendorname_*.pdf
        for name, fn in parsers.items():
            try:
                items = fn(str(file_path))
                if items:
                    vendor = name
                    parsed = items
                    break
            except Exception as e:
                logger.debug("Parser %s failed: %s", name, e)
        if not parsed:
            parsed = generic_parse(str(file_path))

        for item in parsed:
            item.setdefault("vendor", vendor or file_path.stem.split("_")[0])
            # normalize unit/quantity
            qty, unit = normalize_unit_quantity(item.get("quantity"), item.get("unit"))
            item["quantity_normalized"] = qty
            item["unit_normalized"] = unit
            # compute unit_cost if necessary
            if item.get("unit_cost") is None and item.get("total_cost"):
                try:
                    item["unit_cost"] = float(item["total_cost"]) / float(qty)
                except Exception:
                    item["unit_cost"] = None
            # product matching
            matched_name, score = match_product_name(item.get("raw_description",""), master_products)
            item["matched_product"] = matched_name
            item["match_score"] = score
            all_items.append(item)

    if not all_items:
        logger.error("No items extracted. Exiting with code 2.")
        sys.exit(2)

    df = pd.DataFrame(all_items)
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = Path(args.output_dir) / "vendor_price_comparison.xlsx"
    write_comparison_excel(df, out_path)
    logger.info("Wrote %s", out_path)

if __name__ == "__main__":
    main()
