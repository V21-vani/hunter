"""Source repository — CRUD and queries for sources."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.source import Source
from app.db.repositories.base_repository import BaseRepository
from app.schemas.source import SourceCreate, SourceUpdate


class SourceRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Source)

    def get_by_url(
        self, session: Session, *, original_source_url: str
    ) -> Optional[Source]:
        return (
            session.query(Source)
            .filter(Source.original_source_url == original_source_url)
            .first()
        )

    def create_or_get_by_url(
        self, session: Session, *, source_in: SourceCreate
    ) -> Source:
        """Duplicate prevention: return existing source by URL or create new."""
        existing = self.get_by_url(session, original_source_url=str(source_in.original_source_url))
        if existing:
            return existing
        return self.create(session, obj_in=source_in.model_dump())

    def search(
        self,
        session: Session,
        *,
        source_type: Optional[str] = None,
        platform: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Source]:
        q = session.query(Source)
        if source_type:
            q = q.filter(Source.source_type == source_type)
        if platform:
            q = q.filter(Source.platform == platform)
        return q.offset(skip).limit(limit).all()

    def count_search(
        self,
        session: Session,
        *,
        source_type: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> int:
        q = session.query(Source)
        if source_type:
            q = q.filter(Source.source_type == source_type)
        if platform:
            q = q.filter(Source.platform == platform)
        return q.count()