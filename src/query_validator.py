import re

class QueryValidator:
    """Validator for SQL queries to ensure safety and enforce limits."""

    DANGEROUS_KEYWORDS = [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bDROP\b",
        r"\bALTER\b",
        r"\bTRUNCATE\b",
        r"\bCREATE\b",
        r"\bGRANT\b",
        r"\bREVOKE\b"
    ]

    @staticmethod
    def validate(query: str) -> str:
        """
        Validate an SQL query string.

        1. Allow only SELECT statements.
        2. Reject dangerous keywords.
        
        Args:
            query (str): SQL query to validate.

        Returns:
            str: Validated query 

        Raises:
            ValueError: If the query is invalid or dangerous.
        """
        query = query.strip()
        if not query.lower().startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        # Check for dangerous keywords
        for kw in QueryValidator.DANGEROUS_KEYWORDS:
            if re.search(kw, query, re.IGNORECASE):
                raise ValueError(f"Dangerous keyword detected: {kw}")

        return query

# Example use case:
if __name__ == "__main__":
    try:
        safe_query = QueryValidator.validate("SELECT * FROM cities;")
        print("Validated query:", safe_query)
    except ValueError as e:
        print("Validation error:", e)
