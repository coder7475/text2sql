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
    Test that queries containing dangerous SQL keywords are rejected by the validator.

    The validator should raise a ValueError if the query contains any of the following keywords:
    UPDATE, DELETE, DROP, ALTER.
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
