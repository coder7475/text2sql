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
    Apply the database schema from the given SQL file.

    Args:
        sql_path (str or Path): Path to the SQL schema file.

    This function connects to the database using the DSN from config,
    reads the SQL schema file, and executes it to create/update the schema.
    """
    dsn = get_db_dsn()
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            sql = Path(sql_path).read_text()
            cur.execute(sql)
            conn.commit()
    print('Schema applied.')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--schema', default='data/schema/schema.sql', help='Path to schema SQL')
    args = p.parse_args()
    apply_schema(args.schema)
