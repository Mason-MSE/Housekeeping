from fastapi import Depends
from sqlalchemy.orm import Session

from cruds.booking import booking_crud
from service.ServiceBase import ServiceBase
from model.booking import BookingModel
from schemas.booking import BookingCreateSchema, BookingUpdateSchema


# --------------------------------------------------
# Service Layer
# --------------------------------------------------
# This service layer handles business logic for the model.
# It wraps the CRUD layer and can be extended with
# custom validation, permission checks, or other
# domain-specific logic.

class booking(ServiceBase[BookingModel, BookingCreateSchema, BookingUpdateSchema]):
    """
    Booking service class.

    Inherits from ServiceBase to reuse generic CRUD
    operations such as create, read, update, delete,
    and pagination.

    Override methods here to implement custom
    business logic for this model.
    """
    def __init__(self,db:Session):
        crud_instance = super().get_crud(crud_cls=booking_crud,model_cls=BookingModel)
        super().__init__(crud=crud_instance,db=db)




