from fastapi import FastAPI
from api.routes.reconciliation import router as reconciliation_router

app = FastAPI(title="FinFlow Intelligent IPRA", version="1.0.0")

# Include routes
app.include_router(reconciliation_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to FinFlow Intelligent Invoice Processing & Reconciliation Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
