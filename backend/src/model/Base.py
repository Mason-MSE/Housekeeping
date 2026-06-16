from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  event




class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""
    pass

@event.listens_for(Base, "before_insert", propagate=True)
def base_before_insert(mapper, connection, target):
    """Auto-set create_time and modify_time on insert for models that have those columns."""
    if hasattr(target, "create_time"):
        target.create_time = datetime.now()
    if hasattr(target, "modify_time"):
        target.modify_time = datetime.now()


@event.listens_for(Base, "before_update", propagate=True)
def base_before_update(mapper, connection, target):
    """Auto-update modify_time on update for models that have that column."""
    if hasattr(target, "modify_time"):
        target.modify_time = datetime.now()