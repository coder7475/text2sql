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
        Validate and normalize an SQL SELECT query for safety and limits.
        
        Strips surrounding whitespace, enforces that the statement begins with SELECT, rejects queries containing any configured dangerous SQL keywords, and ensures a LIMIT clause is present by appending "LIMIT 1000;" if missing.
        
        Parameters:
            query (str): The SQL query to validate and possibly modify.
        
        Returns:
            str: The validated (and potentially modified) SQL query.
        
        Raises:
            ValueError: If the query does not start with SELECT or contains a dangerous keyword; the exception message indicates the reason.
        """
        query = query.strip()
        if not query.lower().startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        # Check for dangerous keywords
        for kw in QueryValidator.DANGEROUS_KEYWORDS:
            if re.search(kw, query, re.IGNORECASE):
                raise ValueError(f"Dangerous keyword detected: {kw}")

        # Ensure LIMIT is present and appended before any trailing semicolon
        if not re.search(r'\blimit\b', query, re.IGNORECASE):
            # Remove any trailing semicolon and whitespace
            query = re.sub(r';\s*$', '', query)
            query += " LIMIT 1000;"
        

        return query