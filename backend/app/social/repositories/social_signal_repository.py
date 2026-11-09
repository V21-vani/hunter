"""SocialSignal repository — CRUD and queries for social signals."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.social_signal import SocialSignal
from app.db.repositories.base_repository import BaseRepository
from app.social.models.social_signal import SocialSignal as SocialSignalModel


class SocialSignalRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, SocialSignalModel)

    def get_by_post_url(self, session: Session, *, post_url: str) -> Optional[SocialSignalModel]:
        """Get a signal by its unique post URL."""
        return (
            session.query(SocialSignalModel).filter(SocialSignalModel.post_url == post_url).first()
        )

    def get_by_platform_and_post_id(self, session: Session, *, platform: str, post_id: str) -> Optional[SocialSignalModel]:
        """Get a signal by platform and post ID."""
        return (
            session.query(SocialSignalModel)
            .filter(SocialSignalModel.platform == platform, SocialSignalModel.post_id == post_id)
            .first()
        )

    def get_by_company(self, session: Session, *, company: str, limit: int = 50) -> list[SocialSignalModel]:
        """Retrieve signals by company name (case-insensitive)."""
        return (
            session.query(SocialSignalModel)
            .filter(SocialSignalModel.company.ilike(f"%{company}%"))
            .order_by(SocialSignalModel.post_date.desc())
            .limit(limit)
            .all()
        )

    def search(self, session: Session, *, query: str = "", limit: int = 20):
        """Full-text search across social signals."""
        q = session.query(SocialSignalModel)
        if query:
            q = q.filter(
                SocialSignalModel.post_text.ilike(f"%{query}%")
                | SocialSignalModel.company.ilike(f"%{query}%")
                | SocialSignalModel.author.ilike(f"%{query}%")
            )
        return q.order_by(SocialSignalModel.post_date.desc()).limit(limit).all()

    def count_by_platform(self, session: Session, *, platform: str) -> int:
        """Count signals by platform."""
        return session.query(SocialSignalModel).filter(
            SocialSignalModel.platform == platform
        ).count()

    def create(self, session: Session, obj_in: SocialSignalModel) -> SocialSignalModel:
        """Create a new social signal."""
        # Check for duplicate by post_url to prevent re-crawling
        existing = self.get_by_post_url(session, post_url=str(obj_in.post_url))
        if existing:
            return existing
        return super().create(session, obj_in=obj_in.model_dump())
