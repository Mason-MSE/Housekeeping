from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field


class RoleSchema(BaseModel):
    id: Optional[int] = None
    role_name: Optional[str] = Field(None, max_length=50)
    role_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Optional[List[dict]] = None
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


class RoleCreateSchema(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=50)
    role_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class RoleUpdateSchema(BaseModel):
    role_name: Optional[str] = Field(None, max_length=50)
    role_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_deleted: Optional[int] = None

    class Config:
        from_attributes = True
