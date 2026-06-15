"""CRUD for cleaning service types (portal + billing)."""
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from model.service_type import ServiceTypeModel


class ServiceTypeService:
    """Maintain service_type rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self):
        """All non-deleted types, stable order."""
        return (
            self.db.query(ServiceTypeModel)
            .filter(ServiceTypeModel.is_deleted == 0)
            .order_by(ServiceTypeModel.id.asc())
            .all()
        )

    def get(self, type_id: int) -> Optional[ServiceTypeModel]:
        """Fetch one by primary key ``id``."""
        return (
            self.db.query(ServiceTypeModel)
            .filter(ServiceTypeModel.id == type_id, ServiceTypeModel.is_deleted == 0)
            .first()
        )

    def create(
        self,
        type_name: str,
        description: Optional[str] = None,
        price: float = 0,
        market_price: Optional[float] = None,
    ) -> ServiceTypeModel:
        """Insert a new service type."""
        item = ServiceTypeModel(
            type_name=type_name,
            description=description,
            price=price,
            market_price=market_price,
            is_deleted=0,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, type_id: int, item_in: Dict[str, Any]) -> Optional[ServiceTypeModel]:
        """Patch allowed fields."""
        item = (
            self.db.query(ServiceTypeModel)
            .filter(ServiceTypeModel.id == type_id, ServiceTypeModel.is_deleted == 0)
            .first()
        )
        if not item:
            return None
        allowed = {'type_name', 'description', 'price', 'market_price'}
        for key, value in item_in.items():
            if key in allowed and hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, type_id: int) -> Optional[ServiceTypeModel]:
        """Soft delete."""
        item = (
            self.db.query(ServiceTypeModel)
            .filter(ServiceTypeModel.id == type_id, ServiceTypeModel.is_deleted == 0)
            .first()
        )
        if not item:
            return None
        item.is_deleted = 1
        self.db.commit()
        self.db.refresh(item)
        return item
