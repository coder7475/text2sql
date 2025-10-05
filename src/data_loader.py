"""Basic data loader utilities for Northwind dataset.
- load_excel_sheets: read all sheets into pandas DataFrames
- clean_columns: normalize column names
- save_csvs: persist cleaned tables to data/normalized/
"""
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_excel_sheets(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    dfs = pd.read_excel(path, sheet_name=None)
    logger.info(f"Loaded {len(dfs)} sheets from {path}")
    return dfs

def clean_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    return df

def save_csvs(dfs, out_dir='data/normalized'):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in dfs.items():
        clean = clean_columns(df)
        fname = out / f"{name}.csv"
        clean.to_csv(fname, index=False)
    logger.info(f"Saved {len(dfs)} tables to {out}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='Path to northwind.xlsx (data/raw)')
    args = parser.parse_args()
    dfs = load_excel_sheets(args.excel)
    save_csvs(dfs)
