"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.v1 import opportunities, sources
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="InternRadar Discovery Engine",
    version="0.1.0",
    description="Discovery engine for paid remote internships open to candidates in India",
)

app.include_router(
    sources.router, prefix=f"{settings.API_V1_STR}/sources", tags=["sources"]
)
app.include_router(
    opportunities.router,
    prefix=f"{settings.API_V1_STR}/opportunities",
    tags=["opportunities"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "internradar-discovery"}


@app.get("/")
def root():
    return {
        "service": "InternRadar Discovery Engine",
        "version": "0.1.0",
        "docs": "/docs",
    }