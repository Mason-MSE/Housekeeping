from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Optional, Generic, TypeVar, List
from pydantic.generics import GenericModel

from schemas.user import UserSchema


class PaginationRequest(BaseModel):
    """
    Generic pagination request schema.
    """
    page: int = 1  # Number of records to skip (offset)
    page_size: int = 10  # Maximum number of records to return
    filters: Optional[Dict[str, Any]] = None  # e.g., {"status": 1}
    order_by: Optional[str] = None  # e.g., "start_date desc"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "filters": {"status": 3},
                "order_by": "create_time desc"
            }
        })


T = TypeVar("T")  # Generic type for data list

class PaginationResponse(GenericModel, Generic[T]):
    """
    Generic response schema for paginated results.
    """
    total_records: int  # total number of records in database
    total_pages: int  # total number of pages
    current_page: int  # current page number
    page_size: int  # number of items per page
    data: List[T]  # list of items for current page