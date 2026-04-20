from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("sustaingate")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: create tables on startup for dev convenience."""
    from app.database import engine, Base
    import app.models  # noqa: F401 – ensure all models are imported for table creation

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")

    # Run seed data (gated by env flag — disable in production after first deploy)
    if settings.SEED_ON_STARTUP:
        from app.data.seed import run_seed
        from app.database import async_session

        async with async_session() as session:
            await run_seed(session)
            await session.commit()
        logger.info("Seed data loaded")
    else:
        logger.info("Seed data skipped (SEED_ON_STARTUP=false)")

    yield

    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(
    title="SustainGate API",
    description="AI-governed sustainability compliance platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
# `CORS_ORIGINS` is a comma-separated list of exact origins.
# Additionally, any Vercel preview deploy on *.vercel.app is allowed via
# `allow_origin_regex` so branch previews work without reconfiguring each time.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.auth import router as auth_router
from app.api.organisations import router as organisations_router
from app.api.frameworks import router as frameworks_router
from app.api.agents import router as agents_router
from app.api.emissions import router as emissions_router
from app.api.submissions import router as submissions_router
from app.api.crp import router as crp_router
from app.api.reports import router as reports_router
from app.api.regulatory import router as regulatory_router
from app.api.csv_upload import router as csv_upload_router
from app.api.users import router as users_router
from app.api.platform_admin import router as platform_admin_router

# Auth router at top level
app.include_router(auth_router, prefix="/api/v1")

# All API routers under /api/v1
app.include_router(organisations_router, prefix="/api/v1")
app.include_router(frameworks_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(emissions_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(crp_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(regulatory_router, prefix="/api/v1")
app.include_router(csv_upload_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(platform_admin_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sustaingate-api", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint returning application info."""
    return {
        "name": "SustainGate",
        "description": "AI-governed sustainability compliance platform",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
