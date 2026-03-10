from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import biscuits, users
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the IDV API...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    print("Shutting down the IDV API...")


app = FastAPI(
    title="Identity Verification (IDV) API",
    description="High-performance API for OCR, Biometrics, and User Management.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(users.router, prefix="/api/v1", tags=["User Management"])
app.include_router(biscuits.router, prefix="/api/v1", tags=["Biscuits"])


@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint to check if the API is up and running."""
    return {"status": "healthy", "message": "IDV API is operational."}
