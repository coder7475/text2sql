"""Helper to create schema and optionally bulk-load CSVs into Postgres.
This is a stub: adjust schema SQL path and connection details in src/config.py
"""
import argparse
from pathlib import Path
import psycopg2
import sys
import os


# Add the parent directory to Python path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_dsn

def apply_schema(sql_path):
    """
    Apply the database schema defined in an SQL file to the configured PostgreSQL database.
    
    Reads SQL from `sql_path` and executes it against the database using the DSN obtained from configuration. Prints "Schema applied." on success.
    
    Parameters:
        sql_path (str | pathlib.Path): Path to the SQL schema file to execute.
    """
    dsn = get_db_dsn()
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            sql = Path(sql_path).read_text()
            cur.execute(sql)
            conn.commit()
    print('Schema applied.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--schema', default='data/schema/schema.sql', help='Path to schema SQL')
    # parser.add_argument('--csv_dir', default='data/normalized', help='Directory of normalized CSVs')
    
    args = parser.parse_args()
    apply_schema(args.schema)
    # load_data_to_db(args.csv_dir)