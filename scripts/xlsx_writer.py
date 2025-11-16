import pandas as pd
from pathlib import Path
from typing import Union

def write_comparison_excel(df: pd.DataFrame, out_path: Union[str, Path]) -> None:
    """
    Write the vendor price comparison DataFrame to an XLSX workbook.
    This function does not import scripts.* so it won't cause circular imports.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Basic safe write using pandas ExcelWriter; adjust formatting as needed.
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        # Main sheet
        df.to_excel(writer, sheet_name="comparison", index=False)

        # Optionally add a summary sheet
        try:
            summary = df.groupby("vendor")["unit_cost"].agg(["count", "median", "mean", "min", "max"]).reset_index()
            summary.to_excel(writer, sheet_name="summary", index=False)
        except Exception:
            # If grouping fails (missing columns), skip summary gracefully
            pass
