from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_permission
from database import get_db
from model.user import UserModel
from model.permission import PermissionModel
from model.menu import MenuModel
from model.role import RoleModel
from model.role_permission import RolePermissionModel
from model.user_role import UserRoleModel
from model.role_menu import RoleMenuModel


router = APIRouter(prefix='/api', tags=['rbac'])


class PermissionSchema(BaseModel):
    id: Optional[int] = None
    permission_code: str
    permission_name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PermissionCreateSchema(BaseModel):
    """Payload for creating a permission."""

    permission_code: str
    permission_name: str
    description: Optional[str] = None


class PermissionUpdateSchema(BaseModel):
    """Payload for updating a permission (partial)."""

    permission_code: Optional[str] = None
    permission_name: Optional[str] = None
    description: Optional[str] = None


class MenuSchema(BaseModel):
    id: Optional[int] = None
    menu_name: str
    path: Optional[str] = None
    component: Optional[str] = None
    parent_id: int = 0
    sort: int = 0
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class MenuCreateSchema(BaseModel):
    """Payload for creating a menu."""

    menu_name: str
    path: Optional[str] = None
    component: Optional[str] = None
    parent_id: int = 0
    sort: int = 0
    icon: Optional[str] = None


class MenuUpdateSchema(BaseModel):
    """Payload for updating a menu (partial)."""

    menu_name: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    parent_id: Optional[int] = None
    sort: Optional[int] = None
    icon: Optional[str] = None


class RoleSchema(BaseModel):
    id: Optional[int] = None
    role_name: str
    role_code: Optional[str] = None
    description: Optional[str] = None
    create_time: Optional[str] = None
    permissions: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class AssignPermissionsSchema(BaseModel):
    permission_ids: List[int]


class AssignMenusSchema(BaseModel):
    menu_ids: List[int]


