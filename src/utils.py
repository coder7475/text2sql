# # =========================================================
# # Helper Functions
# # =========================================================
import os
import sys
import psycopg2
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_dsn


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
    # Remove spaces
    s = s.replace(' ', '')
    # Convert camelCase or PascalCase to snake_case
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)

    return s.lower()

def get_or_create_country(cur, country_name):
    """
    Get the country_id for a given country_name, or create it if it does not exist.

    Args:
        cur: psycopg2 cursor.
        country_name (str): Name of the country.

    Returns:
        int: country_id
    """
    cur.execute("SELECT country_id FROM countries WHERE country_name = %s", (country_name,))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO countries (country_name) VALUES (%s)
        RETURNING country_id
    """, (country_name,))
    return cur.fetchone()[0]


def get_or_create_region(cur, region_name, country_id):
    """
    Retrieve the ID for a region with the given name and country, inserting a new region if none exists.
    
    Parameters:
        cur: Database cursor used to execute queries.
        region_name (str): Name of the region; empty or falsy values are treated as "Unknown".
        country_id (int): Primary key of the country to which the region belongs.
    
    Returns:
        region_id (int): The existing or newly created region's ID.
    """
    if not region_name:
        region_name = "Unknown"

    cur.execute("""
        SELECT region_id FROM regions
        WHERE region_name = %s AND country_id = %s
    """, (region_name, country_id))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO regions (region_name, country_id)
        VALUES (%s, %s)
        RETURNING region_id
    """, (region_name, country_id))
    return cur.fetchone()[0]


def get_or_create_city(cur, city_name, region_id):
    """
    Get the city_id for a given city_name and region_id, or create it if it does not exist.

    Args:
        cur: psycopg2 cursor.
        city_name (str): Name of the city.
        region_id (int): ID of the region.

    Returns:
        int: city_id
    """
    cur.execute("""
        SELECT city_id FROM cities WHERE city_name = %s AND region_id = %s
    """, (city_name, region_id))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO cities (city_name, region_id)
        VALUES (%s, %s)
        RETURNING city_id
    """, (city_name, region_id))
    return cur.fetchone()[0]


def execute_query_on_db(query: str) -> pd.DataFrame:
    """
    Execute validated SQL query on the PostgreSQL Northwind database.
    Returns results as a pandas DataFrame.
    """
    dsn = get_db_dsn()
    try:
        with psycopg2.connect(dsn) as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Database execution error: {e}")
        return pd.DataFrame()


def df_to_json(df: pd.DataFrame) -> str:
    """Convert pandas DataFrame to JSON (records format)."""
    return df.to_json(orient="records", indent=2)

