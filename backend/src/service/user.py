from sqlalchemy.orm import Session

from cruds.CRUDBase import CRUDBase
from model.user import UserModel
from model.role import RoleModel
from model.user_role import UserRoleModel
from schemas.housekeeping import AdminUserCreateSchema, UserCreateSchema, UserUpdateSchema


class UserService:
    def __init__(self, db: Session):
        """Initialize the user service with a database session."""
        self.db = db
        self.crud = CRUDBase(UserModel)

    def _get_user_roles(self, user_id: int) -> list:
        """Return a list of role dicts for the given user."""
        roles = (
            self.db.query(RoleModel)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .filter(
                UserRoleModel.user_id == user_id,
                UserRoleModel.is_deleted == 0,
                RoleModel.is_deleted == 0,
            )
            .all()
        )
        return [{"id": r.id, "role_name": r.role_name} for r in roles]

    def _add_roles_to_user(self, user):
        """Attach role info to a single user object."""
        if user:
            user.roles = self._get_user_roles(user.id)
        return user

    def _add_roles_to_users(self, users):
        """Attach role info to a list of user objects."""
        for user in users:
            user.roles = self._get_user_roles(user.id)
        return users

    def get_all(self):
        """Retrieve all users with their roles."""
        users = self.crud.get_all(self.db)
        return self._add_roles_to_users(users)

    def get(self, id: int):
        """Retrieve a single user by ID with their roles."""
        user = self.crud.get(self.db, id)
        return self._add_roles_to_user(user)

    def create(self, item_in: UserCreateSchema):
        """Create a new user with a hashed password."""
        data = item_in.model_dump(exclude={"password"}, exclude_unset=True)
        user = UserModel(**data, status=1)
        user.set_password(item_in.password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_managed(self, item_in: AdminUserCreateSchema):
        """Create user from admin panel; assign roles. Raises ValueError on duplicate username."""
        exists = (
            self.db.query(UserModel)
            .filter(
                UserModel.username == item_in.username,
                UserModel.is_deleted == 0,
            )
            .first()
        )
        if exists:
            raise ValueError("Username already exists")
        raw = item_in.model_dump(exclude={"password", "role_ids"})
        status_val = int(raw.get("status", 1))
        user = UserModel(
            username=raw["username"],
            email=raw.get("email"),
            full_name=raw.get("full_name"),
            phone=raw.get("phone"),
            status=status_val,
        )
        user.set_password(item_in.password)
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        for role_id in item_in.role_ids or []:
            self.db.add(UserRoleModel(user_id=user.id, role_id=role_id))
        self.db.commit()
        self.db.refresh(user)
        return self._add_roles_to_user(user)

    def update(self, id: int, item_in: UserUpdateSchema):
        """Update a user's fields, including optional password change."""
        db_obj = self.crud.get(self.db, id)
        if not db_obj:
            return None
        update_data = item_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            pwd = update_data.pop("password")
            if pwd:
                db_obj.set_password(pwd)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._add_roles_to_user(db_obj)

    def delete(self, id: int):
        """Soft delete a user by their ID."""
        db_obj = self.crud.get(self.db, id)
        if not db_obj:
            return None
        self.crud.soft_delete(self.db, db_obj)
        return {'ok': True}

    def get_by_role(self, role: str):
        """Retrieve all users who have a specific role name."""
        role_obj = self.db.query(RoleModel).filter(RoleModel.role_name == role).first()
        if not role_obj:
            return []
        user_ids = self.db.query(UserRoleModel.user_id).filter(
            UserRoleModel.role_id == role_obj.id
        ).all()
        user_ids = [u[0] for u in user_ids]
        users = self.crud._base_query(self.db).filter(UserModel.id.in_(user_ids)).all()
        return self._add_roles_to_users(users)

    def change_password(self, user_id: int, old_password: str, new_password: str):
        """Verify the old password and update it to a new one."""
        user = self.crud.get(self.db, user_id)
        if not user:
            return {"error": "User not found", "status_code": 404}
        
        if user.password.startswith('$2') or user.password.startswith('$'):
            if not user.verify_password(old_password):
                return {"error": "Current password is incorrect", "status_code": 400}
        else:
            if user.password != old_password:
                return {"error": "Current password is incorrect", "status_code": 400}
        
        user.set_password(new_password)
        self.db.commit()
        return {"message": "Password changed successfully"}
