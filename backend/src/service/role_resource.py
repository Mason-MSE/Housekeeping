from fastapi import Depends
from sqlalchemy.orm import Session

from service.ServiceBase import ServiceBase
from model.role_resource import RoleResourceModel
from cruds.role_resource import role_resource_crud
from schemas.role_resource import RoleResourceSchema, RoleResourceCreateSchema, RoleResourceUpdateSchema


# --------------------------------------------------
# Service Layer
# --------------------------------------------------
# This service layer handles business logic for the model.
# It wraps the CRUD layer and can be extended with
# custom validation, permission checks, or other
# domain-specific logic.

class role_resource(ServiceBase[RoleResourceModel, RoleResourceCreateSchema, RoleResourceUpdateSchema]):
    """
    Role_resource service class.

    Inherits from ServiceBase to reuse generic CRUD
    operations such as create, read, update, delete,
    and pagination.

    Override methods here to implement custom
    business logic for this model.
    """
    def __init__(self, db: Session):
        crud_instance = super().get_crud(crud_cls=role_resource_crud, model_cls=RoleResourceModel)
        super().__init__(crud=crud_instance, db=db)
