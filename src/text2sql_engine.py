from dotenv import load_dotenv
from google import genai
import re

load_dotenv()
client = genai.Client()


def generate_sql_query(prompt: str) -> str:
    """Generate SQL query from an English prompt using the Gemini API."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return ""


def sanitize_sql(sql: str) -> str:
    """Sanitize the generated SQL query."""
    # Remove non-ASCII characters
    sql = re.sub(r'[^\x00-\x7F]+', '', sql)
    # Strip leading/trailing whitespace
    sql = sql.strip()
    # Further sanitization steps can be added here
    return sql


if __name__ == "__main__":
    prompt = "Retrieve all orders placed in 2025 from the Orders table."
    sql_query = generate_sql_query(prompt)
    sanitized_query = sanitize_sql(sql_query)
    print("Generated SQL Query:", sanitized_query)
