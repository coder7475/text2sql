import re
import os
import sys
from dotenv import load_dotenv
from google import genai
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.query_validator import QueryValidator
from src.utils import df_to_json, execute_query_on_db

load_dotenv()

client = genai.Client()


def generate_sql_query(prompt: str) -> str:
    """Generate SQL query from an English prompt using the Gemini API."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return ""


def sanitize_sql(sql: str) -> str:
    """Sanitize the generated SQL query."""
    # Remove non-ASCII characters
    sql = re.sub(r'[^\x00-\x7F]+', '', sql)
    # Strip leading/trailing whitespace
    sql = sql.strip()
    # extract the text from ```sql ...``` block if present
    match = re.search(r"```sql\s*(.*?)\s*```", sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1)

    return sql


if __name__ == "__main__":
    user_question = "Find all unique city names";
    prompt = prompt = f"""
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


    sql_query = generate_sql_query(prompt)

    sanitized_query = sanitize_sql(sql_query)

    if not sanitized_query:
        print("Generated SQL query is empty after sanitization")
        sys.exit(1)
    
    try:
        validated_query = QueryValidator.validate(sanitized_query)
        print("Generated SQL Query:", validated_query)
    except ValueError as e:
        print("Validation error:", e)
        sys.exit(1)

    df = execute_query_on_db(validated_query)

    if df.empty:
        print("\nNo results found or query failed.")
    else:
        print(f"\nQuery: {user_question}")
        print("\nQuery Results (JSON):")
        print(df_to_json(df))