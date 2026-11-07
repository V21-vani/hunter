"""Opportunity API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityList, OpportunityOut

router = APIRouter()


@router.get("", response_model=OpportunityList)
def list_opportunities(
    db: Session = Depends(get_db_dep),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: str | None = Query(None),
    company: str | None = Query(None),
    is_remote: bool | None = Query(None),
    is_paid: bool | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
) -> Any:
    """List discovered opportunities with optional filtering."""
    query = db.query(Opportunity)

    if source:
        query = query.filter(Opportunity.source == source)
    if company:
        query = query.filter(Opportunity.company.ilike(f"%{company}%"))
    if is_remote is not None:
        query = query.filter(Opportunity.is_remote == is_remote)
    if is_paid is not None:
        query = query.filter(Opportunity.is_paid == is_paid)
    if status:
        query = query.filter(Opportunity.status == status)
    if search:
        query = query.filter(
            Opportunity.title.ilike(f"%{search}%")
            | Opportunity.company.ilike(f"%{search}%")
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Opportunity.discovered_at.desc()).offset(offset).limit(page_size).all()

    return OpportunityList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db_dep)) -> Any:
    """Get a single opportunity by ID."""
    from uuid import UUID

    opp = db.query(Opportunity).filter(Opportunity.id == UUID(opportunity_id)).first()
    if not opp:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp