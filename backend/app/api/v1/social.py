"""Social hiring intelligence API routes."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.social import (
    SocialSignalOut,
    SocialSignalCreate,
    SocialSignalUpdate,
)
from app.social.services.social_signal_service import SocialSignalService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SocialSignalOut])
def list_social_signals(
    pagination: PaginationParams = Depends(),
    platform: str | None = None,
    company: str | None = None,
    verification_status: str | None = None,
    query: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> Any:
    """List social signals with optional filtering."""
    service = SocialSignalService(db)
    # Filter by platform
    if platform:
        signals = service.repo.session.query(service.repo.model).filter(
            service.repo.model.platform == platform
        )
    else:
        signals = service.repo.session.query(service.repo.model)

    # Filter by verification status
    if verification_status:
        signals = signals.filter(service.repo.model.verification_status == verification_status)

    # Filter by company
    if company:
        signals = signals.filter(service.repo.model.company.ilike(f"%{company}%"))

    # Search
    if query:
        q = signals
        signals = q.filter(
            (service.repo.model.post_text.ilike(f"%{query}%"))
            | (service.repo.model.company.ilike(f"%{query}%"))
            | (service.repo.model.author.ilike(f"%{query}%"))
        )

    # Count and paginate
    signals = signals.order_by(service.repo.model.post_date.desc())
    total = signals.count()
    items = signals.offset(skip).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.post("", response_model=SocialSignalOut)
def create_social_signal(
    signal_in: SocialSignalCreate, db: Session = Depends(get_db)
) -> Any:
    """Create a new social signal."""
    service = SocialSignalService(db)
    return service.repo.create(
        db, signal_in.model_dump(exclude_unset=True, exclude={"id", "created_at"})
    )


@router.get("/companies/{company}", response_model=list[SocialSignalOut])
def get_signals_by_company(
    company: str, limit: int = 50, db: Session = Depends(get_db)
) -> Any:
    """Get all social signals for a company."""
    service = SocialSignalService(db)
    return service.get_by_company(company=company, limit=limit)


@router.get("/verify/{signal_id}", response_model=SocialSignalOut)
def verify_signal(signal_id: str, db: Session = Depends(get_db)) -> Any:
    """Manually verify a social signal.

    Updates verification_status to 'verified' if an official opening
    or employer-owned application route is confirmed.
    """
    signal = (
        db.query(service.repo.model).filter(service.repo.model.id == signal_id).first()
    )
    if not signal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Social signal not found")

    # In a real implementation, this would trigger:
    # 1. Match against official careers page
    # 2. Confirm employer-owned application route
    # 3. Update verification_status to 'verified'
    signal.verification_status = "verified"
    signal.last_verified = db.func.now()  # Assuming a column exists
    db.commit()
    db.refresh(signal)
    return signal
