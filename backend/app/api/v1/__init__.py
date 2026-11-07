"""API v1 routes."""

from app.api.v1.company import router as company_router
from app.api.v1.company_signal import router as company_signal_router
from app.api.v1.internship import router as internship_router
from app.api.v1.scan_log import router as scan_log_router
from app.api.v1.source import router as source_router
from app.api.v1.verification import router as verification_router

# Aggregate router for all v1 endpoints
from fastapi import APIRouter

router = APIRouter()
router.include_router(company_router, prefix="/companies", tags=["companies"])
router.include_router(company_signal_router, prefix="/company-signals", tags=["company-signals"])
router.include_router(internship_router, prefix="/internships", tags=["internships"])
router.include_router(scan_log_router, prefix="/scan-logs", tags=["scan-logs"])
router.include_router(source_router, prefix="/sources", tags=["sources"])
router.include_router(verification_router, prefix="/verifications", tags=["verifications"])

__all__ = ["router", "company_router", "company_signal_router", "internship_router",
           "scan_log_router", "source_router", "verification_router"]