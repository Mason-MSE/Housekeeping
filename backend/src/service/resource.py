from fastapi import Depends
from sqlalchemy.orm import Session

from service.ServiceBase import ServiceBase
from model.resource import ResourceModel
from cruds.resource import resource_crud
from schemas.resource import ResourceSchema, ResourceCreateSchema, ResourceUpdateSchema


# --------------------------------------------------
# Service Layer
# --------------------------------------------------
# This service layer handles business logic for the model.
# It wraps the CRUD layer and can be extended with
# custom validation, permission checks, or other
# domain-specific logic.

class resource(ServiceBase[ResourceModel, ResourceCreateSchema, ResourceUpdateSchema]):
    """
    Resource service class.

    Inherits from ServiceBase to reuse generic CRUD
    operations such as create, read, update, delete,
    and pagination.

    Override methods here to implement custom
    business logic for this model.
    """
    def __init__(self, db: Session):
        crud_instance = super().get_crud(crud_cls=resource_crud, model_cls=ResourceModel)
        super().__init__(crud=crud_instance, db=db)
