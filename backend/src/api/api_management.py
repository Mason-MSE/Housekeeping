from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from database import get_db
from model.api import ApiModel
from model.permission import PermissionModel
from model.user import UserModel


router = APIRouter(prefix='/api/rbac', tags=['api-management'])


@router.get('/permissions/options')
def list_permission_options(
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    """
    Return active permissions for API binding dropdowns.

    Separate from GET /api/permissions so API Management works without permission:view.
    """
    perms = (
        db.query(PermissionModel)
        .filter(PermissionModel.is_deleted == 0)
        .order_by(PermissionModel.permission_code)
        .all()
    )
    return [
        {
            'id': p.id,
            'permission_name': p.permission_name,
            'permission_code': p.permission_code,
        }
        for p in perms
    ]


class ApiSchema(BaseModel):
    """Schema for API create/update request payload."""
    id: Optional[int] = None
    api_path: Optional[str] = None
    api_method: Optional[str] = None
    permission_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


@router.get('/apis')
def get_all_apis(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    method: Optional[str] = None,
    permission_id: Optional[int] = None,
    api_path: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get APIs with pagination and filters"""
    query = db.query(ApiModel).filter(ApiModel.is_deleted == 0)
    
    if method:
        query = query.filter(ApiModel.api_method == method.upper())
    
    if permission_id:
        query = query.filter(ApiModel.permission_id == permission_id)
    
    if api_path:
        query = query.filter(ApiModel.api_path.like(f'%{api_path}%'))
    
    total = query.count()
    
    items = query.order_by(ApiModel.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size
    }


@router.post('/apis')
def create_api(api_data: ApiSchema, db: Session = Depends(get_db)):
    """Create a new API"""
    api = ApiModel(
        api_path=api_data.api_path,
        api_method=api_data.api_method,
        permission_id=api_data.permission_id,
        description=api_data.description
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    return {'success': True, 'id': api.id}


@router.put('/apis/{api_id}')
def update_api(api_id: int, api_data: ApiSchema, db: Session = Depends(get_db)):
    """Update an API"""
    api = db.query(ApiModel).filter(ApiModel.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail='API not found')
    
    if api_data.api_path:
        api.api_path = api_data.api_path
    if api_data.api_method:
        api.api_method = api_data.api_method
    if api_data.permission_id:
        api.permission_id = api_data.permission_id
    if api_data.description:
        api.description = api_data.description
    
    db.commit()
    return {'success': True}


@router.delete('/apis/{api_id}')
def delete_api(api_id: int, db: Session = Depends(get_db)):
    """Delete an API"""
    api = db.query(ApiModel).filter(ApiModel.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail='API not found')
    
    api.is_deleted = 1
    db.commit()
    return {'success': True}
