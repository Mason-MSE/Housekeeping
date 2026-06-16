from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import mapped_column

from model.Base import Base


class InventoryItemModel(Base):
    """Inventory item/consumable record mapped to the 'inventory_item' table."""
    __tablename__ = 'inventory_item'

    id = mapped_column(Integer, primary_key=True)
    item_name = mapped_column(String(100), nullable=False)
    category = mapped_column(String(50), nullable=True)
    quantity = mapped_column(Integer, nullable=True)
    min_stock = mapped_column(Integer, nullable=True)
    unit = mapped_column(String(20), nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
