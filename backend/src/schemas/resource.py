from pydantic import BaseModel,Field, constr
from datetime import datetime, date, time
from typing import Optional

class ResourceSchema(BaseModel):
    """Schema representing a resource (API endpoint)."""
    id: Optional[int] = None
    resource_name: Optional[str] = Field(None, max_length=100)
    resource_link: Optional[str] = Field(None, max_length=255)
    resource_method: Optional[str] = Field(None, max_length=10)
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,
            date: lambda v: v.strftime('%Y-%m-%d') if v else None,
            time: lambda v: v.strftime('%H:%M:%S') if v else None,
        }

class ResourceCreateSchema(BaseModel):
    """Schema for creating a new resource."""
    id: int
    resource_name: Optional[str] = Field(None, max_length=100)
    resource_link: Optional[str] = Field(None, max_length=255)
    resource_method: Optional[str] = Field(None, max_length=10)
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True

class ResourceUpdateSchema(BaseModel):
    """Schema for updating an existing resource."""
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True
