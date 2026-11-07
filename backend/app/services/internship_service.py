"""Internship service — business logic for internships."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.internship import Internship
from app.db.repositories.internship_repository import InternshipRepository
from app.schemas.internship import InternshipCreate, InternshipUpdate

logger = get_logger(__name__)


class InternshipService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = InternshipRepository(session)

    def create_or_get_duplicate(
        self, internship_in: InternshipCreate
    ) -> Internship:
        """Duplicate prevention by role_title + company_id."""
        internship = self.repo.create_or_get_duplicate(
            self.session, internship_in=internship_in
        )
        logger.info(
            "Internship created or retrieved",
            role=internship.role_title,
            id=str(internship.id),
        )
        return internship

    def get(self, internship_id: str) -> Optional[Internship]:
        return self.repo.get(self.session, id=internship_id)

    def search(
        self,
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
        return self.repo.search(
            self.session,
            query=query,
            company_id=company_id,
            role_category=role_category,
            remote_status=remote_status,
            india_eligible=india_eligible,
            status=status,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def count_search(
        self,
        query: Optional[str] = None,
        company_id: Optional[UUID] = None,
        role_category: Optional[str] = None,
        remote_status: Optional[str] = None,
        india_eligible: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> int:
        return self.repo.count_search(
            self.session,
            query=query,
            company_id=company_id,
            role_category=role_category,
            remote_status=remote_status,
            india_eligible=india_eligible,
            status=status,
        )

    def update(self, internship_id: str, internship_in: InternshipUpdate) -> Optional[Internship]:
        db_obj = self.repo.get(self.session, id=internship_id)
        if not db_obj:
            return None
        update_data = internship_in.model_dump(exclude_unset=True)
        return self.repo.update(self.session, db_obj=db_obj, obj_in=update_data)