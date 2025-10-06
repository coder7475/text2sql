import pytest
from src.query_validator import QueryValidator

def test_valid_select_adds_limit():
    """
    Test that a simple SELECT query without a LIMIT clause
    is automatically appended with 'LIMIT 1000' by the validator.
    """
    query = "SELECT * FROM cities"
    result = QueryValidator.validate(query)
    assert "LIMIT 1000" in result

def test_select_with_existing_limit_unchanged():
    """
    Test that a SELECT query which already contains a LIMIT clause
    is not modified by the validator to add another LIMIT.
    """
    query = "SELECT * FROM cities LIMIT 5"
    result = QueryValidator.validate(query)
    assert "LIMIT 5" in result
    assert "LIMIT 1000" not in result

@pytest.mark.parametrize("dangerous_kw", [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"
])
def test_rejects_dangerous_keywords(dangerous_kw):
    """
    Verify that a query starting with a dangerous SQL keyword is rejected by the validator.
    
    Raises ValueError with message "Only SELECT statements are allowed." for queries constructed with dangerous SQL keywords such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, and REVOKE.
    
    Parameters:
        dangerous_kw (str): Dangerous SQL keyword used to build the test query.
    """
    query = f"{dangerous_kw} cities SET name='X';"
    with pytest.raises(ValueError, match="Only SELECT statements are allowed."):
        QueryValidator.validate(query)

def test_non_select_statement_rejected():
    """
    Test that non-SELECT SQL statements are rejected by the validator.

    The validator should raise a ValueError if the query is not a SELECT statement.
    """
    with pytest.raises(ValueError, match="Only SELECT"):
        QueryValidator.validate("Only SELECT statements are allowed.")