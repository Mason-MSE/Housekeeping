from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from model.role import RoleModel
from schemas.role import RoleSchema, RoleCreateSchema, RoleUpdateSchema

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

class role_crud(CRUDBase[RoleModel, RoleCreateSchema, RoleUpdateSchema]):
    """
    Role CRUD class.

    Extends the generic CRUDBase class to perform
    database operations for the associated model.

    Override methods here if model-specific query
    behavior is required.
    """
    pass

