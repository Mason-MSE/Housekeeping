from pydantic import BaseModel,Field
from datetime import datetime, date, time
from typing import Optional

class UserSchema(BaseModel):
    """Schema representing a user."""
    id: Optional[int] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[int] = None
    totp_secret: Optional[str] = None
    is_2fa_enabled: Optional[int] = None
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

class UserCreateSchema(BaseModel):
    """Schema for creating a new user."""
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[int] = 1
    enable_2fa: Optional[bool] = False

    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    """Schema for updating an existing user."""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True


