"""Company service — business logic for companies."""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.company import Company
from app.db.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate

logger = get_logger(__name__)


class CompanyService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CompanyRepository(session)

    def create_or_get(self, company_in: CompanyCreate) -> Company:
        company = self.repo.create_or_get_by_name(self.session, company_in=company_in)
        logger.info("Company created or retrieved", name=company.name, id=str(company.id))
        return company

    def get(self, company_id: str) -> Optional[Company]:
        return self.repo.get(self.session, id=company_id)

    def search(
        self,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        verification_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Company]:
        return self.repo.search(
            self.session,
            query=query,
            industry=industry,
            verification_status=verification_status,
            skip=skip,
            limit=limit,
        )

    def count_search(
        self,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> int:
        return self.repo.count_search(
            self.session,
            query=query,
            industry=industry,
            verification_status=verification_status,
        )

    def update(self, company_id: str, company_in: CompanyUpdate) -> Optional[Company]:
        db_obj = self.repo.get(self.session, id=company_id)
        if not db_obj:
            return None
        update_data = company_in.model_dump(exclude_unset=True)
        return self.repo.update(self.session, db_obj=db_obj, obj_in=update_data)