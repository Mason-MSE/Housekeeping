from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    id: int
    username: str
    roles: list[str] = []
    full_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: Optional[bool] = False
    user_info: Optional[UserInfo] = None

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    enable_2fa: bool = False
    role: str = 'guest'


class TwoFactorResponse(BaseModel):
    requires_2fa: bool
    temp_token: Optional[str] = None
    qr_code: Optional[str] = None
    message: Optional[str] = None


class LoginRequestJSON(BaseModel):
    username: str
    password: str


class LoginWith2FARequest(BaseModel):
    username: str
    password: str
    code: str
