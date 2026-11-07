"""Source discovery API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.adapters.registry import get as get_adapter, list_sources
from app.api.deps import get_db_dep
from app.core.logging import get_logger
from app.db.models.opportunity import Opportunity
from app.db.models.source_run import SourceRun
from app.schemas.source_run import SourceRunOut
from app.services.discovery_service import DiscoveryService

logger = get_logger(__name__)

router = APIRouter()


class DiscoveryRequest(BaseModel):
    source: str
    adapter_kwargs: dict[str, Any] = {}


class DiscoveryResponse(BaseModel):
    source: str
    found: int
    new: int
    updated: int


@router.get("", response_model=list[str])
def list_registered_sources() -> Any:
    """List all registered adapter source names."""
    return list_sources()


@router.post("/discover", response_model=DiscoveryResponse)
def discover_source(
    req: DiscoveryRequest, db: Session = Depends(get_db_dep)
) -> Any:
    """Run discovery for a single source and persist results."""
    adapter_cls = get_adapter(req.source)
    if adapter_cls is None:
        raise HTTPException(status_code=404, detail=f"Unknown source: {req.source}")

    with DiscoveryService(db) as svc:
        result = svc.run_source_and_persist(req.source, req.adapter_kwargs)

    return DiscoveryResponse(
        source=result["source"],
        found=result["found"],
        new=result["new"],
        updated=result["updated"],
    )


@router.get("/runs", response_model=list[SourceRunOut])
def list_source_runs(
    db: Session = Depends(get_db_dep),
    limit: int = 50,
) -> Any:
    """List recent source runs."""
    runs = (
        db.query(SourceRun)
        .order_by(SourceRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return runs


@router.get("/companies")
def list_companies(db: Session = Depends(get_db_dep)) -> Any:
    """List distinct companies with opportunity counts."""
    from sqlalchemy import func

    rows = (
        db.query(
            Opportunity.company,
            func.count(Opportunity.id).label("count"),
        )
        .group_by(Opportunity.company)
        .order_by(func.count(Opportunity.id).desc())
        .all()
    )
    return [{"company": r[0], "count": r[1]} for r in rows]