# Standard library imports
import re
from typing import Optional

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from cruds.role import role_crud
from model.role import RoleModel
from model.user_role import UserRoleModel
from schemas.role import RoleCreateSchema, RoleUpdateSchema
from service.ServiceBase import ServiceBase


class role(ServiceBase[RoleModel, RoleCreateSchema, RoleUpdateSchema]):
    """Role service: CRUD with unique role_code and safe soft-delete."""

    def __init__(self, db: Session):
        crud_instance = super().get_crud(crud_cls=role_crud, model_cls=RoleModel)
        super().__init__(crud=crud_instance, db=db)

    def get_all(self):
        return self.crud.get_all(self.db)

    def get(self, id: int) -> Optional[RoleModel]:
        return self.crud.get(self.db, id)

    @staticmethod
    def _slug_code(name: str) -> str:
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')
        return slug or 'role'

    def _unique_role_code(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """Return True if ``code`` is free among non-deleted roles."""
        query = self.db.query(RoleModel).filter(
            RoleModel.role_code == code,
            RoleModel.is_deleted == 0,
        )
        if exclude_id is not None:
            query = query.filter(RoleModel.id != exclude_id)
        return query.first() is None

    def create(self, item_in: RoleCreateSchema) -> RoleModel:
        data = item_in.model_dump(exclude_unset=True)
        name = (data.get('role_name') or '').strip()
        if not name:
            raise ValueError('role_name is required')
        code = (data.get('role_code') or '').strip()
        if not code:
            code = self._slug_code(name)
        if not self._unique_role_code(code):
            raise ValueError('role_code already exists')
        desc = data.get('description')
        if desc is not None:
            desc = str(desc).strip()[:255] or None
        obj = RoleModel(
            role_name=name[:50],
            role_code=code[:50],
            description=desc,
            is_deleted=0,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: RoleModel, item_in: RoleUpdateSchema) -> RoleModel:
        data = item_in.model_dump(exclude_unset=True)
        if 'role_name' in data and data['role_name'] is not None:
            nm = str(data['role_name']).strip()
            if not nm:
                raise ValueError('role_name cannot be empty')
            db_obj.role_name = nm[:50]
        if 'role_code' in data and data['role_code'] is not None:
            code = str(data['role_code']).strip()
            if not code:
                raise ValueError('role_code cannot be empty')
            if not self._unique_role_code(code[:50], exclude_id=db_obj.id):
                raise ValueError('role_code already exists')
            db_obj.role_code = code[:50]
        if 'description' in data:
            raw = data['description']
            if raw is None or raw == '':
                db_obj.description = None
            else:
                db_obj.description = str(raw).strip()[:255] or None
        if 'is_deleted' in data and data['is_deleted'] is not None:
            db_obj.is_deleted = int(data['is_deleted'])
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: RoleModel) -> bool:
        """Soft-delete if no active user assignments."""
        assigned = (
            self.db.query(UserRoleModel)
            .filter(
                UserRoleModel.role_id == db_obj.id,
                UserRoleModel.is_deleted == 0,
            )
            .count()
        )
        if assigned > 0:
            raise ValueError('Cannot delete role while it is assigned to users')
        return self.soft_delete(db_obj)
