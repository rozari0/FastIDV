from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import users

app = FastAPI(
    title="Identity Verification (IDV) API",
    description="High-performance API for OCR, Biometrics, and User Management.",
    version="1.0.0",
)

# Set up CORS (Cross-Origin Resource Sharing)
# Update this with your actual frontend domains in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register your routers with appropriate prefixes and tags
# app.include_router(idv.router, prefix="/api/v1/idv", tags=["Identity Verification"])
app.include_router(users.router, prefix="/api/v1", tags=["User Management"])


@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint to check if the API is up and running."""
    return {"status": "healthy", "message": "IDV API is operational."}
