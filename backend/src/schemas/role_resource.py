from pydantic import BaseModel,Field, constr
from datetime import datetime, date, time
from typing import Optional

class RoleResourceSchema(BaseModel):
    """Schema representing a role-resource association."""
    id: Optional[int] = None
    role_id: Optional[int] = None
    resource_id: Optional[int] = None
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

class RoleResourceCreateSchema(BaseModel):
    """Schema for creating a new role-resource association."""
    id: int
    role_id: Optional[int] = None
    resource_id: Optional[int] = None
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True

class RoleResourceUpdateSchema(BaseModel):
    """Schema for updating an existing role-resource association."""
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True
