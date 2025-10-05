"""Basic data loader utilities for Northwind dataset.
- load_excel_sheets: read all sheets into pandas DataFrames
- clean_columns: normalize column names
- save_csvs: persist cleaned tables to data/normalized/
"""
import sys
import os
from pathlib import Path
import pandas as pd
import logging
import psycopg2
# from psycopg2.extras import execute_values

# Add the parent directory to Python path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.config import get_db_dsn

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

def to_snake_case(s):
    """
    Convert a string to snake_case.

    This function normalizes a string by:
    - Stripping leading/trailing whitespace
    - Replacing spaces with underscores
    - Converting camelCase or PascalCase to snake_case
    - Lowercasing all characters

    Args:
        s (str): The input string.

    Returns:
        str: The snake_case version of the input string.
    """
    import re
    s = str(s).strip()
    # Replace spaces with underscores
    s = s.replace(' ', '_')
    # Convert camelCase or PascalCase to snake_case
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower()
    
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
    df.columns = [to_snake_case(c) for c in df.columns]
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in a DataFrame.

    Numeric columns: fill NaN with 0.
    String/object columns: fill NaN with empty string.
    Datetime columns: fill NaN with pd.Timestamp('1970-01-01').
    Boolean columns: fill NaN with False.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
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
        finished = handle_missing_values(clean)
        fname = out / f"{name}.csv"
        finished.to_csv(fname, index=False)
    logger.info(f"Saved {len(dfs)} tables to {out}")


# # =========================================================
# # Helper Functions
# # =========================================================

def get_or_create_country(cur, country_name):
    cur.execute("SELECT country_id FROM country WHERE country_name = %s", (country_name,))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO country (country_name) VALUES (%s)
        RETURNING country_id
    """, (country_name,))
    return cur.fetchone()[0]


def get_or_create_region(cur, region_name, country_id):
    # Region may be NULL in the CSV (empty string)
    if not region_name:
        region_name = "Unknown"

    cur.execute("""
        SELECT region_id FROM region
        WHERE region_name = %s AND country_id = %s
    """, (region_name, country_id))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO region (region_name, country_id)
        VALUES (%s, %s)
        RETURNING region_id
    """, (region_name, country_id))
    return cur.fetchone()[0]


def get_or_create_city(cur, city_name, region_id):
    cur.execute("""
        SELECT city_id FROM city WHERE city_name = %s AND region_id = %s
    """, (city_name, region_id))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO city (city_name, region_id)
        VALUES (%s, %s)
        RETURNING city_id
    """, (city_name, region_id))
    return cur.fetchone()[0]



def load_orders(csv_path):
    df = pd.read_csv(csv_path)
    df = handle_missing_values(df)
    dsn = get_db_dsn()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Set search path to northwind schema
            cur.execute("SET search_path TO northwind;")
            for _, row in df.iterrows():
                # Step 1: Ensure location hierarchy exists

                country_id = get_or_create_country(cur, row["ship_country"])
                region_id = get_or_create_region(cur, row["ship_region"], country_id)
                city_id = get_or_create_city(cur, row["ship_city"], region_id)

                # Step 2: Insert into "order"
                # Convert pandas/numpy types to native Python types
                def convert_value(val):
                    if pd.isna(val):
                        return None
                    elif hasattr(val, 'item'):  # NumPy scalar
                        return val.item()
                    return val
                    
                cur.execute("""
                    INSERT INTO "order" (
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
    Generic loader for CSV files into tables with optional city/region/country mapping.
    
    Args:
        csv_path (str): Path to CSV file.
        table_name (str): Target table in DB.
        city_col (str): Column name for city in CSV.
        region_col (str): Column name for region in CSV.
        country_col (str): Column name for country in CSV.
        id_col (str): Column to use for ON CONFLICT handling (primary key).
    """
    df = pd.read_csv(csv_path)  
    df = handle_missing_values(df)
    dsn = get_db_dsn()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO northwind;")

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
    Command-line interface for loading an Excel file and saving its sheets as CSVs.

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
            "table_name": "category",
            "id_col": "category_id"
        },
        {
            "csv_path": "data/normalized/Customer.csv",
            "table_name": "customer",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "customer_id"
        },
        {
            "csv_path": "data/normalized/Employee.csv",
            "table_name": "employee",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "employee_id"
        },
        {   
            "csv_path": "data/normalized/Supplier.csv",
            "table_name": "supplier",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "supplier_id"
        },
        {
            "csv_path": "data/normalized/Product.csv",
            "table_name": "product",
            "city_col": "city",
            "region_col": "region",
            "country_col": "country",
            "id_col": "product_id"
        },
        {
            "csv_path": "data/normalized/Shipper.csv",
            "table_name": "shipper",
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
        "table_name": "order_detail",
    }
    load_generic_csv(**order_detail_config)
