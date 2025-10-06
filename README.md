# Text2SQL Analytics System

## Quickstart (local)

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
├── .env.example
├── .gitignore
├── setup.py
├── data/
│   ├── raw/
│   │   └── northwind.xlsx
│   └── schema/
│       └── schema.sql
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── database.py
│   ├── text2sql_engine.py
│   ├── query_validator.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data_loader.py
│   ├── test_database.py
│   ├── test_query_validator.py
│   ├── test_text2sql_engine.py
│   └── test_accuracy/
│       ├── test_simple_queries.py
│       ├── test_intermediate_queries.py
│       └── test_complex_queries.py
├── notebooks/
│   └── analysis.ipynb
└── scripts/
    ├── setup_database.py
    └── run_evaluation.py
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

## Testing

From root use:

```bash
pytest -v
```

Generate text coverage html

```bash
pytest --cov=src --cov-report=html
```

to see HTML coverage open `htmlcov/index.html` in browser.

## References

- [GenAI Doc](https://ai.google.dev/gemini-api/docs/quickstart)
- [Prompting_text2SQL](https://medium.com/datamindedbe/prompt-engineering-for-a-better-sql-code-generation-with-llms-263562c0c35d)
