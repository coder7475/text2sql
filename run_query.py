"""Minimal CLI to run a natural language query through the Text2SQL prototype.
Currently uses a mocked LLM function for safety/demos.
"""
import sys
from src.text2sql_engine import mock_gemini_to_sql
from src.query_validator import validate_query
from src.config import get_db_dsn
import pandas as pd
import psycopg2

def execute_sql(sql):
    dsn = get_db_dsn()
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

def main():
    if len(sys.argv) < 2:
        print('Usage: python run_query.py "natural language question"')
        sys.exit(1)
    question = sys.argv[1]
    sql = mock_gemini_to_sql(question)
    print('=== Generated SQL (mock) ===')
    print(sql)
    valid = validate_query(sql)
    if not valid['ok']:
        print('Query validation failed:', valid['reason'])
        sys.exit(2)
    print('Executing query...')
    df = execute_sql(valid['sql'])
    print(df.head().to_json(orient='records'))

if __name__ == '__main__':
    main()
