"""Helper to create schema and optionally bulk-load CSVs into Postgres.
This is a stub: adjust schema SQL path and connection details in src/config.py
"""
import argparse
from pathlib import Path
import psycopg2
from src.config import get_db_dsn

def apply_schema(sql_path):
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
