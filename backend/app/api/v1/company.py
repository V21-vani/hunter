"""Company API routes — REST endpoints for companies."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CompanyOut])
def list_companies(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(None, description="Search by company name"),
    industry: str | None = Query(None, description="Filter by industry"),
    verification_status: str | None = Query(None, description="Filter by verification status"),
    db: Session = Depends(get_db),
) -> Any:
    """List companies with optional search and filtering."""
    service = CompanyService(db)
    companies = service.search(
        query=query,
        industry=industry,
        verification_status=verification_status,
        skip=(pagination.page - 1) * pagination.page_size,
        limit=pagination.page_size,
    )
    total = service.count_search(
        query=query, industry=industry, verification_status=verification_status
    )
    return {
        "items": companies,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size,
        "has_next": pagination.page * pagination.page_size < total,
        "has_prev": pagination.page > 1,
    }


@router.post("", response_model=CompanyOut)
def create_company(
    company_in: CompanyCreate, db: Session = Depends(get_db)
) -> Any:
    """Create a new company (duplicate prevention by name)."""
    service = CompanyService(db)
    return service.create_or_get(company_in)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: str, db: Session = Depends(get_db)
) -> Any:
    """Get a single company by ID."""
    service = CompanyService(db)
    company = service.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: str,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """Update a company by ID."""
    service = CompanyService(db)
    updated = service.update(company_id, company_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated


@router.delete("/{company_id}")
def delete_company(company_id: str, db: Session = Depends(get_db)) -> Any:
    """Delete a company by ID."""
    service = CompanyService(db)
    deleted = service.repo.delete(db, id=company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"detail": "Company deleted successfully"}