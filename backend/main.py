"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import data, analytics, ml, prediction
import uvicorn
import os
import shutil
from pathlib import Path
from config import DATA_DIR, DATASET_FILENAME

# Ensure database tables exist
init_db()

# Ensure the dataset is in the data directory if it's available in the root
root_dataset = Path(__file__).parent.parent / DATASET_FILENAME
target_dataset = DATA_DIR / DATASET_FILENAME

if root_dataset.exists() and not target_dataset.exists():
    DATA_DIR.mkdir(exist_ok=True)
    shutil.copy2(root_dataset, target_dataset)


app = FastAPI(
    title="T2S CT Scanner Predictive Maintenance API",
    description="API for estimating failure risk of CT Scanners using Machine Learning.",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3005", "http://127.0.0.1:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router)
app.include_router(analytics.router)
app.include_router(ml.router)
app.include_router(prediction.router)


@app.get("/")
def root():
    """API health check."""
    return {"status": "online", "message": "T2S Predictive Maintenance API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
