"""Source service — business logic for sources."""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.source import Source
from app.db.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreate, SourceUpdate

logger = get_logger(__name__)


class SourceService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SourceRepository(session)

    def create_or_get(self, source_in: SourceCreate) -> Source:
        source = self.repo.create_or_get_by_url(self.session, source_in=source_in)
        logger.info("Source created or retrieved", url=str(source_in.original_source_url))
        return source

    def get(self, source_id: str) -> Optional[Source]:
        return self.repo.get(self.session, id=source_id)

    def search(
        self,
        source_type: Optional[str] = None,
        platform: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Source]:
        return self.repo.search(
            self.session,
            source_type=source_type,
            platform=platform,
            skip=skip,
            limit=limit,
        )

    def count_search(
        self,
        source_type: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> int:
        return self.repo.count_search(
            self.session, source_type=source_type, platform=platform
        )

    def update(self, source_id: str, source_in: SourceUpdate) -> Optional[Source]:
        db_obj = self.repo.get(self.session, id=source_id)
        if not db_obj:
            return None
        update_data = source_in.model_dump(exclude_unset=True)
        return self.repo.update(self.session, db_obj=db_obj, obj_in=update_data)