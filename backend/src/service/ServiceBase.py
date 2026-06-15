from typing import Generic, Type, TypeVar, Optional, Dict, Any, Tuple, List

from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from cruds.CRUDBase import CRUDBase

from database import get_db

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ServiceBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Service layer with auto DB injection, pagination, sorting, batch operations
    """
    def __init__(self, crud: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType], db: Session):
        self.crud = crud
        self.db = db

    # CRUD
    def get_all(self) -> List[ModelType]:
        return self.crud.get_all(self.db)

    def get(self, id: int) -> Optional[ModelType]:
        return self.crud.get(self.db, id)

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        return self.crud.create(self.db, obj_in)

    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        return self.crud.update(self.db, db_obj, obj_in)

    def delete(self, db_obj: ModelType) -> bool:
        return self.crud.delete(self.db, db_obj)

    def soft_delete(self, db_obj: ModelType) -> bool:
        return self.crud.soft_delete(self.db, db_obj)

    # Pagination
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Tuple[int, List[ModelType]]:
        if page < 1:
            page = 1
        skip = (page - 1) * page_size
        total, data = self.crud.get_multi(
            session=self.db,
            skip=skip,
            limit=page_size,
            filters=filters,
            order_by=order_by
        )
        return total, data

    # Batch operations
    def batch_soft_delete(self, objects: List[ModelType]) -> int:
        return self.crud.batch_soft_delete(self.db, objects)

    def batch_update(self, objects: List[ModelType], update_data: Dict[str, Any]) -> int:
        return self.crud.batch_update(self.db, objects, update_data)

    @staticmethod
    def get_crud(crud_cls: Type[CRUDBase], model_cls: Type) -> CRUDBase:
        return crud_cls(model_cls)
