# Text2SQL Analytics System (Prototype)

Minimum viable scaffold created by ChatGPT.

## Quickstart (local)
1. Create a Python 3.10+ virtual environment and activate it.
   ```bash
   python -m venv .venv
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

## Structure
- `src/` — source code (data loader, DB, text2sql engine, validator)
- `scripts/` — helper scripts (db setup)
- `data/` — sample input data (put northwind.xlsx in `data/raw/`)
- `tests/` — pytest tests

## Notes
- This is an initial scaffold. Implementations (Gemini integration, full normalization) are provided as stubs to be developed next.
