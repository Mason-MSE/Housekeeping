from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    """Schema representing basic user information returned after login."""
    id: int
    username: str
    roles: list[str] = []
    full_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    """Schema representing an authentication token response."""
    access_token: str
    token_type: str
    requires_2fa: Optional[bool] = False
    user_info: Optional[UserInfo] = None

class LoginRequest(BaseModel):
    """Schema for login request with email and password."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Schema for user registration requests."""
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    enable_2fa: bool = False
    role: str = 'guest'


class TwoFactorResponse(BaseModel):
    """Schema for two-factor authentication challenge response."""
    requires_2fa: bool
    temp_token: Optional[str] = None
    qr_code: Optional[str] = None
    message: Optional[str] = None


class LoginRequestJSON(BaseModel):
    """Schema for JSON-based login request with username and password."""
    username: str
    password: str


class LoginWith2FARequest(BaseModel):
    """Schema for login requests that include a two-factor authentication code."""
    username: str
    password: str
    code: str
