"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.v1 import company, company_signal, internship, scan_log, source, social, verification, v1
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="InternRadar Discovery Engine",
    version="0.1.0",
    description="Discovery engine for paid remote internships open to candidates in India",
)

# Phase 1: Backend Infrastructure routes
app.include_router(company.router, prefix=f"{settings.API_V1_STR}/companies", tags=["companies"])
app.include_router(company_signal.router, prefix=f"{settings.API_V1_STR}/company-signals", tags=["company-signals"])
app.include_router(internship.router, prefix=f"{settings.API_V1_STR}/internships", tags=["internships"])
app.include_router(scan_log.router, prefix=f"{settings.API_V1_STR}/scan-logs", tags=["scan-logs"])
app.include_router(source.router, prefix=f"{settings.API_V1_STR}/sources", tags=["sources"])
app.include_router(verification.router, prefix=f"{settings.API_V1_STR}/verifications", tags=["verifications"])

# Phase 2: Discovery Engine routes (legacy, placeholder)
from app.api.v1 import opportunities as opportunities_router

app.include_router(opportunities_router, prefix=f"{settings.API_V1_STR}/opportunities", tags=["opportunities"])

# Phase 3: Social Hiring Intelligence routes
app.include_router(social.router, prefix=f"{settings.API_V1_STR}/social", tags=["social"])

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