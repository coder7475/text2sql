import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse



app = FastAPI()

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
@app.get("/test")
async def test():
    # Improved logic: Informative message and custom exception for demonstration
    active_ips = list(requests.keys())
    if len(active_ips) > 2:
        raise CustomException(name=f"Too many active IPs: {active_ips}")
    return JSONResponse({"message": "Request successful", "active_requesters": active_ips})
