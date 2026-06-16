# Standard library imports
from typing import Optional, Type, TypeVar

# Third-party imports
from fastapi import Depends, HTTPException, Request, status
from fastapi.routing import compile_path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

# Local application imports
from core.security import decode_access_token
from database import get_db
from model.user import UserModel
from model.api import ApiModel
from model.permission import PermissionModel
from model.role_permission import RolePermissionModel
from model.user_role import UserRoleModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
optional_http_bearer = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_http_bearer),
    db: Session = Depends(get_db),
) -> Optional[UserModel]:
    """Return the logged-in user when ``Authorization: Bearer`` is valid; otherwise ``None``."""
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        username: Optional[str] = payload.get("sub")
    except JWTError:
        return None
    if not username:
        return None
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    if user.is_deleted is not None and user.is_deleted != 0:
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    """FastAPI dependency that returns the authenticated user from the JWT token, or raises 401."""
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------------- Permission checker ----------------
def require_permission():
    """
    Dependency to check if current user has permission for this request
    Uses api table and permission system
    """
    def checker(request: Request, current_user: UserModel = Depends(get_current_user),
                db: Session = Depends(get_db)):
        path = request.url.path.rstrip('/')
        method = request.method.upper()

        # Get user roles
        role_ids = db.query(UserRoleModel.role_id).filter(
            UserRoleModel.user_id == current_user.id,
            UserRoleModel.is_deleted == 0
        ).all()
        role_ids = [r[0] for r in role_ids]

        if not role_ids:
            raise HTTPException(status_code=403, detail="No roles assigned")

        # Get permissions for user's roles
        permission_ids = db.query(RolePermissionModel.permission_id).filter(
            RolePermissionModel.role_id.in_(role_ids),
            RolePermissionModel.is_deleted == 0
        ).distinct().all()
        permission_ids = [p[0] for p in permission_ids]

        if not permission_ids:
            raise HTTPException(status_code=403, detail="No permissions assigned")

        # Get APIs that require these permissions
        apis = db.query(ApiModel.api_path, ApiModel.api_method).filter(
            ApiModel.permission_id.in_(permission_ids),
            ApiModel.is_deleted == 0
        ).all()
        
        print(f"User '{current_user.username}' with roles {role_ids} has permissions {permission_ids} for APIs: {apis}")
        print(f"Checking access for path '{path}' and method '{method}'")
        # Check if current path + method matches any API
        for api_path, api_method in apis:
            path_regex, _, _ = compile_path(api_path)
            if path_regex.match(path) and api_method.upper() == method.upper():
                return current_user

        # Deny if no match
        raise HTTPException(status_code=403, detail="Permission denied")
    return checker


def require_role(*allowed_roles: str):
    """
    Dependency to check if current user has one of the allowed roles.
    Usage: require_role("admin"), require_role("admin", "cleaner")
    """
    def role_checker(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
        from model.role import RoleModel
        from model.user_role import UserRoleModel
        
        roles = db.query(RoleModel.role_name).join(
            UserRoleModel, UserRoleModel.role_id == RoleModel.id
        ).filter(UserRoleModel.user_id == current_user.id).all()
        user_roles = [r[0].lower() for r in roles] if roles else []
        
        allowed_roles_lower = [r.lower() for r in allowed_roles]
        
        if not any(user_role in allowed_roles_lower for user_role in user_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker



S = TypeVar("S")

def get_service(service_cls: Type[S]):
    """FastAPI dependency factory that instantiates and injects a service class with a DB session."""
    def _get_service(db: Session = Depends(get_db)) -> S:
        return service_cls(db=db)
    return _get_service


# C = TypeVar("C",bound=CRUDBase)
# def get_crud(crud_cls: Type[C], model_cls):
#     def _get_crud(db: Session = Depends(get_db)) -> C:
#         return crud_cls(model_cls)
#     return _get_crud
