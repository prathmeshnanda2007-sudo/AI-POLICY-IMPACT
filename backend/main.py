"""
AI Public Policy Impact Simulator — FastAPI Backend

Main application entry point with CORS, logging, route registration,
and production-ready static file serving with SPA fallback.
"""

import logging
import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Nexora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # --- Startup ---
    logger.info("[STARTUP] Initializing database...")
    try:
        from services.database import init_db
        init_db()
        logger.info("[STARTUP] Database ready.")
    except Exception as e:
        logger.error(f"[STARTUP] Database init failed: {e}")

    logger.info("[STARTUP] Verifying ML model...")
    try:
        from models.ml_model import load_model
        model, scaler, meta = load_model()
        logger.info(f"[STARTUP] Model loaded: {meta.get('model_type', 'unknown')} | R²={meta.get('r2_score', 0):.4f}")
    except Exception as e:
        logger.warning(f"[STARTUP] Model load warning: {e}")

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("[SHUTDOWN] Nexora backend shutting down.")


# Create FastAPI app
app = FastAPI(
    title="AI Policy Impact Simulator",
    description="ML-powered public policy impact prediction API",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow frontend connections
# NOTE: Wildcards in allow_origins don't work with allow_credentials=True in browsers
_ENV = os.environ.get("ENVIRONMENT", "production")

if _ENV == "development":
    # Development: allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: specific origins + regex for Vercel previews
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "https://ai-policy-impact-d9th.vercel.app",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Import and register API routes
from routes.api import router
from routes.auth import router as auth_router
from routes.ws import router as ws_router

app.include_router(router)
app.include_router(auth_router)
app.include_router(ws_router)


@app.get("/api/status")
async def api_status():
    return {
        "name": "AI Policy Impact Simulator API",
        "version": "2.5.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# --- Serve Frontend (Production) ---
# Path to the built frontend (../dist relative to backend/)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "dist"

if FRONTEND_DIR.is_dir():
    logger.info(f"[OK] Serving frontend from: {FRONTEND_DIR}")

    # Mount static assets (JS, CSS, images) under /assets
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")

    # Serve other static files at root level (favicon, etc.)
    @app.get("/favicon.svg")
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = FRONTEND_DIR / "favicon.svg"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return JSONResponse({"error": "not found"}, status_code=404)

    # SPA Fallback: Any route not matched by API endpoints serves index.html
    # This is the KEY fix for 404 errors — React Router handles routing client-side
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Don't intercept API docs
        if full_path in ("docs", "redoc", "openapi.json"):
            return None

        # Try to serve the exact file if it exists (e.g., favicon.svg)
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise, serve index.html (SPA fallback)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

        return JSONResponse({"error": "not found"}, status_code=404)
else:
    logger.warning(f"[WARN] Frontend dist/ not found at {FRONTEND_DIR}")
    logger.warning("   Run 'npm run build' in the project root to build the frontend.")

    # When no frontend build exists, serve API root info
    @app.get("/")
    async def root():
        return {
            "name": "AI Policy Impact Simulator API",
            "version": "2.5.0",
            "status": "online",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build' to create the dist/ folder.",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

