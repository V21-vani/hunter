"""CompanySignal repository — CRUD and queries for company signals."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.company_signal import CompanySignal
from app.db.repositories.base_repository import BaseRepository
from app.schemas.company_signal import CompanySignalCreate, CompanySignalUpdate


class CompanySignalRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, CompanySignal)

    def get_by_company(
        self,
        session: Session,
        *,
        company_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CompanySignal]:
        return (
            session.query(CompanySignal)
            .filter(CompanySignal.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_company(self, session: Session, *, company_id: UUID) -> int:
        return session.query(CompanySignal).filter(
            CompanySignal.company_id == company_id
        ).count()