"""CompanySignal service — business logic for company signals."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.company_signal import CompanySignal
from app.db.repositories.company_signal_repository import CompanySignalRepository
from app.schemas.company_signal import CompanySignalCreate, CompanySignalUpdate

logger = get_logger(__name__)


class CompanySignalService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CompanySignalRepository(session)

    def create(self, signal_in: CompanySignalCreate) -> CompanySignal:
        signal = self.repo.create(self.session, obj_in=signal_in.model_dump())
        logger.info(
            "Company signal created",
            company_id=str(signal.company_id),
            signal_type=signal.signal_type,
        )
        return signal

    def get_by_company(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CompanySignal]:
        return self.repo.get_by_company(
            self.session, company_id=company_id, skip=skip, limit=limit
        )

    def count_by_company(self, company_id: UUID) -> int:
        return self.repo.count_by_company(self.session, company_id=company_id)

    def update(
        self, signal_id: str, signal_in: CompanySignalUpdate
    ) -> Optional[CompanySignal]:
        db_obj = self.repo.get(self.session, id=signal_id)
        if not db_obj:
            return None
        update_data = signal_in.model_dump(exclude_unset=True)
        return self.repo.update(self.session, db_obj=db_obj, obj_in=update_data)