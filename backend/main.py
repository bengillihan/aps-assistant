"""
APS Internal Assistant — FastAPI entrypoint.

Run locally:
    uvicorn main:app --reload --port 8000

The frontend (or Electron shell) connects to http://localhost:8000.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes import router

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# --- App ---
app = FastAPI(
    title=settings.app_name,
    description="Internal AI assistant with mode-based prompts and LLM failover.",
    version="0.1.0",
    docs_url="/docs",       # Swagger UI — disable in prod if desired
    redoc_url="/redoc",
)

# --- CORS ---
# Allow the React dev server and Electron (file://) origins.
# Tighten this list in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server (alternative)
        "null",                    # Electron production: file:// requests arrive with origin "null"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
