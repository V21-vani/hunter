"""Pydantic schemas for API requests/responses."""

from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate
from app.schemas.common import ErrorResponse, PaginationParams, PaginatedResponse
from app.schemas.company_signal import (
    CompanySignalCreate,
    CompanySignalOut,
    CompanySignalUpdate,
)
from app.schemas.internship import InternshipCreate, InternshipOut, InternshipUpdate
from app.schemas.scan_log import ScanLogCreate, ScanLogOut, ScanLogUpdate
from app.schemas.source import SourceCreate, SourceOut, SourceUpdate
from app.schemas.social import SocialSignalCreate, SocialSignalOut, SocialSignalUpdate
from app.schemas.verification import VerificationCreate, VerificationOut, VerificationUpdate

__all__ = [
    "CompanyCreate",
    "CompanyOut",
    "CompanyUpdate",
    "CompanySignalCreate",
    "CompanySignalOut",
    "CompanySignalUpdate",
    "ErrorResponse",
    "InternshipCreate",
    "InternshipOut",
    "InternshipUpdate",
    "PaginationParams",
    "PaginatedResponse",
    "ScanLogCreate",
    "ScanLogOut",
    "ScanLogUpdate",
    "SocialSignalCreate",
    "SocialSignalOut",
    "SocialSignalUpdate",
    "SourceCreate",
    "SourceOut",
    "SourceUpdate",
    "VerificationCreate",
    "VerificationOut",
    "VerificationUpdate",
]