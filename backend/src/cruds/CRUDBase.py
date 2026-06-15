
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Type
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError


from database import get_db

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model
        pk_list = model.__mapper__.primary_key
        if not pk_list:
            raise RuntimeError(f"{model.__name__} has no primary key")
        self.pk_column = pk_list[0]
        self.has_soft_delete = hasattr(model, "is_deleted")

    def _base_query(self, session: Session):
        query = session.query(self.model)
        if self.has_soft_delete:
            query = query.filter(self.model.is_deleted == 0)
        return query

    def get_all(self, session:Session):
        return self._base_query(session).all()

    def get(self, session: Session, id: int):
        return (
            self._base_query(session)
            .filter(self.pk_column == id)
            .first()
        )

    def get_by(self, session: Session, **kwargs):
        return (
            self._base_query(session)
            .filter_by(**kwargs)
            .first()
        )

    def get_multi(self, session: Session, skip: int = 0, limit: int = 10, **filters):
        query = self._base_query(session)

        if filters:
            query = query.filter_by(**filters)

        total_count = query.count()
        data = query.offset(skip).limit(limit).all()
        return total_count, data

    def create(self, session: Session, obj_in: CreateSchemaType):
        obj = self.model(**obj_in.dict())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def update(self, session: Session, db_obj: ModelType, obj_in: UpdateSchemaType):
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, db_obj: ModelType):
        session.delete(db_obj)
        session.commit()
        return True

    def soft_delete(self, session: Session, db_obj: ModelType):
        if hasattr(db_obj, "is_deleted"):
            db_obj.is_deleted = 1
        session.commit()
        session.refresh(db_obj)
        return True

    def get_paginated(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Tuple[int, List[ModelType]]:

        query = self._base_query(session)

        if filters:
            for field, value in filters.items():
                if value is None or value == '':
                    continue
                if hasattr(self.model, field):
                    col = getattr(self.model, field)
                    if isinstance(value, str) and field in ['room_number', 'room_type', 'description']:
                        query = query.filter(col.like(f'%{value}%'))
                    else:
                        query = query.filter(col == value)

        if order_by:
            parts = order_by.strip().split()
            field_name = parts[0]
            direction = parts[1].lower() if len(parts) > 1 else "asc"

            if hasattr(self.model, field_name):
                col = getattr(self.model, field_name)
                query = query.order_by(col.asc() if direction == "asc" else col.desc())

        total_count = query.count()
        data = query.offset(skip).limit(limit).all()
        return total_count, data

    def batch_soft_delete(self, session: Session, objects: List[ModelType]) -> int:
        count = 0
        try:
            for obj in objects:
                if hasattr(obj, "is_deleted"):
                    obj.is_deleted = 1
                    count += 1
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        return count

    def batch_update(self, session: Session, objects: List[ModelType], update_data: Dict[str, Any]) -> int:
        count = 0
        try:
            for obj in objects:
                for field, value in update_data.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
                count += 1
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        return count
