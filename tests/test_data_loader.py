import os
from pathlib import Path
import psycopg2
import pandas as pd
import pytest
from src.data_loader import clean_columns, load_excel_sheets
from tests.conftest import db_dsn

@pytest.fixture(scope="session")
def db_connection():
    """Create a temporary PostgreSQL connection."""
    dsn = db_dsn()
    conn = psycopg2.connect(dsn)
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def test_excel_path():
    return Path("data/raw/northwind.xlsx")

def test_load_excel_sheets(test_excel_path):
    """Check that Excel sheets can be loaded as DataFrames."""
    dfs = load_excel_sheets(test_excel_path)

    assert isinstance(dfs, dict), "Expected a dictionary of DataFrames"
    assert len(dfs) > 0, "No sheets found in Excel file"

    for sheet_name, df in dfs.items():
        assert isinstance(df, pd.DataFrame), f"Sheet {sheet_name} is not a DataFrame"


def test_csv_files_exist():
    """Ensure normalized CSVs exist before loading."""
    csv_dir = Path("data/normalized")
    assert csv_dir.exists(), "CSV directory does not exist"
    
    csv_files = list(csv_dir.glob("*.csv"))
    assert len(csv_files) > 0, "No CSV files found"
    
    print(f"Found {len(csv_files)} CSV files.")

def test_clean_columns():
    """Check that column names are converted to snake_case."""
    df = pd.DataFrame({"First Name": [1], "lastName": [2], "AGE": [3]})
    clean_df = clean_columns(df)
    expected_cols = ["first_name", "last_name", "age"]
    assert list(clean_df.columns) == expected_cols
