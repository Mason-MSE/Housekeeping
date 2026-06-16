from pydantic import BaseModel,Field, constr
from datetime import datetime, date, time
from typing import Optional

class UserRoleSchema(BaseModel):
    """Schema representing a user-role association."""
    user_id: Optional[int] = None
    role_id: Optional[int] = None
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

class UserRoleCreateSchema(BaseModel):
    """Schema for creating a new user-role association."""
    user_id: int
    role_id: int
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True

class UserRoleUpdateSchema(BaseModel):
    """Schema for updating an existing user-role association."""
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True
