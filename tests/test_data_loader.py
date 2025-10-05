from src.data_loader import clean_columns
import pandas as pd

def test_clean_columns():
    df = pd.DataFrame({'First Name': ['Alice'], 'Age ': [30]})
    cleaned = clean_columns(df)
    assert 'first_name' in cleaned.columns
    assert 'age' in cleaned.columns
