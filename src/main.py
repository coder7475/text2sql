import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai

from src.utils import build_prompt

app = FastAPI(
    title="Text2SQL API (Gemini + Northwind)",
    version="1.0.0",
    description="Convert natural language questions to SQL queries and execute them safely."
)



client = genai.Client()


# Request and Response Model for generate-sql endpoint
class SQLResponseModel(BaseModel):
    sql_query: str
    sanitized_query: str
    validate_query: str
    result_json: str

class Text2SQLRequest(BaseModel):
    question: str

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
        prompt = build_prompt(request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")