"""Verification repository — CRUD and queries for verifications."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.verification import Verification
from app.db.repositories.base_repository import BaseRepository
from app.schemas.verification import VerificationCreate, VerificationUpdate


class VerificationRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Verification)

    def get_by_internship(
        self, session: Session, *, internship_id: UUID
    ) -> Optional[Verification]:
        return (
            session.query(Verification)
            .filter(Verification.internship_id == internship_id)
            .first()
        )

    def create_or_update_for_internship(
        self,
        session: Session,
        *,
        internship_id: UUID,
        verification_in: VerificationCreate,
    ) -> Verification:
        existing = self.get_by_internship(session, internship_id=internship_id)
        if existing:
            update_data = verification_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(existing, field, value)
            session.commit()
            session.refresh(existing)
            return existing
        return self.create(session, obj_in=verification_in.model_dump())

    def search_by_status(
        self,
        session: Session,
        *,
        employer_verification_status: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Verification]:
        return (
            session.query(Verification)
            .filter(
                Verification.employer_verification_status == employer_verification_status
            )
            .offset(skip)
            .limit(limit)
            .all()
        )