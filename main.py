import time
import logging
from fastapi import FastAPI, Request
from api.routes.reconciliation import router as reconciliation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("uvicorn")

app = FastAPI(title="FinFlow Intelligent IPRA", version="1.0.0")

# Middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"RID={request.scope.get('root_path')} METHOD={request.method} PATH={request.url.path} STATUS={response.status_code} TIME={formatted_process_time}ms"
    )
    return response

# Include routes
app.include_router(reconciliation_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to FinFlow Intelligent Invoice Processing & Reconciliation Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
