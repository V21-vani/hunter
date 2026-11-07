"""Base repository with common CRUD operations."""

from typing import TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base
from app.schemas.common import PaginationParams

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository:
    """Base repository providing CRUD operations for any SQLAlchemy model."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get(self, id: str) -> ModelType | None:
        from uuid import UUID
        return self.session.query(self.model).filter(self.model.id == UUID(id)).first()

    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        return session.query(self.model).offset(skip).limit(limit).all()

    def create(self, session: Session, *, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self, session: Session, *, db_obj: ModelType, obj_in: dict
    ) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, *, id: str) -> bool:
        from uuid import UUID
        obj = session.query(self.model).filter(self.model.id == UUID(id)).first()
        if obj:
            session.delete(obj)
            session.commit()
            return True
        return False

    def count(self, session: Session) -> int:
        return session.query(self.model).count()