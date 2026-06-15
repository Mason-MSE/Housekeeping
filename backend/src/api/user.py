from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_permission, require_role, get_service
from database import get_db
from service.user import UserService
from model.user import UserModel
from schemas.housekeeping import (
    AdminUserCreateSchema,
    UserSchema,
    UserCreateSchema,
    UserUpdateSchema,
)



class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str


router = APIRouter(prefix='/api/user', tags=['user'])
public_router = APIRouter(prefix='/api/user', tags=['user'])


@router.get('/', response_model=List[UserSchema])
def read_all(
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    return service.get_all()


@router.get('/{id}', response_model=UserSchema)
def read_item(
    id: int,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj


@public_router.post('/', response_model=UserSchema)
def create_item(
    item_in: UserCreateSchema,
    service: UserService = Depends(get_service(UserService))
):
    return service.create(item_in)


@router.post('/manage', response_model=UserSchema)
def create_managed_user(
    item_in: AdminUserCreateSchema,
    current_user: UserModel = Depends(
        require_role('admin', 'manager', 'administrator', 'Administrator')
    ),
    service: UserService = Depends(get_service(UserService)),
):
    """Create a user from admin User Management (authenticated)."""
    try:
        return service.create_managed(item_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put('/{id}', response_model=UserSchema)
def update_item(
    id: int,
    item_in: UserUpdateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService)),
):
    if item_in.status is not None and item_in.status != 1 and id == current_user.id:
        raise HTTPException(status_code=400, detail='Cannot disable your own account')
    db_obj = service.update(id, item_in)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj


@router.delete('/{id}')
def delete_item(
    id: int,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService)),
):
    if id == current_user.id:
        raise HTTPException(status_code=400, detail='Cannot delete your own account')
    result = service.delete(id)
    if not result:
        raise HTTPException(status_code=404, detail='Item not found')
    return result


@router.get('/role/{role}', response_model=List[UserSchema])
def get_users_by_role(
    role: str,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    return service.get_by_role(role)


@router.get('/me/2fa-status')
def get_2fa_status(
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee"))
):
    """Get current user's 2FA status"""
    return {
        "is_2fa_enabled": current_user.is_2fa_enabled == 1,
        "has_secret": bool(current_user.totp_secret)
    }


@router.post('/change-password')
def change_password(
    data: ChangePasswordSchema,
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee")),
    service: UserService = Depends(get_service(UserService))
):
    """Change current user's password"""
    result = service.change_password(current_user.id, data.old_password, data.new_password)
    
    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    
    return result


@router.post('/me/enable-2fa')
def enable_2fa(
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee"))
):
    """Generate QR code for enabling 2FA"""
    from service.auth import AuthService
    
    db = next(get_db())
    auth_service = AuthService(db)
    result = auth_service.enable_2fa(current_user.id)
    
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    
    return result


@router.post('/me/verify-2fa')
def verify_and_enable_2fa(
    code: str,
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee"))
):
    """Verify 2FA code and enable 2FA"""
    from service.auth import AuthService
    
    db = next(get_db())
    auth_service = AuthService(db)
    result = auth_service.verify_and_enable_2fa(current_user.id, code)
    
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    
    return result


@router.post('/me/disable-2fa')
def disable_2fa(
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee"))
):
    """Disable 2FA for current user"""
    from datetime import datetime
    
    db = next(get_db())
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    
    if user:
        user.is_2fa_enabled = 0
        user.totp_secret = None
        user.modify_time = datetime.now()
        db.commit()
    
    return {"success": True, "message": "2FA disabled successfully"}


@router.get('/me/permissions')
def get_user_permissions(
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee")),
    db: Session = Depends(get_db)
):
    """Get current user's permissions"""
    from model.role import RoleModel
    from model.role_permission import RolePermissionModel
    from model.permission import PermissionModel
    from model.user_role import UserRoleModel
    
    role_ids = db.query(UserRoleModel.role_id).filter(
        UserRoleModel.user_id == current_user.id,
        UserRoleModel.is_deleted == 0
    ).all()
    role_ids = [r[0] for r in role_ids]
    
    role_names = db.query(RoleModel.role_name).filter(
        RoleModel.id.in_(role_ids)
    ).all() if role_ids else []
    roles = [r[0] for r in role_names]
    
    if not role_ids:
        return {"roles": roles, "permissions": []}
    
    perms = db.query(PermissionModel).join(
        RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id
    ).filter(
        RolePermissionModel.role_id.in_(role_ids),
        RolePermissionModel.is_deleted == 0,
        PermissionModel.is_deleted == 0
    ).distinct().all()
    
    return {
        "roles": roles,
        "permissions": [
            {
                "id": p.id,
                "permission_code": p.permission_code,
                "permission_name": p.permission_name
            }
            for p in perms
        ]
    }


@router.get('/me/role-resources')
def get_user_role_resources(
    current_user: UserModel = Depends(require_role("administrator", "admin", "manager", "guest", "cleaner", "staff", "employee")),
    db: Session = Depends(get_db)
):
    """Get current user's role resources - DEPRECATED, use /me/permissions instead"""
    return get_user_permissions(current_user, db)


class UpdateUserRolesSchema(BaseModel):
    role_ids: List[int]


@router.post('/{user_id}/roles')
def update_user_roles(
    user_id: int,
    data: UpdateUserRolesSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    from model.user_role import UserRoleModel
    
    db.query(UserRoleModel).filter(UserRoleModel.user_id == user_id).delete()
    
    for role_id in data.role_ids:
        user_role = UserRoleModel(user_id=user_id, role_id=role_id)
        db.add(user_role)
    
    db.commit()
    return {"message": "User roles updated successfully"}
