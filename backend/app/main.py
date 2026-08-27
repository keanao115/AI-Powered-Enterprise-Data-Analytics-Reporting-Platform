from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import PlatformException
from app.observability.middleware import ObservabilityMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.queries import router as queries_router
from app.api.v1.schemas import router as schemas_router
from app.api.v1.metrics import metrics_router
from app.api.v1.reports import router as reports_router
from app.api.v1.audit import router as audit_router
from app.api.v1.evaluation import eval_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.security import router as security_router

app = FastAPI(
    title="AI-Powered Enterprise Data Analytics & Reporting Platform",
    description="Enterprise-Grade AI Analyst Agent platform with Text-to-SQL, AST security boundaries, RLS, PII firewall, and grounded report generation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry & Observability Middleware
app.add_middleware(ObservabilityMiddleware)


@app.exception_handler(PlatformException)
async def platform_exception_handler(request: Request, exc: PlatformException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", "N/A"),
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": {"reason": str(exc)},
                "request_id": getattr(request.state, "request_id", "N/A"),
            }
        },
    )


# Startup Event: Auto-verify and seed DuckDB if tables are missing
@app.on_event("startup")
async def startup_event():
    import duckdb
    from app.core.database import get_analytics_db_path
    
    db_path = get_analytics_db_path()
    try:
        conn = duckdb.connect(db_path)
        tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
        conn.close()
        
        required_tables = [
            "nyc_taxi_trips", "olist_orders", "bts_flights",
            "mimic_icu_stays", "chicago_crimes", "market_securities"
        ]
        if not all(t in tables for t in required_tables):
            print(f"[Startup] Missing tables detected. Running complete database seeder on '{db_path}'...")
            from seed.seed_data import seed_synthetic_analytics_database
            seed_synthetic_analytics_database(db_path)
            print(f"[Startup] Successfully seeded all 6 real-world dataset tables into '{db_path}'.")
    except Exception as e:
        print(f"[Startup Warning] DuckDB verification or auto-seed encountered: {e}")


# Health checks
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "HEALTHY", "version": "1.0.0", "env": settings.APP_ENV}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    return {"status": "READY", "database": "CONNECTED", "llm_provider": settings.LLM_PROVIDER}


@app.get("/live", tags=["Health"])
async def liveness_check():
    return {"status": "ALIVE"}


# Include API v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(queries_router, prefix="/api/v1")
app.include_router(schemas_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(eval_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")
app.include_router(security_router, prefix="/api/v1")
