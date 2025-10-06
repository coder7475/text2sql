import pytest
from src.utils import to_snake_case, df_to_json
import pandas as pd

# ----------------------
# Test to_snake_case
# ----------------------
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("CamelCase", "camel_case"),
        ("PascalCase", "pascal_case"),
        ("  leadingSpace", "leading_space"),
        ("snake_case", "snake_case"),
        ("with space", "withspace"),
        ("mixedCASEString", "mixed_case_string")
    ]
)
def test_to_snake_case(input_str, expected):
    """
    Test the to_snake_case utility function.

    This test checks that various string formats (CamelCase, PascalCase, leading/trailing spaces,
    snake_case, strings with spaces, and mixed case) are correctly converted to snake_case.
    """
    assert to_snake_case(input_str) == expected


