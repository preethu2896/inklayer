import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv

from .routes import subscribe, admin
from .services.db_service import init_db
from .services.rate_limiter import limiter

# Load .env file from the backend/ directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Lifespan (replaces deprecated @app.on_event) ─────────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle events for FastAPI to initialize resources at startup."""
    await init_db()
    yield


# ── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Inklayer Backend API",
    description=(
        "Drop Notification & Community System for Inklayer Premium Streetwear.\n\n"
        "**Public:** POST /api/subscribe\n\n"
        "**Admin (JWT required):** GET /api/emails · PATCH /api/admin/tag · "
        "GET /api/admin/export · POST /api/send-drop\n\n"
        "Obtain a token via **POST /api/admin/login**."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Tightened to env config; use ["*"] only in dev
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Custom Error Handler — never expose raw errors to users ──────────────────
@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception):
    """Catches all unhandled exceptions and returns a generic 500 JSON response."""
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Something went wrong. Please try again."},
    )

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(subscribe.router, prefix="/api")
app.include_router(admin.router,    prefix="/api")

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Returns a basic 200 operational status when the backend is active."""
    return {"status": "operational", "service": "Inklayer API", "version": "2.0.0"}
