from tests.mocks.mock_gemini_client import MockGeminiClient
from src.text2sql_engine import generate_sql_query

def test_generate_sql_query_with_mock_client(monkeypatch):
    # Create a mock client with custom SQL response
    mock_client = MockGeminiClient("SELECT name FROM cities;")
    
    # Patch the client in your module
    monkeypatch.setattr("src.text2sql_engine.client", mock_client)

    # Call your function
    result = generate_sql_query("Get all city names")

    # Assertions
    assert result == "SELECT name FROM cities;"
    mock_client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents="Get all city names"
    )

def test_generate_sql_query_with_exception(monkeypatch):
    mock_client = MockGeminiClient()
    mock_client.set_exception(Exception("API failure"))

    monkeypatch.setattr("src.text2sql_engine.client", mock_client)

    result = generate_sql_query("Get all city names")
    assert result == ""  # function should return empty string on API error
