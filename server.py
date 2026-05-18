import uvicorn

if __name__ == "__main__":
    # Import the FastAPI app from main.py
    # This assumes main.py has an 'app' object
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
