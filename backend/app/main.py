from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .routes import subscribe
from .services.db_service import init_db
from .services.rate_limiter import limiter

app = FastAPI(
    title="Inklayer Backend API",
    description="Drop Notification and Community Backend System",
    version="1.0.0"
)

# Connect to the slowapi Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Adjust CORS to allow our frontend to consume the API properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be tightened strictly to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Database at startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# Hook the API routes to the application
app.include_router(subscribe.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "operational", "service": "Inklayer API"}
