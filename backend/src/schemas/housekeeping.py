from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, computed_field, field_serializer


class UserSchema(BaseModel):
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: int = 1
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    roles: Optional[list] = []

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class AdminUserCreateSchema(BaseModel):
    """Admin-only user creation with optional initial roles."""

    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: int = 1
    role_ids: List[int] = []


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[int] = None
    password: Optional[str] = None


class RoomSchema(BaseModel):
    room_id: Optional[int] = None
    room_number: str
    floor: int
    room_type: str
    capacity: int = 2
    price: float
    status: int = 0
    last_clean_time: Optional[datetime] = None
    description: Optional[str] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomCreateSchema(BaseModel):
    room_number: str
    floor: int
    room_type: str
    capacity: int = 2
    price: float
    description: Optional[str] = None


class RoomUpdateSchema(BaseModel):
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[int] = None
    description: Optional[str] = None


class ServiceTypeSchema(BaseModel):
    """API shape for service_type; ``type_id`` mirrors ``id`` for legacy clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type_name: str
    description: Optional[str] = None
    price: Optional[float] = None
    market_price: Optional[float] = None

    @computed_field
    @property
    def type_id(self) -> int:
        return self.id


class ServiceTypeCreateSchema(BaseModel):
    type_name: str
    description: Optional[str] = None
    price: float = 0
    market_price: Optional[float] = None


class ServiceOrderSchema(BaseModel):
    order_id: Optional[int] = None
    order_no: Optional[str] = None
    requirement_id: Optional[int] = None
    room_id: int
    guest_id: int
    service_type_id: int
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None
    status: int = 0
    priority: int = 0
    request_time: datetime
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_complete: Optional[datetime] = None
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None
    remarks: Optional[str] = None
    rating: Optional[int] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceOrderCreateSchema(BaseModel):
    requirement_id: Optional[int] = None
    room_id: int
    service_type_id: int
    priority: int = 0
    request_time: datetime
    remarks: Optional[str] = None


class ServiceOrderUpdateSchema(BaseModel):
    assigned_staff_id: Optional[int] = None
    status: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_complete: Optional[datetime] = None
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None
    remarks: Optional[str] = None


class OrderPhotoSchema(BaseModel):
    id: Optional[int] = None
    order_id: int
    photo_type: str
    photo_url: str
    description: Optional[str] = None
    uploaded_by: Optional[int] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderPhotoCreateSchema(BaseModel):
    order_id: int
    photo_type: str
    photo_url: str
    description: Optional[str] = None


class InspectionSchema(BaseModel):
    inspection_id: Optional[int] = None
    order_id: int
    inspector_id: int
    cleaner_id: int
    status: int = 0
    score: Optional[int] = None
    issues: Optional[str] = None
    inspection_time: datetime

    class Config:
        from_attributes = True


class InventoryItemSchema(BaseModel):
    item_id: Optional[int] = None
    item_name: str
    category: str
    quantity: int
    min_stock: int
    unit: str
    location: Optional[str] = None
    is_active: int = 1

    class Config:
        from_attributes = True


class InventoryItemCreateSchema(BaseModel):
    item_name: str
    category: str
    quantity: int = 0
    min_stock: int = 10
    unit: str
    location: Optional[str] = None


class ReviewSchema(BaseModel):
    review_id: Optional[int] = None
    order_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewCreateSchema(BaseModel):
    order_id: int
    rating: int
    comment: Optional[str] = None


class NotificationSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    content: Optional[str] = None
    type: str = 'info'
    link_url: Optional[str] = None
    is_read: int = 0
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationCreateSchema(BaseModel):
    user_id: int
    title: str
    content: Optional[str] = None
    type: str = 'info'
    link_url: Optional[str] = None


class WalletSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    balance: float
    frozen_balance: float

    class Config:
        from_attributes = True


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    wallet_id: int
    order_id: Optional[int] = None
    user_id: int
    type: str
    amount: Optional[float] = None
    status: str
    description: Optional[str] = None
    create_time: Optional[datetime] = None

    @field_serializer('create_time')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime('%Y-%m-%d %H:%M:%S')


class RechargeSchema(BaseModel):
    amount: float


class RateSchema(BaseModel):
    rating: float
    comment: Optional[str] = None


class ReorderSchema(BaseModel):
    photo_ids: list[int]


class PaymentSchema(BaseModel):
    order_id: int
    payment_method: str = 'online'


class OrderReviewSchema(BaseModel):
    order_id: int
    rating: float
    comment: Optional[str] = None
