"""Verification service — business logic for verifications."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.verification import Verification
from app.db.repositories.verification_repository import VerificationRepository
from app.schemas.verification import VerificationCreate, VerificationUpdate

logger = get_logger(__name__)


class VerificationService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = VerificationRepository(session)

    def create_or_update_for_internship(
        self,
        internship_id: UUID,
        verification_in: VerificationCreate,
    ) -> Verification:
        verification = self.repo.create_or_update_for_internship(
            self.session,
            internship_id=internship_id,
            verification_in=verification_in,
        )
        logger.info(
            "Verification created or updated",
            internship_id=str(internship_id),
            status=verification.employer_verification_status,
        )
        return verification

    def get_by_internship(self, internship_id: UUID) -> Optional[Verification]:
        return self.repo.get_by_internship(self.session, internship_id=internship_id)

    def search_by_status(
        self,
        employer_verification_status: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Verification]:
        return self.repo.search_by_status(
            self.session,
            employer_verification_status=employer_verification_status,
            skip=skip,
            limit=limit,
        )

    def update(
        self, verification_id: str, verification_in: VerificationUpdate
    ) -> Optional[Verification]:
        db_obj = self.repo.get(self.session, id=verification_id)
        if not db_obj:
            return None
        update_data = verification_in.model_dump(exclude_unset=True)
        return self.repo.update(self.session, db_obj=db_obj, obj_in=update_data)