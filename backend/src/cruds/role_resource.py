from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from model.role_resource import RoleResourceModel
from schemas.role_resource import RoleResourceSchema, RoleResourceCreateSchema, RoleResourceUpdateSchema

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

class role_resource_crud(CRUDBase[RoleResourceModel, RoleResourceCreateSchema, RoleResourceUpdateSchema]):
    """
    Role_resource CRUD class.

    Extends the generic CRUDBase class to perform
    database operations for the associated model.

    Override methods here if model-specific query
    behavior is required.
    """
    pass

