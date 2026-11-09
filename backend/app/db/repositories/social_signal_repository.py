"""SocialSignal repository — CRUD and queries for social signals."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.social.models.social_signal import SocialSignal
from app.db.repositories.base_repository import BaseRepository


class SocialSignalRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, SocialSignal)

    def get_by_platform_and_post_id(
        self,
        session: Session,
        *,
        platform: str,
        post_id: str,
    ) -> Optional[SocialSignal]:
        return (
            session.query(SocialSignal)
            .filter(SocialSignal.platform == platform, SocialSignal.post_id == post_id)
            .first()
        )

    def get_by_company(
        self,
        session: Session,
        *,
        company: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SocialSignal]:
        return (
            session.query(SocialSignal)
            .filter(SocialSignal.company.ilike(f"%{company}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_signal_type(
        self,
        session: Session,
        *,
        signal_type: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SocialSignal]:
        return (
            session.query(SocialSignal)
            .filter(SocialSignal.signal_type == signal_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_platform(self, session: Session, *, platform: str) -> int:
        return session.query(SocialSignal).filter(
            SocialSignal.platform == platform
        ).count()