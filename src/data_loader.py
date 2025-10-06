"""
Northwind Data Loader Utilities

This module provides utilities and a command-line interface for processing the Northwind dataset,
including:

- Loading all sheets from an Excel file into pandas DataFrames.
- Normalizing DataFrame column names to snake_case.
- Handling missing values in DataFrames based on column type.
- Saving cleaned DataFrames as CSV files in a normalized directory.
- Loading normalized CSVs into a PostgreSQL database, including normalization of city/region/country
  hierarchies and referential integrity for location tables.
- Command-line interface for converting Excel to CSV and loading all normalized data
  into the database in the correct order.

**Main Functions:**
- `load_excel_sheets(path)`: Read all sheets from an Excel file.
- `clean_columns(df)`: Normalize DataFrame column names.
- `handle_missing_values(df)`: Fill missing values appropriately.
- `save_csvs(dfs, out_dir)`: Save cleaned DataFrames to CSV.
- `load_orders(csv_path)`: Load orders with location hierarchy into the database.
- `load_generic_csv(...)`: Generic loader for other tables with optional location mapping.

**Helper Functions:**
- `get_or_create_country`, `get_or_create_region`, `get_or_create_city`: Ensure location
  hierarchy exists in the database.

**Command-Line Usage:**
    python src/data_loader.py --excel path/to/northwind.xlsx

**Requirements:**
- pandas
- psycopg2
- src.config.get_db_dsn
"""

import sys
import os
from pathlib import Path
import pandas as pd
import logging
import psycopg2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import get_or_create_city, get_or_create_country, get_or_create_region, to_snake_case
from src.config import get_db_dsn


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_excel_sheets(path):
    """
    Read every sheet from an Excel workbook and return them keyed by sheet name.

    Args:
        path (str or Path): Path to the Excel file to read.

    Returns:
        dict: Mapping of sheet name to pandas DataFrame for each sheet in the workbook.

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
    Normalize DataFrame column names to snake_case.

    Returns a copy of the input DataFrame with all column names converted to snake_case
    (whitespace trimmed, camelCase/PascalCase converted, spaces replaced with underscores, and lowercased).

    Args:
        df (pd.DataFrame): DataFrame whose column names will be normalized.

    Returns:
        pd.DataFrame: A copy of `df` with cleaned column names.
    """
    df = df.copy()
    df.columns = [to_snake_case(c) for c in df.columns]
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame according to column types.

    - Numeric columns: filled with 0
    - Boolean columns: filled with False
    - Datetime columns: filled with pd.Timestamp('1970-01-01')
    - All other columns: filled with an empty string

    Args:
        df (pd.DataFrame): Input DataFrame to process.

    Returns:
        pd.DataFrame: A copy of the DataFrame with missing values filled as described.
    """
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].fillna(False)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].fillna(pd.Timestamp('1970-01-01'))
        else:
            df[col] = df[col].fillna('')
    return df

def save_csvs(dfs, out_dir='data/normalized'):
    """
    Write cleaned DataFrames from a mapping to CSV files in the given output directory.

    Each DataFrame has its column names normalized and missing values filled before being written.

    Args:
        dfs (dict): Mapping of base file name (string) to pandas.DataFrame to save.
        out_dir (str or Path): Directory where CSV files will be created (directory is created if missing).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in dfs.items():
        clean = clean_columns(df)
        finished = handle_missing_values(clean)
        fname = out / f"{name}.csv"
        finished.to_csv(fname, index=False)
    logger.info(f"Saved {len(dfs)} tables to {out}")



