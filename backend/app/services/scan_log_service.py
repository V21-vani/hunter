"""ScanLog service — business logic for scan logs."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.scan_log import ScanLog
from app.db.repositories.scan_log_repository import ScanLogRepository
from app.schemas.scan_log import ScanLogCreate, ScanLogUpdate

logger = get_logger(__name__)


class ScanLogService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ScanLogRepository(session)

    def create(self, scan_in: ScanLogCreate) -> ScanLog:
        scan = self.repo.create_scan_log(self.session, scan_in=scan_in)
        logger.info(
            "Scan log created",
            source=scan_in.source_scanned,
            id=str(scan.id),
        )
        return scan

    def complete_scan(
        self,
        scan_id: UUID,
        end_time: datetime,
        jobs_discovered: int,
        jobs_new: int,
        jobs_updated: int,
        errors: Optional[str] = None,
        rate_limited: bool = False,
        status: str = "completed",
    ) -> Optional[ScanLog]:
        scan = self.repo.complete_scan(
            self.session,
            scan_id=scan_id,
            end_time=end_time,
            jobs_discovered=jobs_discovered,
            jobs_new=jobs_new,
            jobs_updated=jobs_updated,
            errors=errors,
            rate_limited=rate_limited,
            status=status,
        )
        if scan:
            logger.info(
                "Scan log completed",
                source=scan.source_scanned,
                status=scan.status,
                jobs_discovered=scan.jobs_discovered,
            )
        return scan

    def get_by_source_scanned(
        self,
        source_scanned: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ScanLog]:
        return self.repo.get_by_source_scanned(
            self.session, source_scanned=source_scanned, skip=skip, limit=limit
        )