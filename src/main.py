import sys
import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.query_validator import QueryValidator
from src.text2sql_engine import generate_sql_query, sanitize_sql
from src.utils import build_prompt, df_to_json, execute_query_on_db

load_dotenv()


client = genai.Client()


# Request and Response Model for generate-sql endpoint
class SQLResponseModel(BaseModel):
    sql_query: str
    sanitized_query: str
    validate_query: str
    result_json: str

class Text2SQLRequest(BaseModel):
    question: str


app = FastAPI(
    title="Text2SQL API (Gemini + Northwind)",
    version="1.0.0",
    description="Convert natural language questions to SQL queries and execute them safely."
)

# Middlewares
# Auth Middleware
@app.middleware
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} took {process_time} time")

    return response

# Rate Limiting Middleware
requests = {}

RATE_LIMIT = 5 # requests
RATE_TIME = 10 # seconds

@app.middleware("http")

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host

    if client_ip in requests:
        if len(requests[client_ip]) >= RATE_LIMIT:
            # Remove old requests
            current_time = time.time()
            requests[client_ip] = [
                req_time for req_time in requests[client_ip]
                if current_time - req_time < RATE_TIME
            ]
            if len(requests[client_ip]) >= RATE_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={"message": "Too many requests"}
                )
    else:
        requests[client_ip] = []

    requests[client_ip].append(time.time())

    response = await call_next(request)
    return response

# Custom Exception class
class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name


# Custom Exception Handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something wrong."},
    )

# Router
@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Text2SQL API running."}


@app.post("/generate-sql", response_model=SQLResponseModel)
def generate_and_execute_sql(request: Text2SQLRequest):
    try:
        print(request.question)
        prompt = build_prompt(request.question)
        # Generate SQL using Gemini
        raw_sql = generate_sql_query(prompt)
        sanitized_sql = sanitize_sql(raw_sql)

        if not sanitized_sql:
            raise HTTPException(status_code=400, detail="Generated SQL is empty after sanitization.")

        # Validate the SQL
        validated_sql = QueryValidator.validate(sanitized_sql)

        df = execute_query_on_db(validated_sql)

        return SQLResponseModel(
            sql_query=raw_sql,
            sanitized_query=sanitized_sql,
            validate_query=validated_sql,
            result_json=df_to_json(df)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")