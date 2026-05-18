import time
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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

# Ensure frontend directory exists
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(FRONTEND_PATH):
    os.makedirs(FRONTEND_PATH)

@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to FinFlow Intelligent Invoice Processing & Reconciliation Agent API. Frontend not found at /frontend/index.html"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
