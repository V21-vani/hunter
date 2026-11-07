"""ScanLog repository — CRUD and queries for scan logs."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.scan_log import ScanLog
from app.db.repositories.base_repository import BaseRepository
from app.schemas.scan_log import ScanLogCreate, ScanLogUpdate


class ScanLogRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, ScanLog)

    def get_by_source_scanned(
        self,
        session: Session,
        *,
        source_scanned: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ScanLog]:
        return (
            session.query(ScanLog)
            .filter(ScanLog.source_scanned == source_scanned)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_scan_log(
        self, session: Session, *, scan_in: ScanLogCreate
    ) -> ScanLog:
        return self.create(session, obj_in=scan_in.model_dump())

    def complete_scan(
        self,
        session: Session,
        *,
        scan_id: UUID,
        end_time,
        jobs_discovered: int,
        jobs_new: int,
        jobs_updated: int,
        errors: Optional[str] = None,
        rate_limited: bool = False,
        status: str = "completed",
    ) -> Optional[ScanLog]:
        scan = self.get(session, id=str(scan_id))
        if scan:
            scan.end_time = end_time
            scan.jobs_discovered = jobs_discovered
            scan.jobs_new = jobs_new
            scan.jobs_updated = jobs_updated
            scan.errors = errors
            scan.rate_limited = rate_limited
            scan.status = status
            session.commit()
            session.refresh(scan)
            return scan
        return None