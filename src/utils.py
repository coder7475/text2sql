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
    - Remove Spaces
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

def build_prompt(user_question: str) -> str:
    return f"""
        You are a helpful assistant specializing in data analysis in a PostgreSQL warehouse.
        Answer the questions by providing SQL code that is compatible with the PostgreSQL environment.
        This is the question you are required to answer:
        {user_question}

        Here is the relevant context of the database:
        -- Countries
        CREATE TABLE countries (
            country_id SERIAL PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL UNIQUE
        );

        -- Regions
        CREATE TABLE regions (
            region_id SERIAL PRIMARY KEY,
            region_name VARCHAR(100) NOT NULL,
            country_id INT NOT NULL REFERENCES countries(country_id)
        );

        -- Cities
        CREATE TABLE cities (
            city_id SERIAL PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL,
            region_id INT NOT NULL REFERENCES regions(region_id)
        );

        -- Customers
        CREATE TABLE customers (
            customer_id VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            contact_name VARCHAR(100),
            contact_title VARCHAR(50),
            address TEXT,
            city_id INT REFERENCES cities(city_id),
            postal_code VARCHAR(20),
            phone VARCHAR(30),
            fax VARCHAR(30)
        );

        -- Employees
        CREATE TABLE employees (
            employee_id SERIAL PRIMARY KEY,
            last_name VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            title VARCHAR(50),
            title_of_courtesy VARCHAR(25),
            birth_date DATE,
            hire_date DATE,
            city_id INT REFERENCES cities(city_id)
        );

        -- Suppliers
        CREATE TABLE suppliers (
            supplier_id SERIAL PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            city_id INT REFERENCES cities(city_id)
        );

        -- Categories
        CREATE TABLE categories (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL UNIQUE
        );

        -- Products
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            supplier_id INT REFERENCES suppliers(supplier_id),
            category_id INT REFERENCES categories(category_id)
        );

        -- Shippers
        CREATE TABLE shippers (
            shipper_id SERIAL PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL
        );

        -- Orders
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id),
            employee_id INT REFERENCES employees(employee_id),
            order_date DATE,
            ship_via INT REFERENCES shippers(shipper_id)
        );

        -- Order Details
        CREATE TABLE order_details (
            order_id INT NOT NULL REFERENCES orders(order_id),
            product_id INT NOT NULL REFERENCES products(product_id),
            unit_price NUMERIC(10,2) NOT NULL,
            quantity SMALLINT NOT NULL,
            discount REAL DEFAULT 0,
            PRIMARY KEY (order_id, product_id)
        );
        """