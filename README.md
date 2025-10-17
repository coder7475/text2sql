# Text2SQL Analytics System

## Project Overview

The **Text2SQL Analytics System** allows users to interact with a normalized Northwind PostgreSQL database using natural language queries. Queries are converted into SQL via the **Gemini API**, validated for safety, executed on the database, and returned as structured outputs (JSON or pandas DataFrame).

**Architecture Diagram:**

```sh
[User Input (Natural Language)]
|
v
[Text2SQL Engine - Gemini API]
|
v
[Query Sanitizer & Validator]
|
v
[PostgreSQL DB]
|
v
[Results: pandas DataFrame / JSON]
```

## Quickstart

1. Create a Python 3.10+ virtual environment and activate it.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate    # Windows (PowerShell)
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Fill `.env` based on `.env.example` and start a local Postgres (or Docker Compose).
4. Use `scripts/setup_database.py` to prepare schema and optionally load CSVs.
5. Use `run_query.py` to try sample queries (currently uses mocked LLM responses).

## Project Structure

```bash
text2sql-analytics/
├── README.md
├── requirements.txt
├── docker-compose
├── .env.example
├── .gitignore
├── setup.py
├── data/
│   ├── normalized/*
│   ├── raw/
│   │   └── northwind.xlsx
│   └── schema/
│       └── schema.sql
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── text2sql_engine.py
│   ├── query_validator.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data_loader.py
|   |── test_db_connection.py
|   |── test_mock_utils_db.py
│   ├── test_query_validator.py
│   ├── test_text2sql_engine.py
│   ├── test_utils.py
│   └── mocks/
│       ├── mock_gemini_client.py
├── notebooks/
│   └── analysis.ipynb
└── scripts/
    ├── setup_database.py

```

## Database Setup

### Run with Docker Compose

1. **Ensure Docker is installed and running**

   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

2. **Start PostgreSQL via Docker Compose**

   From the project root directory:

   ```bash
   docker-compose up -d
   ```

   This will:

   - Start a PostgreSQL 17 container named `text2sql-db-1`
   - Expose port `5432`
   - Create a database `northwind_db` with user `northwind_admin` and password `northwind123`
   - Persist data inside `data/postgres/`

3. **Verify the container is running**

   ```bash
   docker ps
   ```

4. **Connect to the database**

   ```bash
   docker exec -it text2sql-db-1 psql -U northwind_admin -d northwind_db
   ```

### Environment Configuration

1. Create a `.env` file in the project root (or copy `.env.example`):

   ```bash
   cp .env.example .env
   ```

2. Update it with your local database credentials:

   ```bash
   # Example environment variables
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=northwind_db
   DB_USER=northwind_admin
   DB_PASSWORD=northwind123
   GEMINI_API_KEY=your_gemini_api_key_here

   ```

### Verify Database Connection

To confirm the connection works:

```bash
python3 tests/test_db_connection.py
```

If you see:

```
Connected to: northwind_db
```

You’re good to go!

## Data Model

ER Diagram

[![](./Northwind_ER_Diagram.png)]

## Data Engineering

Load the data

```bash
python3 src/data_loader.py --excel data/raw/northwind.xlsx
```

## Text2SQL engine

Run

```sh
python3 src/text2sql_engine.py
```

output:

```json
python3 src/text2sql_engine.py
Generated SQL Query: SELECT * FROM cities;
/home/fahad/text2sql/src/../src/utils.py:141: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, conn)

Query: Find all unique city names

Query Results (JSON):
[
  {
    "city_id":1,
    "city_name":"Berlin",
    "region_id":1,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":2,
    "city_name":"M\u00e9xico D.F.",
    "region_id":2,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":3,
    "city_name":"London",
    "region_id":3,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":4,
    "city_name":"Lule\u00e5",
    "region_id":4,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":5,
    "city_name":"Mannheim",
    "region_id":1,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":6,
    "city_name":"Strasbourg",
    "region_id":5,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":7,
    "city_name":"Madrid",
    "region_id":6,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":8,
    "city_name":"Marseille",
    "region_id":5,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":9,
    "city_name":"Tsawassen",
    "region_id":7,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":10,
    "city_name":"Buenos Aires",
    "region_id":8,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },
  {
    "city_id":11,
    "city_name":"Bern",
    "region_id":9,
    "created_at":1759732635038,
    "updated_at":1759732635038
  },

 ....

  {
    "city_id":95,
    "city_name":"Annecy",
    "region_id":5,
    "created_at":1759732635709,
    "updated_at":1759732635709
  },
  {
    "city_id":96,
    "city_name":"Ste-Hyacinthe",
    "region_id":25,
    "created_at":1759732635709,
    "updated_at":1759732635709
  },
  {
    "city_id":97,
    "city_name":"Colchester",
    "region_id":45,
    "created_at":1759732830414,
    "updated_at":1759732830414
  }
]
```

