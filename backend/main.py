"""
AI Public Policy Impact Simulator — FastAPI Backend

Main application entry point with CORS, logging, and route registration.
"""

import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PolicyAI")

# Create FastAPI app
app = FastAPI(
    title="AI Policy Impact Simulator",
    description="ML-powered public policy impact prediction API",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",  # For development; restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
from routes.api import router
from routes.auth import router as auth_router
app.include_router(router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "name": "AI Policy Impact Simulator API",
        "version": "2.4.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
