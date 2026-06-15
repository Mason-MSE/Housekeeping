from cruds.CRUDBase import CRUDBase
from model.booking import BookingModel
from schemas.booking import BookingCreateSchema, BookingUpdateSchema

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

class booking_crud(CRUDBase[BookingModel, BookingCreateSchema, BookingUpdateSchema]):
    """
    Booking CRUD class.

    Extends the generic CRUDBase class to perform
    database operations for the associated model.

    Override methods here if model-specific query
    behavior is required.
    """
    pass


