from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from model.resource import ResourceModel
from schemas.resource import ResourceSchema, ResourceCreateSchema, ResourceUpdateSchema

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

class resource_crud(CRUDBase[ResourceModel, ResourceCreateSchema, ResourceUpdateSchema]):
    """
    Resource CRUD class.

    Extends the generic CRUDBase class to perform
    database operations for the associated model.

    Override methods here if model-specific query
    behavior is required.
    """
    pass

