from pathlib import Path
from dotenv import load_dotenv
import os

ENV_PATH = Path('.') / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # fallback to environment

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'northwind_db')
DB_USER = os.getenv('DB_USER', 'northwind_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'northwind123')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)

def get_db_dsn():
    """
    Construct and return a PostgreSQL DSN string for psycopg2.

    Returns:
        str: DSN string with host, port, dbname, user, and password.
    """
    return f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