## API Design

### Overview

The Text2SQL Analytics System exposes a RESTful API built with **FastAPI** that converts natural language queries into SQL and executes them against a PostgreSQL database. The API includes built-in security features, rate limiting, and comprehensive error handling.

### Base URL

```
http://localhost:8000
```

### Authentication & Security

- **Rate Limiting**: 5 requests per 10 seconds per IP address
- **Request Timeout**: Monitored via `X-Process-Time` header
- **SQL Injection Protection**: Built-in query validation and sanitization
- **Error Handling**: Structured error responses with appropriate HTTP status codes

### Endpoints

#### 1. Health Check

**GET** `/`

Returns the API health status.

**Response:**

```json
{
  "status": "ok",
  "message": "Text2SQL API running."
}
```

#### 2. Generate and Execute SQL

**POST** `/generate-sql`

Converts natural language to SQL, validates the query, and executes it against the database.

**Request Body:**

```json
{
  "question": "Show all orders shipped in 1997"
}
```

**Response Schema:**

```json
{
  "sql_query": "string", // Raw SQL generated by Gemini
  "sanitized_query": "string", // SQL after sanitization
  "validate_query": "string", // Final validated SQL
  "result_json": "string" // Query results as JSON string
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/generate-sql" \
     -H "Content-Type: application/json" \
     -d '{"question": "Find all customers from Germany"}'
```

**Example Response:**

```json
{
  "sql_query": "SELECT * FROM customers WHERE country = 'Germany';",
  "sanitized_query": "SELECT * FROM customers WHERE country = 'Germany'",
  "validate_query": "SELECT * FROM customers WHERE country = 'Germany'",
  "result_json": "[{\"customer_id\":1,\"company_name\":\"Alfreds Futterkiste\",\"country\":\"Germany\"}]"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Validation error: Invalid SQL syntax"
}
```

#### 429 Too Many Requests

```json
{
  "message": "Too many requests"
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Internal error: Database connection failed"
}
```

### Request/Response Models

**Text2SQLRequest:**

- `question` (string, required): Natural language query
- Default: "Show all orders shipped in 1997"

**SQLResponseModel:**

- `sql_query` (string): Original SQL generated by Gemini API
- `sanitized_query` (string): SQL after sanitization process
- `validate_query` (string): Final validated SQL ready for execution
- `result_json` (string): Query results serialized as JSON

### API Features

#### Middleware Stack

1. **Process Time Tracking**: Adds `X-Process-Time` header to all responses
2. **Rate Limiting**: IP-based request limiting (5 req/10sec)
3. **CORS**: Cross-origin resource sharing support

#### Query Processing Pipeline

1. **Natural Language Input**: User provides English question
2. **Prompt Engineering**: Question converted to optimized prompt
3. **SQL Generation**: Gemini API generates SQL query
4. **Sanitization**: Remove dangerous SQL constructs
5. **Validation**: Ensure SQL syntax and safety
6. **Execution**: Run validated query against PostgreSQL
7. **Serialization**: Convert results to JSON format

#### Supported Query Types

- **SELECT queries**: Data retrieval operations
- **Aggregations**: COUNT, SUM, AVG, MIN, MAX
- **Joins**: Inner, left, right joins across tables
- **Filtering**: WHERE clauses with various conditions
- **Grouping**: GROUP BY with HAVING clauses
- **Sorting**: ORDER BY operations

#### Blocked Operations

- INSERT, UPDATE, DELETE statements
- DROP, ALTER, CREATE statements
- System function calls
- Subqueries with potential security risks

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Running the FastAPI Application

To start the development server with hot-reload, run:

```bash
uvicorn src.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

### Production Deployment

For production deployment, use:

```bash
# With specific host and port
uvicorn src.main:app --host 0.0.0.0 --port 8000

# With multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

From root use:

```bash
pytest -v
```

Generate text coverage html

```bash
pytest --cov=src --cov-report=html
```

to see HTML coverage open `htmlcov/index.html` in browser:

```
http://localhost:5500/htmlcov/
```

## References

- [GenAI Doc](https://ai.google.dev/gemini-api/docs/quickstart)
- [Prompting_text2SQL](https://medium.com/datamindedbe/prompt-engineering-for-a-better-sql-code-generation-with-llms-263562c0c35d)
