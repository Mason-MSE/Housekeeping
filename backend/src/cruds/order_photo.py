from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from model.service_order import OrderPhotoModel
from schemas.housekeeping import OrderPhotoSchema, OrderPhotoCreateSchema
from typing import Optional


class OrderPhotoCRUD(CRUDBase[OrderPhotoModel, OrderPhotoCreateSchema, dict]):
    """CRUD class for order photo operations, inheriting from CRUDBase."""
    pass


order_photo_crud = OrderPhotoCRUD(OrderPhotoModel)


class OrderPhotoService:
    """Service layer for order photo operations, wrapping OrderPhotoCRUD with additional logic."""
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db

    def get_all(self):
        """Retrieve all order photos."""
        return order_photo_crud.get_all(self.db)

    def get(self, id: int):
        """Retrieve a single order photo by its ID."""
        return order_photo_crud.get(self.db, id)

    def get_by_order(self, order_id: int):
        """Retrieve all photos for a given order, sorted by sort_order."""
        return self.db.query(OrderPhotoModel).filter(
            OrderPhotoModel.order_id == order_id,
            OrderPhotoModel.is_deleted == 0
        ).order_by(OrderPhotoModel.sort_order.asc()).all()

    def create(self, obj_in: OrderPhotoCreateSchema, uploaded_by: int):
        """Create a new order photo record with sort order auto-assigned."""
        data = obj_in.dict()
        data['uploaded_by'] = uploaded_by

        max_order = self.db.query(OrderPhotoModel).filter(
            OrderPhotoModel.order_id == obj_in.order_id,
            OrderPhotoModel.photo_type == obj_in.photo_type,
            OrderPhotoModel.is_deleted == 0
        ).count()
        data['sort_order'] = max_order

        obj = OrderPhotoModel(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int):
        """Soft-delete an order photo by its ID and return True if successful."""
        db_obj = order_photo_crud.get(self.db, id)
        if not db_obj:
            return False
        return order_photo_crud.soft_delete(self.db, db_obj)