def load_orders(csv_path):
    """
    Load orders from a CSV file into the database, ensuring location hierarchy exists.

    Args:
        csv_path (str): Path to the Order.csv file.

    Returns:
        None
    """
    df = pd.read_csv(csv_path)
    df = handle_missing_values(df)
    dsn = get_db_dsn()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                # Step 1: Ensure location hierarchy exists

                country_id = get_or_create_country(cur, row["ship_country"])
                region_id = get_or_create_region(cur, row["ship_region"], country_id)
                city_id = get_or_create_city(cur, row["ship_city"], region_id)

                # Step 2: Insert into "orders"
                # Convert pandas/numpy types to native Python types
                def convert_value(val):
                    """
                    Convert pandas/NumPy scalar and missing values to native Python equivalents.

                    Args:
                        val: The input value (possibly a pandas/NumPy scalar or missing value) to normalize.

                    Returns:
                        The normalized value: `None` if `val` is missing, a native Python scalar if `val` is a NumPy scalar, or `val` unchanged otherwise.
                    """
                    if pd.isna(val):
                        return None
                    elif hasattr(val, 'item'):  # NumPy scalar
                        return val.item()
                    return val
                    
                cur.execute("""
                    INSERT INTO orders (
                        order_id,
                        customer_id,
                        employee_id,
                        order_date,
                        required_date,
                        shipped_date,
                        ship_via,
                        freight,
                        ship_name,
                        ship_city_id,
                        ship_postal_code
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    convert_value(row["order_id"]),
                    convert_value(row["customer_id"]),
                    convert_value(row["employee_id"]),
                    convert_value(row["order_date"]),
                    convert_value(row["required_date"]),
                    convert_value(row["shipped_date"]),
                    convert_value(row["ship_via"]),
                    convert_value(row["freight"]),
                    convert_value(row["ship_name"]),
                    city_id,
                    convert_value(row["ship_postal_code"])
                ))
        conn.commit()
    print("Orders successfully loaded.")



def load_generic_csv(csv_path, table_name, city_col="city", region_col="region", country_col="country", id_col=None):
    """
    Load rows from a CSV file into a database table, optionally resolving and inserting city/region/country hierarchy.

    Reads the CSV at `csv_path`, fills missing values, connects to the northwind schema, and inserts each row into `table_name`.
    If the CSV contains city/region/country columns (names provided by `city_col`, `region_col`, `country_col`), the function
    ensures corresponding country, region, and city records exist and adds the resulting city_id to inserts.
    If `id_col` is provided, conflicts on that column are ignored (`ON CONFLICT (...) DO NOTHING`).

    Args:
        csv_path (str): Path to the input CSV file.
        table_name (str): Target table name to insert rows into.
        city_col (str): Column name in the CSV containing city names (default "city").
        region_col (str): Column name in the CSV containing region names (default "region").
        country_col (str): Column name in the CSV containing country names (default "country").
        id_col (str or None): Column to use for conflict resolution; when provided, uses `ON CONFLICT (id_col) DO NOTHING`.
    """
    df = pd.read_csv(csv_path)  
    df = handle_missing_values(df)
    dsn = get_db_dsn()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                # Step 1: Resolve city hierarchy if columns exist
                city_id = None
                if city_col in df.columns and country_col in df.columns:
                    country_id = get_or_create_country(cur, row[country_col])
                    region_id = get_or_create_region(cur, row.get(region_col, ''), country_id)
                    city_id = get_or_create_city(cur, row[city_col], region_id)

                # Step 2: Prepare columns and values
                columns = []
                values = []
                for col in df.columns:
                    if col in [city_col, region_col, country_col]:
                        continue  # Already handled
                    columns.append(col)
                    # Convert pandas/numpy types to native Python types
                    value = row[col]
                    if pd.isna(value):
                        value = None
                    elif hasattr(value, 'item'):  # NumPy scalar
                        value = value.item()
                    values.append(value)
                
                # Include city_id if present
                if city_id is not None:
                    columns.append("city_id")
                    values.append(city_id)

                # Step 3: Build INSERT query
                cols_str = ",".join(columns)
                placeholders = ",".join(["%s"] * len(values))

                query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
                if id_col:
                    query += f" ON CONFLICT ({id_col}) DO NOTHING"

                cur.execute(query, values)
        conn.commit()

    print(f"Data from {csv_path} successfully loaded into {table_name}.")


if __name__ == '__main__':
    """
    Command-line interface for loading an Excel file and saving its sheets as CSVs,
    then loading all normalized CSVs into the database in the correct order.

    Usage:
        python src/data_loader.py --excel path/to/northwind.xlsx
    """
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='Path to northwind.xlsx (data/raw)')
    args = parser.parse_args()

    # Load Excel sheets and save as CSVs
    dfs = load_excel_sheets(args.excel)
    save_csvs(dfs)

    # List of configs for tables except Order and Order Detail
    csv_configs = [
        {
            "csv_path": "data/normalized/Category.csv",
            "table_name": "categories",
            "id_col": "category_id"
        },
        {
            "csv_path": "data/normalized/Customer.csv",
            "table_name": "customers",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "customer_id"
        },
        {
            "csv_path": "data/normalized/Employee.csv",
            "table_name": "employees",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "employee_id"
        },
        {   
            "csv_path": "data/normalized/Supplier.csv",
            "table_name": "suppliers",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "supplier_id"
        },
        {
            "csv_path": "data/normalized/Product.csv",
            "table_name": "products",
            "id_col": "product_id"
        },
        {
            "csv_path": "data/normalized/Shipper.csv",
            "table_name": "shippers",
            "id_col": "shipper_id"
        },
    ]

    # Make sure all required CSV files exist before loading
    missing_files = [cfg["csv_path"] for cfg in csv_configs if not os.path.isfile(cfg["csv_path"])]
    if missing_files:
        raise FileNotFoundError(f"Missing required CSV files: {missing_files}")

    for config in csv_configs:
        load_generic_csv(**config)

    # Make sure Order.csv exists before loading orders
    order_csv_path = "data/normalized/Order.csv"
    if not os.path.isfile(order_csv_path):
        raise FileNotFoundError(f"Missing required CSV file: {order_csv_path}")

    # Load orders before order details to ensure referential integrity
    load_orders(order_csv_path)

    # Make sure Order Detail.csv exists before loading order details
    order_detail_csv_path = "data/normalized/Order Detail.csv"
    if not os.path.isfile(order_detail_csv_path):
        raise FileNotFoundError(f"Missing required CSV file: {order_detail_csv_path}")

    order_detail_config = {
        "csv_path": order_detail_csv_path,
        "table_name": "order_details",
    }
    load_generic_csv(**order_detail_config)