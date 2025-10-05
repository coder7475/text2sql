"""Simple validator to ensure only safe SELECT queries are executed.
Returns dict: {'ok': True, 'sql': safe_sql} or {'ok': False, 'reason': '...'}
"""
import sqlparse
import re

DANGEROUS = re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke)\b", re.I)

def validate_query(sql: str):
    # Quick blacklist
    if DANGEROUS.search(sql):
        return {'ok': False, 'reason': 'DML/DDL commands are not allowed.'}
    parsed = sqlparse.parse(sql)
    if not parsed:
        return {'ok': False, 'reason': 'Unable to parse SQL.'}
    stmt = parsed[0]
    if stmt.get_type() != 'SELECT':
        return {'ok': False, 'reason': 'Only SELECT statements are allowed.'}
    # Enforce row limit by wrapping (if LIMIT not present)
    if 'limit' not in sql.lower():
        safe_sql = f"SELECT * FROM ({sql.rstrip(';')}) AS subq LIMIT 1000;"
    else:
        safe_sql = sql
    # Block access to system schemas
    if re.search(r"\b(pg_catalog|information_schema)\b", safe_sql, re.I):
        return {'ok': False, 'reason': 'Access to system tables is blocked.'}
    return {'ok': True, 'sql': safe_sql}
