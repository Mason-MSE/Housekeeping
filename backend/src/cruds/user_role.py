from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from model.user_role import UserRoleModel
from schemas.user_role import UserRoleSchema, UserRoleCreateSchema, UserRoleUpdateSchema

# --------------------------------------------------
# CRUD Layer
# --------------------------------------------------
# This class provides database-level operations
# for the corresponding model.
# It inherits common CRUD methods from CRUDBase:
# - get
# - get_all
# - create
# - update
# - delete
# - soft_delete
# - get_multi (pagination & filtering)

class user_role_crud(CRUDBase[UserRoleModel, UserRoleCreateSchema, UserRoleUpdateSchema]):
    """
    User_role CRUD class.

    Extends the generic CRUDBase class to perform
    database operations for the associated model.

    Override methods here if model-specific query
    behavior is required.
    """
    pass

