"""Internship repository — CRUD and queries for internships."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.internship import Internship
from app.db.repositories.base_repository import BaseRepository
from app.schemas.internship import InternshipCreate, InternshipUpdate


class InternshipRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Internship)

    def get_by_role_and_company(
        self,
        session: Session,
        *,
        role_title: str,
        company_id: UUID,
    ) -> Optional[Internship]:
        return (
            session.query(Internship)
            .filter(
                Internship.role_title == role_title,
                Internship.company_id == company_id,
            )
            .first()
        )

    def create_or_get_duplicate(
        self,
        session: Session,
        *,
        internship_in: InternshipCreate,
    ) -> Internship:
        """Duplicate prevention: return existing internship by role+company or create new."""
        if internship_in.company_id:
            existing = self.get_by_role_and_company(
                session,
                role_title=internship_in.role_title,
                company_id=internship_in.company_id,
            )
            if existing:
                # Update fields if new data provided
                update_data = internship_in.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    if value is not None:
                        setattr(existing, field, value)
                session.commit()
                session.refresh(existing)
                return existing
        return self.create(session, obj_in=internship_in.model_dump())

    def search(
        self,
        session: Session,
        *,
        query: Optional[str] = None,
        company_id: Optional[UUID] = None,
        role_category: Optional[str] = None,
        remote_status: Optional[str] = None,
        india_eligible: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> list[Internship]:
        q = session.query(Internship)
        if query:
            search = f"%{query}%"
            q = q.filter(Internship.role_title.ilike(search))
        if company_id:
            q = q.filter(Internship.company_id == company_id)
        if role_category:
            q = q.filter(Internship.role_category == role_category)
        if remote_status:
            q = q.filter(Internship.remote_status == remote_status)
        if india_eligible is not None:
            q = q.filter(Internship.india_eligible == india_eligible)
        if status:
            q = q.filter(Internship.status == status)
        if sort_by and hasattr(Internship, sort_by):
            col = getattr(Internship, sort_by)
            if sort_order == "asc":
                q = q.order_by(col.asc())
            else:
                q = q.order_by(col.desc())
        else:
            q = q.order_by(Internship.first_discovered_date.desc())
        return q.offset(skip).limit(limit).all()

    def count_search(
        self,
        session: Session,
        *,
        query: Optional[str] = None,
        company_id: Optional[UUID] = None,
        role_category: Optional[str] = None,
        remote_status: Optional[str] = None,
        india_eligible: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> int:
        q = session.query(Internship)
        if query:
            search = f"%{query}%"
            q = q.filter(Internship.role_title.ilike(search))
        if company_id:
            q = q.filter(Internship.company_id == company_id)
        if role_category:
            q = q.filter(Internship.role_category == role_category)
        if remote_status:
            q = q.filter(Internship.remote_status == remote_status)
        if india_eligible is not None:
            q = q.filter(Internship.india_eligible == india_eligible)
        if status:
            q = q.filter(Internship.status == status)
        return q.count()