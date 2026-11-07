"""Internship API routes — REST endpoints for internships."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.internship import InternshipCreate, InternshipOut, InternshipUpdate
from app.services.internship_service import InternshipService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[InternshipOut])
def list_internships(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(None, description="Search by role title"),
    company_id: str | None = Query(None, description="Filter by company ID"),
    role_category: str | None = Query(None, description="Filter by role category"),
    remote_status: str | None = Query(None, description="Filter by remote status"),
    india_eligible: bool | None = Query(None, description="Filter by India eligibility"),
    status: str | None = Query(None, description="Filter by status"),
    sort_by: str | None = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    db: Session = Depends(get_db),
) -> Any:
    """List internships with optional filtering, pagination and sorting."""
    service = InternshipService(db)
    internships = service.search(
        query=query,
        company_id=UUID(company_id) if company_id else None,
        role_category=role_category,
        remote_status=remote_status,
        india_eligible=india_eligible,
        status=status,
        skip=(pagination.page - 1) * pagination.page_size,
        limit=pagination.page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total = service.count_search(
        query=query,
        company_id=UUID(company_id) if company_id else None,
        role_category=role_category,
        remote_status=remote_status,
        india_eligible=india_eligible,
        status=status,
    )
    return {
        "items": internships,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size,
        "has_next": pagination.page * pagination.page_size < total,
        "has_prev": pagination.page > 1,
    }


@router.post("", response_model=InternshipOut)
def create_internship(
    internship_in: InternshipCreate, db: Session = Depends(get_db)
) -> Any:
    """Create a new internship (duplicate prevention by role + company)."""
    service = InternshipService(db)
    return service.create_or_get_duplicate(internship_in)


@router.get("/{internship_id}", response_model=InternshipOut)
def get_internship(
    internship_id: str, db: Session = Depends(get_db)
) -> Any:
    """Get a single internship by ID."""
    service = InternshipService(db)
    internship = service.get(internship_id)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return internship


@router.patch("/{internship_id}", response_model=InternshipOut)
def update_internship(
    internship_id: str,
    internship_in: InternshipUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """Update an internship by ID."""
    service = InternshipService(db)
    updated = service.update(internship_id, internship_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Internship not found")
    return updated


@router.delete("/{internship_id}")
def delete_internship(internship_id: str, db: Session = Depends(get_db)) -> Any:
    """Delete a internship by ID."""
    service = InternshipService(db)
    deleted = service.repo.delete(db, id=internship_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Internship not found")
    return {"detail": "Internship deleted successfully"}