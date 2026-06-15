from fastapi import Depends
from sqlalchemy.orm import Session

from service.ServiceBase import ServiceBase
from model.user_role import UserRoleModel
from cruds.user_role import user_role_crud
from schemas.user_role import UserRoleSchema, UserRoleCreateSchema, UserRoleUpdateSchema


# --------------------------------------------------
# Service Layer
# --------------------------------------------------
# This service layer handles business logic for the model.
# It wraps the CRUD layer and can be extended with
# custom validation, permission checks, or other
# domain-specific logic.

class user_role(ServiceBase[UserRoleModel, UserRoleCreateSchema, UserRoleUpdateSchema]):
    """
    User_role service class.

    Inherits from ServiceBase to reuse generic CRUD
    operations such as create, read, update, delete,
    and pagination.

    Override methods here to implement custom
    business logic for this model.
    """
    def __init__(self, db: Session):
        crud_instance = super().get_crud(crud_cls=user_role_crud, model_cls=UserRoleModel)
        super().__init__(crud=crud_instance, db=db)
