from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from core.dependencies import get_service
from service.auth import AuthService
from schemas.login import (


    RegisterRequest,
    TwoFactorResponse,
    Token,
    LoginRequestJSON,
    LoginWith2FARequest
)


auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=TwoFactorResponse)
def register(
    request: RegisterRequest,
    service: AuthService = Depends(get_service(AuthService)),
):
    from database import get_db
    from model.user import UserModel
    from model.role import RoleModel
    from model.user_role import UserRoleModel
    
    result = service.register(
        username=request.username,
        password=request.password,
        full_name=request.full_name,
        email=request.email,
        enable_2fa=request.enable_2fa,
        role=request.role
    )

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    
    # Ensure user_role is added
    db = next(get_db())
    user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if user:
        existing = db.query(UserRoleModel).filter(UserRoleModel.user_id == user.id).first()
        if not existing:
            role_obj = db.query(RoleModel).filter(RoleModel.role_name == request.role).first()
            if role_obj:
                user_role = UserRoleModel(user_id=user.id, role_id=role_obj.id)
                db.add(user_role)
                db.commit()
                print(f"API: Added user_role for {request.username}")

    return TwoFactorResponse(**result)


@auth_router.post("/verify-2fa")
def verify_2fa(
    username: str,
    code: str,
    role: str = 'guest',
    service: AuthService = Depends(get_service(AuthService)),
):
    from database import get_db
    from model.user import UserModel
    from model.role import RoleModel
    from model.user_role import UserRoleModel
    
    result = service.verify_2fa(username=username, code=code)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    # Ensure user_role is added after 2FA verification
    db = next(get_db())
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user:
        existing = db.query(UserRoleModel).filter(UserRoleModel.user_id == user.id).first()
        if not existing:
            role_obj = db.query(RoleModel).filter(RoleModel.role_name == role).first()
            if role_obj:
                user_role = UserRoleModel(user_id=user.id, role_id=role_obj.id)
                db.add(user_role)
                db.commit()
                print(f"API: Added user_role for {username} after 2FA verification")

    return result


@auth_router.post("/login", response_model=Token)
def login(
    data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_service(AuthService)),
):
    result = service.login(username=data.username, password=data.password)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return Token(**result)


@auth_router.post("/login/json", response_model=Token)
def login_json(
    request: LoginRequestJSON,
    service: AuthService = Depends(get_service(AuthService)),
):
    result = service.login(username=request.username, password=request.password)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return Token(**result)


@auth_router.post("/login-with-2fa")
def login_with_2fa(
    request: LoginWith2FARequest,
    service: AuthService = Depends(get_service(AuthService)),
):
    result = service.login_with_2fa(
        username=request.username,
        password=request.password,
        code=request.code
    )

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result
