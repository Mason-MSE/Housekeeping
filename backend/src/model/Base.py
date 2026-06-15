from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  event




class Base(DeclarativeBase):
    pass

@event.listens_for(Base, "before_insert", propagate=True)
def base_before_insert(mapper, connection, target):
    if hasattr(target, "create_time"):
        target.create_time = datetime.now()
    if hasattr(target, "modify_time"):
        target.modify_time = datetime.now()


@event.listens_for(Base, "before_update", propagate=True)
def base_before_update(mapper, connection, target):
    if hasattr(target, "modify_time"):
        target.modify_time = datetime.now()