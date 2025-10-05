from src.query_validator import validate_query

def test_block_insert():
    r = validate_query('INSERT INTO users (id) VALUES (1);')
    assert not r['ok']

def test_allow_select_and_wrap():
    r = validate_query('SELECT * FROM customers;')
    assert r['ok']
    assert 'LIMIT' in r['sql'].upper()
