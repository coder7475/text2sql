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
    """
    Load all sheets from an Excel file into a dictionary of pandas DataFrames.

    Args:
        path (str or Path): Path to the Excel file.

    Returns:
        dict: Dictionary where keys are sheet names and values are DataFrames.

    Raises:
        FileNotFoundError: If the specified Excel file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    dfs = pd.read_excel(path, sheet_name=None)
    logger.info(f"Loaded {len(dfs)} sheets from {path}")
    return dfs

def clean_columns(df):
    """
    Normalize DataFrame column names by stripping whitespace, converting to lowercase,
    and replacing spaces with underscores.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned column names.
    """
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in a DataFrame.

    Numeric columns: fill NaN with 0.
    Non-numeric columns: fill NaN with empty string.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna('')
    return df

def save_csvs(dfs, out_dir='data/normalized'):
    """
    Save a dictionary of DataFrames to CSV files in the specified output directory.
    Column names are cleaned before saving.

    Args:
        dfs (dict): Dictionary of DataFrames to save.
        out_dir (str or Path): Output directory for CSV files (default: 'data/normalized').
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in dfs.items():
        clean = clean_columns(df)
        fname = out / f"{name}.csv"
        clean.to_csv(fname, index=False)
    logger.info(f"Saved {len(dfs)} tables to {out}")

if __name__ == '__main__':
    """
    Command-line interface for loading an Excel file and saving its sheets as CSVs.

    Usage:
        python src/data_loader.py --excel path/to/northwind.xlsx
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='Path to northwind.xlsx (data/raw)')
    args = parser.parse_args()
    dfs = load_excel_sheets(args.excel)
    save_csvs(dfs)
