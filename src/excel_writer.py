# ---------------------------------------------
# Step 6.1 - Excel Writer Utility
# ---------------------------------------------

# This module provides functionality to write multiple tables
# pandas DataFrames to an Excel file, each in its own sheet.

import pandas as pd
from pathlib import Path

def write_tables_to_excel(tables, output_path):
    """
    tables: list of dicts
        [
          {
            "page": int,
            "table": int,
            "dataframe": pd.DataFrame
          }
        ]
    output_path: str
    """

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for item in tables:
            page = item["page"]
            table = item["table"]
            df = item["dataframe"]

            sheet_name = f"Page_{page}_Table_{table}"
            sheet_name = sheet_name[:31]  # Excel limit

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                header=False
            )
