from unittest.mock import Mock, MagicMock
import pandas as pd

from src.utils import get_or_create_country, get_or_create_region, get_or_create_city, execute_query_on_db

# ------------------------
# Tests for get_or_create_country
# ------------------------
def test_get_or_create_country_existing():
    mock_cur = Mock()
    mock_cur.fetchone.return_value = [1]  # existing country_id

    country_id = get_or_create_country(mock_cur, "USA")
    mock_cur.execute.assert_called_with(
        "SELECT country_id FROM countries WHERE country_name = %s", ("USA",)
    )
    assert country_id == 1


def test_get_or_create_country_new():
    mock_cur = Mock()
    # first fetch returns None -> country does not exist
    mock_cur.fetchone.side_effect = [None, [2]]  # new country_id returned after insert

    country_id = get_or_create_country(mock_cur, "Canada")
    # First SELECT
    mock_cur.execute.assert_any_call(
        "SELECT country_id FROM countries WHERE country_name = %s", ("Canada",)
    )
    # Then INSERT
    mock_cur.execute.assert_any_call(
        """
        INSERT INTO countries (country_name) VALUES (%s)
        RETURNING country_id
    """, ("Canada",)
    )
    assert country_id == 2

# ------------------------
# Tests for get_or_create_region
# ------------------------
def test_get_or_create_region_existing():
    mock_cur = Mock()
    mock_cur.fetchone.return_value = [10]

    region_id = get_or_create_region(mock_cur, "California", 1)
    mock_cur.execute.assert_called_with(
        """
        SELECT region_id FROM regions
        WHERE region_name = %s AND country_id = %s
    """, ("California", 1)
    )
    assert region_id == 10


def test_get_or_create_region_new_empty_name():
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [None, [11]]  # New region id returned after insert

    region_id = get_or_create_region(mock_cur, "", 1)
    # Should convert empty region_name to "Unknown"
    mock_cur.execute.assert_any_call(
        """
        INSERT INTO regions (region_name, country_id)
        VALUES (%s, %s)
        RETURNING region_id
    """, ("Unknown", 1)
    )
    assert region_id == 11

# ------------------------
# Tests for get_or_create_city
# ------------------------
def test_get_or_create_city_existing():
    mock_cur = Mock()
    mock_cur.fetchone.return_value = [100]

    city_id = get_or_create_city(mock_cur, "New York", 10)
    mock_cur.execute.assert_called_with(
        """
        SELECT city_id FROM cities WHERE city_name = %s AND region_id = %s
    """, ("New York", 10)
    )
    assert city_id == 100


def test_get_or_create_city_new():
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [None, [101]]

    city_id = get_or_create_city(mock_cur, "Los Angeles", 10)
    mock_cur.execute.assert_any_call(
        """
        INSERT INTO cities (city_name, region_id)
        VALUES (%s, %s)
        RETURNING city_id
    """, ("Los Angeles", 10)
    )
    assert city_id == 101

# ------------------------
# Tests for execute_query_on_db
# ------------------------
def test_execute_query_on_db_success(monkeypatch):
    mock_conn = MagicMock()
    mock_df = pd.DataFrame({"id": [1, 2]})

    # Patch psycopg2.connect and pd.read_sql_query
    monkeypatch.setattr("psycopg2.connect", lambda dsn: mock_conn)
    monkeypatch.setattr("pandas.read_sql_query", lambda query, conn: mock_df)

    df = execute_query_on_db("SELECT * FROM cities")
    assert isinstance(df, pd.DataFrame)
    assert df.equals(mock_df)


def test_execute_query_on_db_failure(monkeypatch):
    # Simulate exception in DB connection
    monkeypatch.setattr("psycopg2.connect", lambda dsn: (_ for _ in ()).throw(Exception("DB error")))

    df = execute_query_on_db("SELECT * FROM cities")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
