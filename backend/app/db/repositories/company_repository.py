"""Company repository — CRUD and queries for companies."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.company import Company
from app.db.repositories.base_repository import BaseRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Company)

    def get_by_name(self, session: Session, *, name: str) -> Optional[Company]:
        return session.query(Company).filter(Company.name == name).first()

    def get_by_website(self, session: Session, *, website: str) -> Optional[Company]:
        return session.query(Company).filter(Company.website == website).first()

    def create_or_get_by_name(
        self, session: Session, *, company_in: CompanyCreate
    ) -> Company:
        """Duplicate prevention: return existing company by name or create new."""
        existing = self.get_by_name(session, name=company_in.name)
        if existing:
            return existing
        return self.create(session, obj_in=company_in.model_dump())

    def search(
        self,
        session: Session,
        *,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        verification_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Company]:
        q = session.query(Company)
        if query:
            search = f"%{query}%"
            q = q.filter(Company.name.ilike(search))
        if industry:
            q = q.filter(Company.industry == industry)
        if verification_status:
            q = q.filter(Company.verification_status == verification_status)
        return q.offset(skip).limit(limit).all()

    def count_search(
        self,
        session: Session,
        *,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> int:
        q = session.query(Company)
        if query:
            search = f"%{query}%"
            q = q.filter(Company.name.ilike(search))
        if industry:
            q = q.filter(Company.industry == industry)
        if verification_status:
            q = q.filter(Company.verification_status == verification_status)
        return q.count()