@router.get('/permissions', response_model=List[PermissionSchema])
def get_all_permissions(
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Get all permissions (requires permission:view)."""
    permissions = db.query(PermissionModel).filter(PermissionModel.is_deleted == 0).all()
    return permissions


@router.get('/permissions/{perm_id}', response_model=PermissionSchema)
def get_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Get one permission by id (requires permission:view)."""
    perm = db.query(PermissionModel).filter(
        PermissionModel.id == perm_id,
        PermissionModel.is_deleted == 0,
    ).first()
    if not perm:
        raise HTTPException(status_code=404, detail='Permission not found')
    return perm


@router.post('/permissions', response_model=PermissionSchema)
def create_permission(
    data: PermissionCreateSchema,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Create a permission (requires permission:create)."""
    code = data.permission_code.strip()
    name = data.permission_name.strip()
    if not code or not name:
        raise HTTPException(status_code=400, detail='permission_code and permission_name are required')
    exists = db.query(PermissionModel).filter(
        PermissionModel.permission_code == code,
        PermissionModel.is_deleted == 0,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail='permission_code already exists')

    desc = data.description.strip() if data.description else None
    perm = PermissionModel(
        permission_code=code,
        permission_name=name,
        description=desc,
        is_deleted=0,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.put('/permissions/{perm_id}', response_model=PermissionSchema)
def update_permission(
    perm_id: int,
    data: PermissionUpdateSchema,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Update a permission (requires permission:update)."""
    perm = db.query(PermissionModel).filter(
        PermissionModel.id == perm_id,
        PermissionModel.is_deleted == 0,
    ).first()
    if not perm:
        raise HTTPException(status_code=404, detail='Permission not found')

    payload = data.model_dump(exclude_unset=True)
    if 'permission_code' in payload and payload['permission_code'] is not None:
        new_code = str(payload['permission_code']).strip()
        if not new_code:
            raise HTTPException(status_code=400, detail='permission_code cannot be empty')
        conflict = db.query(PermissionModel).filter(
            PermissionModel.permission_code == new_code,
            PermissionModel.is_deleted == 0,
            PermissionModel.id != perm_id,
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail='permission_code already in use')
        payload['permission_code'] = new_code

    if 'permission_name' in payload and payload['permission_name'] is not None:
        new_name = str(payload['permission_name']).strip()
        if not new_name:
            raise HTTPException(status_code=400, detail='permission_name cannot be empty')
        payload['permission_name'] = new_name

    if 'description' in payload and payload['description'] is not None:
        desc = str(payload['description']).strip()
        payload['description'] = desc or None

    for key, value in payload.items():
        setattr(perm, key, value)

    db.commit()
    db.refresh(perm)
    return perm


@router.delete('/permissions/{perm_id}')
def delete_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Soft-delete a permission and related role/menu links (requires permission:delete)."""
    perm = db.query(PermissionModel).filter(
        PermissionModel.id == perm_id,
        PermissionModel.is_deleted == 0,
    ).first()
    if not perm:
        raise HTTPException(status_code=404, detail='Permission not found')

    perm.is_deleted = 1
    db.query(RolePermissionModel).filter(
        RolePermissionModel.permission_id == perm_id,
        RolePermissionModel.is_deleted == 0,
    ).update({RolePermissionModel.is_deleted: 1}, synchronize_session=False)
    db.commit()
    return {'message': 'Permission deleted'}


@router.get('/menus', response_model=List[MenuSchema])
def get_all_menus(
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Get all active menus (requires menu:view)."""
    menus = db.query(MenuModel).filter(MenuModel.is_deleted == 0).order_by(MenuModel.sort).all()
    return menus


@router.post('/menus', response_model=MenuSchema)
def create_menu(
    data: MenuCreateSchema,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Create a menu (requires menu:create)."""
    name = data.menu_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail='menu_name is required')
    if data.path:
        exists = db.query(MenuModel).filter(
            MenuModel.path == data.path.strip(),
            MenuModel.is_deleted == 0,
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail='Path already in use')

    menu = MenuModel(
        menu_name=name,
        path=data.path.strip() if data.path else None,
        component=data.component.strip() if data.component else None,
        parent_id=data.parent_id,
        sort=data.sort,
        icon=data.icon.strip() if data.icon else None,
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


@router.put('/menus/{menu_id}', response_model=MenuSchema)
def update_menu(
    menu_id: int,
    data: MenuUpdateSchema,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Update a menu (requires menu:update)."""
    menu = db.query(MenuModel).filter(MenuModel.id == menu_id, MenuModel.is_deleted == 0).first()
    if not menu:
        raise HTTPException(status_code=404, detail='Menu not found')

    payload = data.model_dump(exclude_unset=True)
    if 'path' in payload and payload['path']:
        path_val = str(payload['path']).strip()
        conflict = db.query(MenuModel).filter(
            MenuModel.path == path_val,
            MenuModel.is_deleted == 0,
            MenuModel.id != menu_id,
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail='Path already in use')
        payload['path'] = path_val
    elif 'path' in payload and payload['path'] is not None:
        payload['path'] = str(payload['path']).strip() or None

    if 'menu_name' in payload and payload['menu_name'] is not None:
        stripped_name = str(payload['menu_name']).strip()
        if not stripped_name:
            raise HTTPException(status_code=400, detail='menu_name cannot be empty')
        payload['menu_name'] = stripped_name
    if 'component' in payload and payload['component'] is not None:
        comp = str(payload['component']).strip()
        payload['component'] = comp or None
    if 'icon' in payload and payload['icon'] is not None:
        ico = str(payload['icon']).strip()
        payload['icon'] = ico or None

    for key, value in payload.items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu


@router.delete('/menus/{menu_id}')
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_permission()),
):
    """Soft-delete a menu (requires menu:delete)."""
    menu = db.query(MenuModel).filter(MenuModel.id == menu_id, MenuModel.is_deleted == 0).first()
    if not menu:
        raise HTTPException(status_code=404, detail='Menu not found')

    menu.is_deleted = 1
    db.commit()
    return {'message': 'Menu deleted'}


@router.get('/roles', response_model=List[RoleSchema])
def get_all_roles(
    db: Session = Depends(get_db)
):
    """Get all roles"""
    roles = db.query(RoleModel).filter(RoleModel.is_deleted == 0).all()
    result = []
    for role in roles:
        perms = db.query(PermissionModel).join(
            RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id
        ).filter(
            RolePermissionModel.role_id == role.id,
            RolePermissionModel.is_deleted == 0,
            PermissionModel.is_deleted == 0,
        ).all()
        role_data = {
            'id': role.id,
            'role_name': role.role_name,
            'role_code': role.role_code,
            'description': role.description,
            'create_time': role.create_time.strftime('%Y-%m-%d %H:%M') if role.create_time else '',
            'permissions': [{'id': p.id, 'permission_name': p.permission_name, 'permission_code': p.permission_code} for p in perms]
        }
        result.append(role_data)
    return result


@router.get('/role/{role_id}/permissions')
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get permissions for a role"""
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    perms = db.query(PermissionModel).join(
        RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id
    ).filter(
        RolePermissionModel.role_id == role_id,
        RolePermissionModel.is_deleted == 0,
        PermissionModel.is_deleted == 0,
    ).all()

    return [{'id': p.id, 'permission_name': p.permission_name, 'permission_code': p.permission_code} for p in perms]


@router.post('/role/{role_id}/permissions')
def assign_permissions_to_role(
    role_id: int,
    data: AssignPermissionsSchema,
    db: Session = Depends(get_db)
):
    """Assign permissions to a role"""
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    db.query(RolePermissionModel).filter(RolePermissionModel.role_id == role_id).delete(synchronize_session=False)
    
    for permission_id in data.permission_ids:
        rp = RolePermissionModel(role_id=role_id, permission_id=permission_id)
        db.add(rp)
    
    db.commit()
    return {'message': 'Permissions assigned successfully'}


@router.get('/role/{role_id}/menus')
def get_role_menus(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get menus for a role"""
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    role_menus = db.query(RoleMenuModel).filter(
        RoleMenuModel.role_id == role_id,
        RoleMenuModel.is_deleted == 0
    ).all()
    
    menu_ids = [rm.menu_id for rm in role_menus]
    
    if not menu_ids:
        return []
    
    menus = db.query(MenuModel).filter(
        MenuModel.id.in_(menu_ids),
        MenuModel.is_deleted == 0
    ).order_by(MenuModel.sort).all()
    
    return [{'id': m.id, 'menu_name': m.menu_name, 'path': m.path, 'component': m.component, 'icon': m.icon} for m in menus]


@router.post('/role/{role_id}/menus')
def assign_menus_to_role(
    role_id: int,
    data: AssignMenusSchema,
    db: Session = Depends(get_db)
):
    """Assign menus to a role"""
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    db.query(RoleMenuModel).filter(RoleMenuModel.role_id == role_id).delete(synchronize_session=False)
    
    for menu_id in data.menu_ids:
        rm = RoleMenuModel(role_id=role_id, menu_id=menu_id)
        db.add(rm)
    
    db.commit()
    return {'message': 'Menus assigned successfully'}


@router.get('/my/menus')
def get_my_menus(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get menus for current user based on their roles"""
    user_roles = db.query(UserRoleModel).filter(
        UserRoleModel.user_id == current_user.id,
        UserRoleModel.is_deleted == 0
    ).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return []
    
    role_menus = db.query(RoleMenuModel).filter(
        RoleMenuModel.role_id.in_(role_ids),
        RoleMenuModel.is_deleted == 0
    ).all()
    
    menu_ids = list({rm.menu_id for rm in role_menus})
    
    if not menu_ids:
        return []
    
    menus = db.query(MenuModel).filter(
        MenuModel.id.in_(menu_ids),
        MenuModel.is_deleted == 0
    ).order_by(MenuModel.sort).all()
    
    return [{'id': m.id, 'menu_name': m.menu_name, 'path': m.path, 'component': m.component, 'icon': m.icon} for m in menus]


@router.get('/my/permissions')
def get_my_permissions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get permissions for current user based on their roles"""
    user_roles = db.query(UserRoleModel).filter(
        UserRoleModel.user_id == current_user.id,
        UserRoleModel.is_deleted == 0
    ).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return []
    
    perms = db.query(PermissionModel).join(
        RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id
    ).filter(
        RolePermissionModel.role_id.in_(role_ids),
        RolePermissionModel.is_deleted == 0,
        PermissionModel.is_deleted == 0
    ).distinct().all()
    
    return [{'id': p.id, 'permission_name': p.permission_name, 'permission_code': p.permission_code} for p in perms]
