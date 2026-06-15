from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CleanerSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CleanerDetailSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    avatar: Optional[str] = None
    recent_reviews: List[dict] = []

    class Config:
        from_attributes = True


class PortalServiceTypeSchema(BaseModel):
    id: int
    type_name: str
    description: Optional[str] = None
    price: Optional[float] = None
    market_price: Optional[float] = None

    class Config:
        from_attributes = True


class PortalRoomSchema(BaseModel):
    room_id: int
    room_number: str
    room_type: str
    floor: int
    price: float
    status: int
    image_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PortalOrderCreateSchema(BaseModel):
    """Payload for portal ``Book now`` → ``service_order`` (home / on-site cleaning)."""

    model_config = ConfigDict(extra='ignore')

    service_type_id: int
    guest_name: str = Field(..., min_length=1, max_length=100)
    guest_phone: str = Field(..., min_length=1, max_length=30)
    guest_email: Optional[str] = Field(None, max_length=100)
    #: Where the cleaning should take place (maps to ``service_order.service_address``).
    service_address: str = Field(..., min_length=1, max_length=500)
    #: Preferred start (maps to ``scheduled_start``). Accepts ISO or ``YYYY-MM-DD HH:mm:ss`` from Element Plus.
    scheduled_time: datetime
    #: Estimated job length in hours (default 2); used only when ``scheduled_end`` is not sent.
    scheduled_duration_hours: float = Field(2.0, ge=0.5, le=24.0)
    remarks: Optional[str] = Field(None, max_length=500)
    cleaner_id: Optional[int] = None
    requirement_id: Optional[int] = None
    #: 0 normal, 1 urgent, 2 emergency (aligns with ``service_order.priority``).
    priority: int = Field(0, ge=0, le=2)

    @field_validator('scheduled_time', mode='before')
    @classmethod
    def parse_scheduled_time(cls, value: Any) -> datetime:
        """Coerce JSON strings from the Vue date picker into ``datetime``."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                raise ValueError('scheduled_time is required')
            normalized = text.replace('Z', '+00:00')
            try:
                return datetime.fromisoformat(normalized.replace(' ', 'T', 1))
            except ValueError:
                pass
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    continue
            raise ValueError('Invalid scheduled_time; use ISO or YYYY-MM-DD HH:mm:ss')
        raise ValueError('scheduled_time must be a string or datetime')

    @field_validator('guest_email', mode='before')
    @classmethod
    def empty_guest_email_as_none(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator('cleaner_id', 'requirement_id', mode='before')
    @classmethod
    def optional_int_ids(cls, value: Any) -> Optional[int]:
        if value is None or value == '':
            return None
        if isinstance(value, bool):
            raise ValueError('Invalid id value')
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return None
            if s.isdigit():
                return int(s)
        raise ValueError('Invalid id value')

    @field_validator('service_type_id', 'priority', mode='before')
    @classmethod
    def coerce_required_ints(cls, value: Any) -> Any:
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @field_validator('scheduled_duration_hours', mode='before')
    @classmethod
    def coerce_duration_hours(cls, value: Any) -> Any:
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return value
            try:
                return float(s)
            except ValueError as exc:
                raise ValueError('scheduled_duration_hours must be a number') from exc
        return value


class PortalOrderSchema(BaseModel):
    order_id: int
    order_no: str
    status: int
    service_type_name: Optional[str] = None
    room_number: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    create_time: datetime
    price: Optional[float] = None
    actual_price: Optional[float] = None
    service_address: Optional[str] = None
    priority: Optional[int] = None

    class Config:
        from_attributes = True


class ServiceTypeDetailSchema(BaseModel):
    type_id: int
    type_name: str
    description: Optional[str] = None
    price: float
    market_price: Optional[float] = None
    features: List[str] = []
    process_steps: List[dict] = []
    precautions: List[str] = []

    class Config:
        from_attributes = True


class CompanyInfoSchema(BaseModel):
    about_us: str = "CleanPro is a professional hotel cleaning service platform"
    phone: str = "400-888-8888"
    email: str = "service@cleanpro.com"
    address: str = "Pudong New District, Shanghai"
    facebook: str = ""
    twitter: str = ""
    instagram: str = ""

    class Config:
        from_attributes = True


class ReviewSchema(BaseModel):
    id: int
    guest_name: str
    rating: float
    comment: str
    service_type_name: Optional[str] = None
    create_time: str

    class Config:
        from_attributes = True


class CustomerRequirementCustomerCreateSchema(BaseModel):
    """Logged-in customer creates a requirement from the management module."""

    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    guest_address: Optional[str] = None
    property_type: str
    bedroom: int = 1
    bathroom: int = 1
    living_room: int = 1
    kitchen: int = 1
    lawn: int = 0
    car_space: int = 0
    square_footage: Optional[float] = None
    service_type_name: Optional[str] = None
    preferred_time: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    publish_to_portal: bool = True


class CustomerRequirementSchema(BaseModel):
    id: int
    user_id: Optional[int] = None
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    guest_address: Optional[str] = None
    property_type: str
    bedroom: int
    bathroom: int
    living_room: int
    kitchen: int
    lawn: int
    car_space: int
    square_footage: Optional[float] = None
    service_type_name: Optional[str] = None
    preferred_time: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    status: int
    is_published: int = 1
    publish_time: Optional[str] = None
    create_time: str

    class Config:
        from_attributes = True


class CleanerApplicationCreateSchema(BaseModel):
    requirement_id: int
    cleaner_id: int
    cleaner_name: str
    offered_price: Optional[float] = None
    message: Optional[str] = None


class CleanerApplicationSchema(BaseModel):
    id: int
    requirement_id: int
    cleaner_id: int
    cleaner_name: str
    offered_price: Optional[float] = None
    message: Optional[str] = None
    status: int
    star_level: Optional[int] = None
    total_orders: Optional[int] = None
    total_rating: Optional[float] = None
    create_time: str

    class Config:
        from_attributes = True


class CleanerTaskSchema(BaseModel):
    id: int
    task_type: str
    task_id: int
    title: str
    description: Optional[str] = None
    status: int
    status_text: str
    price: Optional[float] = None
    create_time: str
    update_time: Optional[str] = None

    class Config:
        from_attributes = True


class AdminRequirementSchema(BaseModel):
    id: int
    user_id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    property_type: str
    bedroom: int
    bathroom: int
    living_room: int
    kitchen: int
    lawn: int
    car_space: int
    square_footage: Optional[float] = None
    service_type_name: Optional[str] = None
    preferred_time: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    status: int
    create_time: str
    applications_count: int = 0
    accepted_cleaner_id: Optional[int] = None
    accepted_cleaner_name: Optional[str] = None
    assigned_cleaner_id: Optional[int] = None
    assigned_cleaner_username: Optional[str] = None
    assigned_cleaner_full_name: Optional[str] = None
    can_reassign_cleaner: bool = True
    service_order_status: Optional[int] = None

    class Config:
        from_attributes = True


class AdminCleanerSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    pending_tasks: int = 0
    completed_tasks: int = 0

    class Config:
        from_attributes = True
