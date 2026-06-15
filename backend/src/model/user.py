from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from passlib.context import CryptContext

from model.Base import Base



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    totp_secret: Mapped[str] = mapped_column(String(32), nullable=True)
    is_2fa_enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    star_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=5.0)
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    languages: Mapped[str] = mapped_column(String(200), nullable=True)
    bio: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    creator: Mapped[int] = mapped_column(Integer, nullable=True)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    modifier: Mapped[int] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __mapper_args__ = {
        "eager_defaults": True
    }

    def set_password(self, raw_password: str):
        self.password = pwd_context.hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password)
