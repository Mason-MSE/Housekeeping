import base64
import io

from sqlalchemy.orm import Session

from model.user import UserModel
from model.role import RoleModel
from model.user_role import UserRoleModel
from core.security import create_access_token

import pyotp
import qrcode


class AuthService:
    def __init__(self, db: Session):
        """Initialize the auth service with a database session."""
        self.db = db

    def _get_user_roles(self, user_id: int) -> list[str]:
        """Return a list of role codes for the given user."""
        roles = self.db.query(RoleModel.role_code).join(
            UserRoleModel, UserRoleModel.role_id == RoleModel.id
        ).filter(UserRoleModel.user_id == user_id).all()
        return [r[0] for r in roles] if roles else []

    def register(self, username: str, password: str, full_name: str = None, email: str = None, enable_2fa: bool = False, role: str = 'guest'):
        """Register a new user account, optionally enabling 2FA."""
        existing_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if existing_user:
            return {"error": "Username already exists", "status_code": 400}

        valid_roles = ['guest', 'cleaner']
        if role not in valid_roles:
            role = 'guest'

        user = UserModel(
            username=username,
            password=password,
            full_name=full_name or username,
            email=email,
            status=1
        )
        user.set_password(password)

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            role_obj = self.db.query(RoleModel).filter(RoleModel.role_name == role).first()
            if role_obj:
                user_role = UserRoleModel(user_id=user.id, role_id=role_obj.id)
                self.db.add(user_role)
                self.db.commit()
            else:
                print(f"ERROR: Role '{role}' not found in database!")
        except Exception as e:
            print(f"Error in register: {e}")
            self.db.rollback()

        if enable_2fa:
            totp_secret = pyotp.random_base32()
            user.totp_secret = totp_secret
            user.is_2fa_enabled = 1
            self.db.commit()

            totp = pyotp.TOTP(totp_secret)
            provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Housekeeping")

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return {
                "requires_2fa": True,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "message": "Please scan the QR code with your authenticator app and verify with a code"
            }
        else:
            token = create_access_token(subject=user.username)
            return {
                "requires_2fa": False,
                "temp_token": token,
                "message": "Registration successful"
            }

    def verify_2fa(self, username: str, code: str):
        """Verify a 2FA code and return an access token on success."""
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "Invalid credentials", "status_code": 401}

        if not user.totp_secret or not user.is_2fa_enabled:
            return {"error": "Invalid credentials", "status_code": 401}

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(code):
            return {"error": "Invalid credentials", "status_code": 401}

        if getattr(user, "status", 1) != 1:
            return {"error": "Invalid credentials", "status_code": 401}

        token = create_access_token(subject=user.username)
        roles = self._get_user_roles(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "roles": roles,
                "full_name": user.full_name,
                "email": user.email
            }
        }

    def login(self, username: str, password: str):
        """Authenticate a user and return an access token or prompt for 2FA."""
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.password.startswith('$2b$'):
            if not user.verify_password(password):
                return {"error": "Invalid credentials", "status_code": 401}
        else:
            if user.password != password:
                return {"error": "Invalid credentials", "status_code": 401}

        if getattr(user, "status", 1) != 1:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.is_2fa_enabled and user.totp_secret:
            return {
                "access_token": create_access_token(subject=f"{user.username}_2fa"),
                "token_type": "bearer",
                "requires_2fa": True
            }

        token = create_access_token(subject=user.username)
        roles = self._get_user_roles(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "roles": roles,
                "full_name": user.full_name,
                "email": user.email
            }
        }

    def login_with_2fa(self, username: str, password: str, code: str):
        """Authenticate with password and 2FA code in a single step."""
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.password.startswith('$2b$'):
            if not user.verify_password(password):
                return {"error": "Invalid credentials", "status_code": 401}
        else:
            if user.password != password:
                return {"error": "Invalid credentials", "status_code": 401}

        if getattr(user, "status", 1) != 1:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.is_2fa_enabled and user.totp_secret:
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(code):
                return {"error": "Invalid credentials", "status_code": 401}

        token = create_access_token(subject=user.username)
        roles = self._get_user_roles(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "roles": roles,
                "full_name": user.full_name,
                "email": user.email
            }
        }

    def enable_2fa(self, user_id: int):
        """Generate QR code for enabling 2FA"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return {"error": "User not found", "status_code": 404}
        
        if user.is_2fa_enabled == 1:
            return {"error": "2FA is already enabled", "status_code": 400}
        
        # Generate new TOTP secret
        totp_secret = pyotp.random_base32()
        user.totp_secret = totp_secret
        self.db.commit()
        
        # Generate QR code
        totp = pyotp.TOTP(totp_secret)
        provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="CleanPro")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "success": True,
            "qr_code": f"data:image/png;base64,{qr_code_base64}",
            "secret": totp_secret,
            "message": "Please scan the QR code with your authenticator app and verify with a code"
        }

    def verify_and_enable_2fa(self, user_id: int, code: str):
        """Verify 2FA code and enable 2FA"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return {"error": "User not found", "status_code": 404}
        
        if not user.totp_secret:
            return {"error": "Please generate QR code first", "status_code": 400}
        
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(code):
            return {"error": "Invalid verification code", "status_code": 400}
        
        user.is_2fa_enabled = 1
        self.db.commit()
        
        return {
            "success": True,
            "message": "2FA enabled successfully"
        }
