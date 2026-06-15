# Standard library imports
import random
import string
from datetime import datetime, timedelta
from typing import List, Optional

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from model.cleaner_application import CleanerApplicationModel
from model.customer_requirement import CustomerRequirementModel
from model.role import RoleModel
from model.service_order import ServiceOrderModel
from model.service_type import ServiceTypeModel
from model.service_detail import ServiceStepModel
from model.wallet import TransactionModel
from model.user import UserModel
from model.user_role import UserRoleModel
from service.order_payment_amount import resolve_guest_order_pay_amount
from service.in_app_notify import notify_user


class PortalService:
    """Service class for portal-related operations."""

    #: Only these service_order.status values allow changing ``assigned_staff_id`` (e.g. 2+=in progress / done / pay / review).
    _ORDER_STATUSES_ALLOW_REASSIGN_STAFF = frozenset({0, 1})

    def _service_type_id_for_requirement(self, requirement: CustomerRequirementModel) -> int:
        """Resolve ``service_type.id`` from requirement's type id or name."""
        if requirement.service_type_id:
            row = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.id == requirement.service_type_id
            ).first()
            if row and (row.is_deleted is None or row.is_deleted == 0):
                return row.id
        if requirement.service_type_name:
            row = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.type_name == requirement.service_type_name
            ).first()
            if row and (row.is_deleted is None or row.is_deleted == 0):
                return row.id
        return 1

    def __init__(self, db: Session):
        """Initialize the service with database session."""
        self.db = db

    @staticmethod
    def _decode_rating(stored_rating: Optional[int]) -> Optional[float]:
        """Decode stored rating value to user-facing star value.

        Legacy values: 1..5
        New encoded values: rating * 10 (e.g. 1.5 -> 15)
        """
        if stored_rating is None:
            return None
        if stored_rating > 5:
            return round(stored_rating / 10, 1)
        return float(stored_rating)

    @staticmethod
    def _user_display_name(user: Optional[UserModel]) -> str:
        """Prefer ``username``, fall back to ``full_name`` for list/detail labels."""
        if user is None:
            return ''
        uname = (user.username or '').strip()
        if uname:
            return uname
        return (user.full_name or '').strip()

    def _order_pay_amount_for_guest(self, order: ServiceOrderModel, guest_id: int) -> float:
        """Amount the guest would pay (requirement budget first; see order_payment_amount)."""
        return float(resolve_guest_order_pay_amount(self.db, order, guest_id))

    # pylint: disable=too-many-branches
    def get_all_service_types(self) -> List[ServiceTypeModel]:
        """Get all active service types.

        Returns:
            List of active ServiceTypeModel objects.
        """
        return self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.is_deleted == 0
        ).all()

    def get_service_type_detail(self, type_id: int) -> dict:
        """Get service type detail with features, process steps, precautions.

        Args:
            type_id: The ID of the service type.

        Returns:
            Dictionary containing service type details.
        """
        service = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.id == type_id,
            ServiceTypeModel.is_deleted == 0
        ).first()

        if not service:
            return {
                'type_id': type_id,
                'type_name': 'Service',
                'description': 'Service details',
                'standard_time': 30,
                'price': 0,
                'market_price': None,
                'icon': 'House',
                'features': ['Professional service'],
                'process_steps': [],
                'precautions': ['Follow guidelines']
            }

        service_steps = self.db.query(ServiceStepModel).filter(
            ServiceStepModel.service_type_id == type_id,
            ServiceStepModel.is_deleted == 0
        ).order_by(ServiceStepModel.step_number).all()

        process_steps = []
        if service_steps:
            for step in service_steps:
                process_steps.append({
                    'step_number': step.step_number,
                    'title': step.step_name,
                    'description': step.description,
                    'image_url': step.image_url,
                    'duration_minutes': step.duration_minutes
                })

        features_map = {
            'Regular Cleaning': ['Dust removal', 'Bed making', 'Floor vacuuming', 'Bathroom cleaning', 'Trash disposal'],
            'Deep Cleaning': ['All regular cleaning tasks', 'Interior appliance cleaning', 'Window cleaning', 'Tile grout cleaning', 'Air vent cleaning'],
            'Bed Sheet Change': ['Fresh linen installation', 'Pillowcase change', 'Bedspread refresh', 'Mattress rotation'],
            'Express Cleaning': ['Quick tidy up', 'Surface cleaning', 'Bathroom refresh', 'Floor sweep'],
            'Home Cleaning': ['Full home cleaning', 'Kitchen deep clean', 'Bathroom sanitization', 'Living areas cleaning'],
            'Commercial Cleaning': ['Office space cleaning', 'Conference room cleaning', 'Reception area', 'Restroom sanitization'],
        }

        precautions_map = {
            'Regular Cleaning': ['Please remove valuables', 'Keep pets away during cleaning', 'Ensure someone is home'],
            'Deep Cleaning': ['Clear access to all areas', 'Remove fragile items', 'Ventilate the space'],
            'Bed Sheet Change': ['Provide linen preference', 'Inform of bed size', 'Any special instructions'],
            'Express Cleaning': ['Focus on main areas', 'Quick turnaround', 'Basic cleaning only'],
        }

        features = features_map.get(service.type_name, ['Professional service', 'Experienced cleaners', 'Quality guarantee', 'Satisfaction insured'])
        precautions = precautions_map.get(service.type_name, ['Follow guidelines', 'Ensure access', 'Supervise if needed'])

        mprice = getattr(service, 'market_price', None)
        return {
            'type_id': service.id,
            'type_name': service.type_name,
            'description': service.description,
            'price': float(service.price) if service.price else 0,
            'market_price': float(mprice) if mprice is not None else None,
            'features': features,
            'process_steps': process_steps,
            'precautions': precautions
        }

    def get_all_rooms(self) -> List[dict]:
        """Get all active rooms - deprecated, returns empty list"""
        return []

    def create_order(
        self,
        order_data: dict,
        current_user: Optional[UserModel] = None,
    ) -> dict:
        """Create a ``service_order`` from the portal (Book now).

        Maps portal fields to ``service_order``: ``service_address``, ``scheduled_start`` /
        ``scheduled_end`` (from duration), ``priority``, ``assigned_staff_id`` (cleaner),
        ``requirement_id`` (optional), and a structured ``remarks`` snapshot for staff.
        """
        service_type = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.id == order_data.get('service_type_id'),
            ServiceTypeModel.is_deleted == 0
        ).first()

        if not service_type:
            return {'success': False, 'message': 'Service type not found'}

        if not current_user:
            return {
                'success': False,
                'message': 'Please log in to create an order.',
            }
        guest = self.db.query(UserModel).filter(
            UserModel.id == current_user.id,
            UserModel.is_deleted == 0
        ).first()
        if not guest:
            return {
                'success': False,
                'message': 'User not found.',
            }

        requirement_id = order_data.get('requirement_id')
        if requirement_id:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == requirement_id,
                CustomerRequirementModel.is_deleted == 0
            ).first()
            if not requirement:
                return {'success': False, 'message': 'Requirement not found'}
            if requirement.status != 1:
                return {
                    'success': False,
                    'message': (
                        'Requirement is not accepted yet. Please wait for admin to assign a cleaner.'
                    ),
                }
            if requirement.user_id is not None and requirement.user_id != guest.id:
                return {'success': False, 'message': 'You can only create an order for your own requirement'}
            if requirement.user_id is None and requirement.guest_phone != order_data.get('guest_phone'):
                return {'success': False, 'message': 'You can only create an order for your own requirement'}

        service_address = (order_data.get('service_address') or '').strip()
        if not service_address:
            return {'success': False, 'message': 'Service address is required'}

        sched_start = order_data.get('scheduled_time')
        if sched_start is None:
            return {'success': False, 'message': 'Preferred service time is required'}
        if isinstance(sched_start, str):
            try:
                sched_start = datetime.fromisoformat(sched_start.replace('Z', '+00:00'))
            except (TypeError, ValueError):
                return {'success': False, 'message': 'Invalid preferred service time'}

        try:
            duration_h = float(order_data.get('scheduled_duration_hours') or 2.0)
        except (TypeError, ValueError):
            duration_h = 2.0
        duration_h = max(0.5, min(duration_h, 24.0))
        sched_end = sched_start + timedelta(hours=duration_h)

        contact_parts: List[str] = []
        name_snap = (order_data.get('guest_name') or '').strip()
        if name_snap:
            contact_parts.append(f'Contact: {name_snap}')
        email_snap = (order_data.get('guest_email') or '').strip()
        if email_snap:
            contact_parts.append(f'Email: {email_snap}')
        phone_snap = (order_data.get('guest_phone') or '').strip()
        if phone_snap:
            contact_parts.append(f'Phone: {phone_snap}')
        contact_line = ' | '.join(contact_parts)
        user_notes = (order_data.get('remarks') or '').strip()
        # Keep contact info readable in the UI:
        # Contact: ... | Email: ... | Phone: ... | Notes: ...
        remark_chunks = [c for c in [contact_line] if c]
        if user_notes:
            remark_chunks.append(f'Notes: {user_notes}')
        remarks_combined = ' | '.join(remark_chunks)[:500] if remark_chunks else None

        try:
            priority = int(order_data.get('priority') or 0)
        except (TypeError, ValueError):
            priority = 0
        priority = max(0, min(priority, 2))

        cleaner_id = order_data.get('cleaner_id')
        new_status = 1 if cleaner_id else 0

        order_no = f"SO{datetime.now().strftime('%Y%m%d%H%M')}{random.randint(100, 999)}"

        new_order = ServiceOrderModel(
            order_no=order_no,
            guest_id=guest.id,
            service_type_id=order_data.get('service_type_id'),
            requirement_id=requirement_id if requirement_id else None,
            assigned_staff_id=cleaner_id,
            service_address=service_address[:500],
            status=new_status,
            priority=priority,
            request_time=datetime.now(),
            scheduled_start=sched_start,
            scheduled_end=sched_end,
            remarks=remarks_combined,
            create_time=datetime.now(),
            modify_time=datetime.now(),
        )

        self.db.add(new_order)
        self.db.commit()

        return {'success': True, 'order_no': order_no, 'order_id': new_order.order_id}

    def get_orders_by_phone(self, phone: str) -> List[dict]:
        """Get orders by phone number"""
        guest = self.db.query(UserModel).filter(
            UserModel.phone == phone,
            UserModel.is_deleted == 0
        ).first()

        if not guest:
            return []

        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == guest.id,
            ServiceOrderModel.is_deleted == 0
        ).order_by(ServiceOrderModel.create_time.desc()).all()

        result = []
        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.id == order.service_type_id
            ).first()

            result.append({
                'order_id': order.order_id,
                'order_no': order.order_no,
                'status': order.status,
                'service_type_name': service_type.type_name if service_type else None,
                'scheduled_start': order.scheduled_start,
                'scheduled_end': order.scheduled_end,
                'create_time': order.create_time,
                'price': float(service_type.price) if service_type else 0,
                'actual_price': float(service_type.price) if service_type else 0,
                'service_address': order.service_address,
                'priority': order.priority,
            })

        return result

    def get_stats(self) -> dict:
        """Get portal statistics"""
        total_users = self.db.query(UserModel).filter(UserModel.is_deleted == 0).count()

        completed_orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.status == 4
        ).count()

        ratings = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.rating.isnot(None)
        ).all()

        avg_rating = 4.9
        if ratings:
            total_rating = sum([self._decode_rating(r.rating) for r in ratings if self._decode_rating(r.rating) is not None])
            avg_rating = round(total_rating / len(ratings), 1)

        return {
            'total_users': total_users,
            'total_orders': completed_orders,
            'total_tasks': completed_orders,
            'rating': avg_rating
        }

    def get_company_info(self) -> dict:
        """Get company info"""
        return {
            'about_us': 'CleanPro is a professional hotel cleaning service platform, committed to providing high-quality cleaning services to our customers.',
            'phone': '400-888-8888',
            'email': 'service@cleanpro.com',
            'address': 'Pudong New District, Shanghai',
            'facebook': '',
            'twitter': '',
            'instagram': ''
        }

    def get_reviews(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """Get customer reviews"""
        reviews = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.guest_feedback.isnot(None),
            ServiceOrderModel.rating.isnot(None)
        ).order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for r in reviews:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.id == r.service_type_id
            ).first()
            guest = self.db.query(UserModel).filter(UserModel.id == r.guest_id).first()

            result.append({
                'id': r.order_id,
                'guest_name': guest.full_name if guest and guest.full_name else 'Guest',
                'rating': self._decode_rating(r.rating) if r.rating is not None else 5,
                'comment': r.guest_feedback or 'Great service!',
                'service_type_name': service_type.type_name if service_type else 'Cleaning Service',
                'create_time': r.create_time.strftime('%Y-%m-%d') if r.create_time else ''
            })

        if not result:
            result = [
                {'id': 1, 'guest_name': 'John D.', 'rating': 5, 'comment': 'Excellent service!', 'service_type_name': 'Deep Cleaning', 'create_time': '2026-03-10'},
                {'id': 2, 'guest_name': 'Sarah M.', 'rating': 5, 'comment': 'Highly recommend!', 'service_type_name': 'Regular Cleaning', 'create_time': '2026-03-09'},
            ]

        return result

    def get_reviews_count(self) -> dict:
        """Get total reviews count"""
        count = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.guest_feedback.isnot(None),
            ServiceOrderModel.rating.isnot(None)
        ).count()
        return {'total': count}

    def get_review_detail(self, review_id: int) -> dict:
        """Get single review detail"""
        order = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == review_id,
            ServiceOrderModel.is_deleted == 0
        ).first()

        if not order or not order.guest_feedback:
            raise ValueError('Review not found')

        service_type = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.id == order.service_type_id
        ).first()
        guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()

        return {
            'id': order.order_id,
            'guest_name': guest.full_name if guest and guest.full_name else 'Guest',
            'rating': self._decode_rating(order.rating) if order.rating is not None else 5,
            'comment': order.guest_feedback or 'Great service!',
            'service_type_name': service_type.type_name if service_type else 'Cleaning Service',
            'create_time': order.create_time.strftime('%Y-%m-%d') if order.create_time else ''
        }

    def get_all_cleaners(self, sort_by: str = None, search: str = None) -> List[dict]:
        """Get all active cleaners with optional sorting and filtering"""
        cleaner_role_ids = self.db.query(RoleModel.id).filter(
            RoleModel.role_name.in_(['staff', 'cleaner', 'employee'])
        ).all()
        cleaner_role_ids = [r[0] for r in cleaner_role_ids]

        if not cleaner_role_ids:
            return []

        user_ids = self.db.query(UserRoleModel.user_id).filter(
            UserRoleModel.role_id.in_(cleaner_role_ids)
        ).all()
        user_ids = [u[0] for u in user_ids]

        if not user_ids:
            return []

        query = self.db.query(UserModel).filter(
            UserModel.id.in_(user_ids),
            UserModel.is_deleted == 0,
            UserModel.status == 1
        )

        if search:
            query = query.filter(UserModel.full_name.ilike(f'%{search}%'))

        cleaners = query.all()

        result = []
        for c in cleaners:
            result.append({
                'id': c.id,
                'username': c.username,
                'full_name': c.full_name or c.username,
                'star_level': getattr(c, 'star_level', None) or 1,
                'total_orders': getattr(c, 'total_orders', None) or 0,
                'total_rating': round(getattr(c, 'total_rating', None) or 5.0, 1),
                'distance': None,
                'avatar': None
            })

        if sort_by == 'rating_desc':
            result.sort(key=lambda x: x['total_rating'], reverse=True)
        elif sort_by == 'rating_asc':
            result.sort(key=lambda x: x['total_rating'])
        elif sort_by == 'orders_desc':
            result.sort(key=lambda x: x['total_orders'], reverse=True)
        elif sort_by == 'orders_asc':
            result.sort(key=lambda x: x['total_orders'])

        return result

    def get_cleaner_detail(self, cleaner_id: int) -> dict:
        """Get cleaner detail with recent reviews"""
        cleaner = self.db.query(UserModel).filter(
            UserModel.id == cleaner_id,
            UserModel.is_deleted == 0
        ).first()

        if not cleaner:
            raise ValueError('Cleaner not found')

        return {
            'id': cleaner.id,
            'username': cleaner.username,
            'full_name': cleaner.full_name or cleaner.username,
            'star_level': cleaner.star_level or 1,
            'total_orders': cleaner.total_orders or 0,
            'total_rating': cleaner.total_rating or 5.0,
            'avatar': None,
            'recent_reviews': []
        }

    def get_cleaner_applications(self, cleaner_id: int) -> List[dict]:
        """Get all applications for a cleaner"""
        result = []

        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.cleaner_id == cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        ).order_by(CleanerApplicationModel.create_time.desc()).all()

        status_text_map = {0: 'Pending', 1: 'Accepted', 2: 'Rejected', 3: 'Completed'}

        for app in applications:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == app.requirement_id
            ).first()

            result.append({
                'id': app.id,
                'task_type': 'application',
                'task_id': app.requirement_id,
                'title': f"Application for: {requirement.property_type if requirement else 'Requirement'}",
                'description': f"Budget: ${app.offered_price}" + (f", Message: {app.message}" if app.message else ""),
                'status': app.status,
                'status_text': status_text_map.get(app.status, 'Unknown'),
                'price': app.offered_price,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else '',
                'update_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
            })

        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.status.in_([3, 4])
        ).order_by(ServiceOrderModel.create_time.desc()).all()

        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.id == order.service_type_id
            ).first()

            result.append({
                'id': order.order_id,
                'task_type': 'order',
                'task_id': order.order_id,
                'title': f"Order #{order.order_no}: {service_type.type_name if service_type else 'Service'}",
                'description': f"Order for {order.order_no}",
                'status': order.status,
                'status_text': 'Completed' if order.status == 4 else 'In Progress',
                'price': float(service_type.price) if service_type else 0,
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'update_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return result

    def get_requirement_by_id(self, requirement_id: int) -> dict:
        """Get a single requirement by ID"""
        req = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id,
            CustomerRequirementModel.is_deleted == 0
        ).first()

        if not req:
            return None

        return {
            'id': req.id,
            'user_id': req.user_id,
            'guest_name': req.guest_name,
            'guest_phone': req.guest_phone,
            'guest_email': req.guest_email,
            'guest_address': getattr(req, 'guest_address', None),
            'property_type': req.property_type,
            'bedroom': req.bedroom,
            'bathroom': req.bathroom,
            'living_room': req.living_room,
            'kitchen': req.kitchen,
            'lawn': req.lawn,
            'car_space': req.car_space,
            'square_footage': req.square_footage,
            'service_type_name': req.service_type_name,
            'preferred_time': req.preferred_time,
            'budget': req.budget,
            'description': req.description,
            'status': req.status,
            'assigned_cleaner_id': req.assigned_cleaner_id,
            'is_published': getattr(req, 'is_published', 1),
            'publish_time': req.publish_time.strftime('%Y-%m-%d %H:%M') if getattr(
                req, 'publish_time', None
            ) else '',
            'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
        }

    def get_all_requirements(self) -> List[dict]:
        """Published, open requirements for the public portal (unassigned)."""
        requirements = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.is_deleted == 0,
            CustomerRequirementModel.assigned_cleaner_id.is_(None),
            CustomerRequirementModel.is_published == 1,
        ).order_by(CustomerRequirementModel.create_time.desc()).all()

        result = []
        for req in requirements:
            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'guest_address': getattr(req, 'guest_address', None),
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'is_published': getattr(req, 'is_published', 1),
                'publish_time': req.publish_time.strftime('%Y-%m-%d %H:%M') if getattr(
                    req, 'publish_time', None
                ) else '',
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
            })

        return result

    def get_requirements_by_phone(self, phone: str) -> List[dict]:
        """Get requirements by phone"""
        requirements = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.guest_phone == phone,
            CustomerRequirementModel.is_deleted == 0
        ).order_by(CustomerRequirementModel.create_time.desc()).all()

        result = []
        for req in requirements:
            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'guest_address': getattr(req, 'guest_address', None),
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'is_published': getattr(req, 'is_published', 1),
                'publish_time': req.publish_time.strftime('%Y-%m-%d %H:%M') if getattr(
                    req, 'publish_time', None
                ) else '',
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
            })

        return result

    def create_requirement(self, requirement_data: dict) -> dict:
        """Create a new customer requirement (public portal form; always published)."""
        now = datetime.now()
        new_req = CustomerRequirementModel(
            user_id=None,
            guest_name=requirement_data.get('guest_name'),
            guest_phone=requirement_data.get('guest_phone'),
            guest_email=requirement_data.get('guest_email'),
            guest_address=(requirement_data.get('guest_address') or '').strip() or None,
            property_type=requirement_data.get('property_type'),
            bedroom=requirement_data.get('bedroom', 1),
            bathroom=requirement_data.get('bathroom', 1),
            living_room=requirement_data.get('living_room', 1),
            kitchen=requirement_data.get('kitchen', 0),
            lawn=requirement_data.get('lawn', 0),
            car_space=requirement_data.get('car_space', 0),
            square_footage=requirement_data.get('square_footage'),
            service_type_name=requirement_data.get('service_type_name'),
            preferred_time=requirement_data.get('preferred_time'),
            budget=requirement_data.get('budget'),
            description=requirement_data.get('description'),
            status=0,
            is_published=1,
            publish_time=now,
            create_time=now,
            modify_time=now
        )

        self.db.add(new_req)
        self.db.commit()

        return {'success': True, 'id': new_req.id}

    def create_customer_requirement(self, user_id: int, data: dict) -> dict:
        """Customer module: save requirement and optionally list it on the portal."""
        publish = bool(data.get('publish_to_portal', True))
        now = datetime.now()
        new_req = CustomerRequirementModel(
            user_id=user_id,
            guest_name=data.get('guest_name'),
            guest_phone=data.get('guest_phone'),
            guest_email=data.get('guest_email'),
            guest_address=(data.get('guest_address') or '').strip() or None,
            property_type=data.get('property_type'),
            bedroom=int(data.get('bedroom', 1) or 1),
            bathroom=int(data.get('bathroom', 1) or 1),
            living_room=int(data.get('living_room', 1) or 1),
            kitchen=int(data.get('kitchen', 1) or 1),
            lawn=int(data.get('lawn', 0) or 0),
            car_space=int(data.get('car_space', 0) or 0),
            square_footage=data.get('square_footage'),
            service_type_name=data.get('service_type_name'),
            preferred_time=data.get('preferred_time'),
            budget=data.get('budget'),
            description=data.get('description'),
            status=0,
            is_published=1 if publish else 0,
            publish_time=now if publish else None,
            create_time=now,
            modify_time=now
        )
        self.db.add(new_req)
        self.db.commit()
        return {
            'success': True,
            'id': new_req.id,
            'published': publish,
        }

    def update_customer_requirement(self, user_id: int, requirement_id: int, data: dict) -> dict:
        """Update a requirement owned by the customer; only while ``is_published`` is 0 (draft)."""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id,
            CustomerRequirementModel.is_deleted == 0,
        ).first()
        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}
        if requirement.user_id != user_id:
            return {'success': False, 'message': 'You can only edit your own requirements'}
        published = int(getattr(requirement, 'is_published', 1) or 0)
        if published != 0:
            return {'success': False, 'message': 'Published requirements cannot be edited. Save as draft first.'}

        now = datetime.now()
        requirement.guest_name = (data.get('guest_name') or requirement.guest_name or '').strip()
        requirement.guest_phone = (data.get('guest_phone') or requirement.guest_phone or '').strip()
        requirement.guest_email = (data.get('guest_email') or '').strip() or None
        requirement.guest_address = (data.get('guest_address') or '').strip() or None
        requirement.property_type = data.get('property_type') or requirement.property_type
        requirement.bedroom = int(data.get('bedroom', requirement.bedroom) or 1)
        requirement.bathroom = int(data.get('bathroom', requirement.bathroom) or 1)
        requirement.living_room = int(data.get('living_room', requirement.living_room) or 1)
        requirement.kitchen = int(data.get('kitchen', requirement.kitchen) or 1)
        requirement.lawn = int(data.get('lawn', requirement.lawn) or 0)
        requirement.car_space = int(data.get('car_space', requirement.car_space) or 0)
        requirement.square_footage = data.get('square_footage')
        requirement.service_type_name = data.get('service_type_name')
        requirement.preferred_time = data.get('preferred_time')
        requirement.budget = data.get('budget')
        requirement.description = data.get('description')
        requirement.modify_time = now

        publish = bool(data.get('publish_to_portal', False))
        if publish:
            requirement.is_published = 1
            requirement.publish_time = now
        else:
            requirement.is_published = 0
            requirement.publish_time = None

        self.db.commit()
        self.db.refresh(requirement)
        return {'success': True, 'published': bool(requirement.is_published)}

    def apply_for_requirement(self, application_data: dict) -> dict:
        """Apply for a customer requirement"""
        existing = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == application_data.requirement_id,
            CleanerApplicationModel.cleaner_id == application_data.cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        ).first()

        if existing:
            return {'success': False, 'message': 'Already applied'}

        new_app = CleanerApplicationModel(
            requirement_id=application_data.requirement_id,
            cleaner_id=application_data.cleaner_id,
            cleaner_name=application_data.cleaner_name,
            offered_price=application_data.offered_price,
            message=application_data.message,
            status=0,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )

        self.db.add(new_app)

        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == application_data.requirement_id
        ).first()
        if requirement and requirement.user_id:
            notify_user(
                self.db,
                requirement.user_id,
                'New cleaner application',
                f'{application_data.cleaner_name} applied for your requirement '
                f"(#{requirement.id}, {requirement.property_type}).",
                'info',
                '/my-requirements',
            )

        self.db.commit()

        return {'success': True, 'id': new_app.id}

    def get_applications(self, requirement_id: int) -> List[dict]:
        """Get applications for a requirement with cleaner details"""
        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == requirement_id,
            CleanerApplicationModel.is_deleted == 0
        ).order_by(CleanerApplicationModel.create_time.desc()).all()

        result = []
        for app in applications:
            cleaner = self.db.query(UserModel).filter(UserModel.id == app.cleaner_id).first()
            star_level = None
            total_orders = None
            total_rating = None
            
            if cleaner:
                star_level = getattr(cleaner, 'star_level', None) or getattr(cleaner, 'rating', None) or 1
                total_orders = getattr(cleaner, 'total_orders', None) or 0
                total_rating = getattr(cleaner, 'total_rating', None) or getattr(cleaner, 'rating', None) or 5.0

            result.append({
                'id': app.id,
                'requirement_id': app.requirement_id,
                'cleaner_id': app.cleaner_id,
                'cleaner_name': app.cleaner_name,
                'offered_price': app.offered_price,
                'message': app.message,
                'status': app.status,
                'star_level': star_level,
                'total_orders': total_orders,
                'total_rating': total_rating,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
            })

        return result

    def get_cleaner_applications_paginated(self, cleaner_id: int, status: Optional[int] = None, 
                                          limit: int = 20, offset: int = 0) -> dict:
        """Get paginated applications for a cleaner"""
        query = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.cleaner_id == cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        )

        if status is not None:
            query = query.filter(CleanerApplicationModel.status == status)

        total = query.count()
        applications = query.order_by(CleanerApplicationModel.create_time.desc()).offset(offset).limit(limit).all()

        status_text_map = {0: 'Pending', 1: 'Accepted', 2: 'Rejected', 3: 'Completed'}

        result = []
        for app in applications:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == app.requirement_id
            ).first()

            result.append({
                'id': app.id,
                'task_type': 'application',
                'task_id': app.requirement_id,
                'requirement_id': app.requirement_id,
                'title': f"Application for: {requirement.property_type if requirement else 'Requirement'}",
                'description': f"Budget: ${app.offered_price}" + (f", Message: {app.message}" if app.message else ""),
                'property_type': requirement.property_type if requirement else '',
                'bedroom': requirement.bedroom if requirement else 0,
                'bathroom': requirement.bathroom if requirement else 0,
                'address': requirement.description if requirement else '',
                'budget': app.offered_price,
                'status': app.status,
                'status_text': status_text_map.get(app.status, 'Unknown'),
                'price': app.offered_price,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else '',
                'update_time': app.modify_time.strftime('%Y-%m-%d %H:%M') if app.modify_time else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_cleaner_requirements(self, cleaner_id: int, status: Optional[int] = None, 
                                limit: int = 20, offset: int = 0) -> dict:
        """Get requirements assigned to or applied by a cleaner"""
        from model.cleaner_application import CleanerApplicationModel
        
        assigned_query = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.assigned_cleaner_id == cleaner_id,
            CustomerRequirementModel.is_deleted == 0
        )
        
        applied_query = self.db.query(CustomerRequirementModel).join(
            CleanerApplicationModel, CleanerApplicationModel.requirement_id == CustomerRequirementModel.id
        ).filter(
            CleanerApplicationModel.cleaner_id == cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        )
        
        assigned_requirements = assigned_query.all()
        applied_requirements = applied_query.all()
        
        all_requirements = {req.id: req for req in assigned_requirements + applied_requirements}.values()
        
        result = []
        for req in all_requirements:
            app = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.cleaner_id == cleaner_id,
                CleanerApplicationModel.is_deleted == 0
            ).first()
            
            if req.assigned_cleaner_id == cleaner_id:
                app_status = 1
                app_status_text = 'Assigned'
            elif app:
                app_status = app.status
                app_status_text = {0: 'Pending', 1: 'Accepted', 2: 'Rejected'}.get(app.status, 'Unknown')
            else:
                app_status = 0
                app_status_text = 'Applied'
            
            if status is not None and app_status != status:
                continue
            
            result.append({
                'id': req.id,
                'requirement_id': req.id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'guest_address': getattr(req, 'guest_address', None),
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'application_status': app_status,
                'application_status_text': app_status_text,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
            })
        
        total = len(result)
        result = result[offset:offset + limit]
        
        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_admin_requirements(self, status: Optional[int] = None, limit: int = 20, offset: int = 0,
                             guest_name: str = None, guest_phone: str = None,
                             property_type: str = None, service_type: str = None,
                             start_date: str = None, end_date: str = None) -> dict:
        """Get all requirements for admin with pagination and filters"""
        query = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.is_deleted == 0
        )

        if status is not None:
            query = query.filter(CustomerRequirementModel.status == status)

        if guest_name:
            query = query.filter(CustomerRequirementModel.guest_name.like(f'%{guest_name}%'))

        if guest_phone:
            query = query.filter(CustomerRequirementModel.guest_phone.like(f'%{guest_phone}%'))

        if property_type:
            query = query.filter(CustomerRequirementModel.property_type == property_type)

        if service_type:
            query = query.filter(CustomerRequirementModel.service_type_name.like(f'%{service_type}%'))

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(CustomerRequirementModel.create_time >= start)
            except (ValueError, TypeError):
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(CustomerRequirementModel.create_time <= end)
            except (ValueError, TypeError):
                pass

        total = query.count()

        requirements = query.order_by(
            CustomerRequirementModel.create_time.desc()
        ).offset(offset).limit(limit).all()

        req_ids = [r.id for r in requirements]
        latest_order_by_req_id = {}
        if req_ids:
            for ord_row in self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.requirement_id.in_(req_ids),
                ServiceOrderModel.is_deleted == 0
            ).all():
                rid = ord_row.requirement_id
                prev = latest_order_by_req_id.get(rid)
                ot = ord_row.create_time or datetime.min
                pt = prev.create_time if prev is not None else datetime.min
                if prev is None or ot > pt:
                    latest_order_by_req_id[rid] = ord_row

        assignee_ids = {r.assigned_cleaner_id for r in requirements if r.assigned_cleaner_id}
        assignees_by_id = {}
        if assignee_ids:
            for user_row in self.db.query(UserModel).filter(
                UserModel.id.in_(assignee_ids),
                UserModel.is_deleted == 0,
            ).all():
                assignees_by_id[user_row.id] = user_row

        result = []
        for req in requirements:
            apps_count = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.is_deleted == 0
            ).count()

            accepted_app = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.status == 1,
                CleanerApplicationModel.is_deleted == 0
            ).first()

            assignee = assignees_by_id.get(req.assigned_cleaner_id) if req.assigned_cleaner_id else None
            assigned_username = assignee.username if assignee else None
            assigned_full_name = (assignee.full_name or '').strip() if assignee else None

            linked_order = latest_order_by_req_id.get(req.id)
            can_reassign_cleaner = True
            if linked_order is not None and linked_order.status not in self._ORDER_STATUSES_ALLOW_REASSIGN_STAFF:
                can_reassign_cleaner = False

            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'guest_address': getattr(req, 'guest_address', None),
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'assigned_cleaner_username': assigned_username,
                'assigned_cleaner_full_name': assigned_full_name or None,
                'can_reassign_cleaner': can_reassign_cleaner,
                'service_order_status': linked_order.status if linked_order else None,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else '',
                'applications_count': apps_count,
                'accepted_cleaner_id': accepted_app.cleaner_id if accepted_app else None,
                'accepted_cleaner_name': accepted_app.cleaner_name if accepted_app else None
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_admin_cleaners(self) -> List[dict]:
        """Get all cleaners with workload for admin"""
        cleaner_role_ids = self.db.query(RoleModel.id).filter(
            RoleModel.role_name.in_(['staff', 'cleaner', 'employee'])
        ).all()
        cleaner_role_ids = [r[0] for r in cleaner_role_ids]

        if not cleaner_role_ids:
            return []

        user_ids = self.db.query(UserRoleModel.user_id).filter(
            UserRoleModel.role_id.in_(cleaner_role_ids)
        ).all()
        user_ids = [u[0] for u in user_ids]

        if not user_ids:
            return []

        cleaners = self.db.query(UserModel).filter(
            UserModel.id.in_(user_ids),
            UserModel.is_deleted == 0,
            UserModel.status == 1
        ).all()

        result = []
        for c in cleaners:
            pending = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.assigned_staff_id == c.id,
                ServiceOrderModel.is_deleted == 0,
                ServiceOrderModel.status.in_([1, 2, 3])
            ).count()

            completed = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.assigned_staff_id == c.id,
                ServiceOrderModel.is_deleted == 0,
                ServiceOrderModel.status == 4
            ).count()

            result.append({
                'id': c.id,
                'username': c.username,
                'full_name': c.full_name or c.username,
                'star_level': c.star_level or 1,
                'total_orders': c.total_orders or 0,
                'total_rating': c.total_rating or 5.0,
                'pending_tasks': pending,
                'completed_tasks': completed
            })

        return result

    def assign_requirement_to_cleaner(self, requirement_id: int, cleaner_id: int) -> dict:
        """Assign a requirement to a specific cleaner"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        cleaner = self.db.query(UserModel).filter(UserModel.id == cleaner_id).first()
        if not cleaner:
            return {'success': False, 'message': 'Cleaner not found'}

        existing_order = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.requirement_id == requirement_id,
            ServiceOrderModel.is_deleted == 0
        ).order_by(ServiceOrderModel.create_time.desc()).first()

        if existing_order is not None and existing_order.status not in self._ORDER_STATUSES_ALLOW_REASSIGN_STAFF:
            if existing_order.assigned_staff_id != cleaner_id:
                return {
                    'success': False,
                    'message': (
                        'Cannot assign a different cleaner: the service order has already left the '
                        '"assigned" stage (e.g. in progress, completed, or pending payment).'
                    ),
                }

        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == requirement_id,
            CleanerApplicationModel.is_deleted == 0
        ).all()

        for app in applications:
            if app.cleaner_id == cleaner_id:
                app.status = 1
            else:
                app.status = 2

        requirement.status = 1
        requirement.assigned_cleaner_id = cleaner_id

        service_type_id = self._service_type_id_for_requirement(requirement)

        if existing_order:
            existing_order.assigned_staff_id = cleaner_id
            existing_order.modify_time = datetime.utcnow()
            if existing_order.status == 0:
                existing_order.status = 1
            order_no = existing_order.order_no
            order_id = existing_order.order_id
        else:
            order_no = 'SO' + ''.join(random.choices(string.digits, k=10))
            new_order = ServiceOrderModel(
                order_no=order_no,
                guest_id=requirement.user_id,
                service_type_id=service_type_id,
                requirement_id=requirement_id,
                assigned_staff_id=cleaner_id,
                status=1,
                request_time=datetime.utcnow(),
            )
            self.db.add(new_order)
            self.db.flush()
            order_id = new_order.order_id

        cleaner_label = cleaner.full_name or cleaner.username or 'cleaner'
        notify_user(
            self.db,
            cleaner_id,
            'Assigned to a customer requirement',
            (
                f'You were assigned to requirement #{requirement_id} ({requirement.property_type}). '
                f'Service order {order_no}.'
            ),
            'info',
            '/my-orders',
        )
        if requirement.user_id:
            notify_user(
                self.db,
                requirement.user_id,
                'Cleaner assigned',
                (
                    f'{cleaner_label} was assigned to your requirement #{requirement_id}. '
                    f'Service order {order_no}.'
                ),
                'success',
                '/my-orders',
            )

        self.db.commit()

        return {
            'success': True,
            'message': f'Requirement assigned to {cleaner_label}',
            'order_id': order_id,
            'order_no': order_no,
        }

    def delete_requirement(self, requirement_id: int) -> dict:
        """Hard delete a requirement"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        self.db.delete(requirement)
        self.db.commit()

        return {'success': True, 'message': 'Requirement deleted'}

    def hide_requirement(self, requirement_id: int) -> dict:
        """Soft delete/hide a requirement"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        requirement.is_deleted = 1
        self.db.commit()

        return {'success': True, 'message': 'Requirement hidden'}

    def get_all_cleaner_tasks(self, status: Optional[int] = None, limit: int = 20, offset: int = 0,
                             order_no: str = None, cleaner_name: str = None,
                             start_date: str = None, end_date: str = None) -> dict:
        """Get all cleaner tasks for admin with pagination and filters"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.assigned_staff_id.isnot(None)
        )

        if status is not None:
            query = query.filter(ServiceOrderModel.status == status)

        if order_no:
            query = query.filter(ServiceOrderModel.order_no.like(f'%{order_no}%'))

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(ServiceOrderModel.create_time >= start)
            except (ValueError, TypeError):
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceOrderModel.create_time <= end)
            except (ValueError, TypeError):
                pass

        if cleaner_name:
            cleaner_ids = self.db.query(UserModel.id).filter(
                UserModel.full_name.like(f'%{cleaner_name}%')
            ).all()
            cleaner_id_list = [c.id for c in cleaner_ids]
            if cleaner_id_list:
                query = query.filter(ServiceOrderModel.assigned_staff_id.in_(cleaner_id_list))
            else:
                return {'items': [], 'total': 0, 'page': 1, 'page_size': limit}

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
            guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.user_id == order.guest_id,
                CustomerRequirementModel.is_deleted == 0
            ).order_by(CustomerRequirementModel.create_time.desc()).first()

            result.append({
                'id': order.order_id,
                'order_no': order.order_no,
                'cleaner_id': order.assigned_staff_id,
                'cleaner_name': self._user_display_name(cleaner),
                'service_type': service_type.type_name if service_type else '',
                'guest_name': requirement.guest_name if requirement else self._user_display_name(guest),
                'guest_phone': requirement.guest_phone if requirement else '',
                'guest_email': requirement.guest_email if requirement else (guest.email if guest else ''),
                'property_type': requirement.property_type if requirement else '',
                'address': (
                    (getattr(requirement, 'guest_address', None) or '').strip()
                    or (requirement.description if requirement else '')
                ),
                'bedroom': requirement.bedroom if requirement else '',
                'bathroom': requirement.bathroom if requirement else '',
                'living_room': requirement.living_room if requirement else '',
                'kitchen': requirement.kitchen if requirement else '',
                'lawn': requirement.lawn if requirement else '',
                'car_space': requirement.car_space if requirement else '',
                'square_footage': requirement.square_footage if requirement else '',
                'preferred_time': requirement.preferred_time if requirement else '',
                'budget': requirement.budget if requirement else '',
                'description': requirement.description if requirement else '',
                'remarks': order.remarks if order.remarks else '',
                'guest_feedback': order.guest_feedback if order.guest_feedback else '',
                'rating': self._decode_rating(order.rating) if order.rating is not None else '',
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def _get_status_text(self, status: int) -> str:
        status_map = {
            0: 'Pending',
            1: 'Assigned',
            2: 'In Progress',
            3: 'Pending Review',
            4: 'Completed',
            5: 'Cancelled'
        }
        return status_map.get(status, 'Unknown')

    def get_cleaner_tasks(self, cleaner_id: int, status: Optional[int] = None, limit: int = 20, offset: int = 0) -> dict:
        """Get tasks for a specific cleaner with pagination"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        )

        if status is not None:
            query = query.filter(ServiceOrderModel.status == status)

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
            guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.user_id == order.guest_id,
                CustomerRequirementModel.is_deleted == 0
            ).order_by(CustomerRequirementModel.create_time.desc()).first()

            result.append({
                'id': order.order_id,
                'order_no': order.order_no,
                'service_type': service_type.type_name if service_type else '',
                'guest_name': guest.full_name if guest else '',
                'guest_phone': guest.phone if guest else '',
                'property_type': requirement.property_type if requirement else '',
                'address': requirement.description if requirement else '',
                'bedroom': requirement.bedroom if requirement else 0,
                'bathroom': requirement.bathroom if requirement else 0,
                'budget': requirement.budget if requirement else 0,
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_customer_requirements(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        requirement_id: int = None,
        status: int = None,
        property_type: str = None,
        service_type: str = None,
        is_published: int = None,
    ) -> dict:
        """Get requirements created by this customer (posted by them), with optional filters."""
        query = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.user_id == user_id,
            CustomerRequirementModel.is_deleted == 0
        )

        if requirement_id is not None:
            query = query.filter(CustomerRequirementModel.id == requirement_id)

        if status is not None:
            query = query.filter(CustomerRequirementModel.status == status)
        
        if property_type:
            query = query.filter(CustomerRequirementModel.property_type == property_type)
        
        if service_type:
            query = query.filter(CustomerRequirementModel.service_type_name.like(f'%{service_type}%'))

        if is_published is not None:
            query = query.filter(CustomerRequirementModel.is_published == int(is_published))

        total = query.count()

        requirements = query.order_by(CustomerRequirementModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for req in requirements:
            order = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.requirement_id == req.id,
                ServiceOrderModel.guest_id == user_id,
                ServiceOrderModel.is_deleted == 0
            ).order_by(ServiceOrderModel.create_time.desc()).first()

            pending_payment = False
            order_id = None
            order_no = None
            if order:
                order_id = order.order_id
                order_no = order.order_no
                pending_payment = self.db.query(TransactionModel).filter(
                    TransactionModel.order_id == order.order_id,
                    TransactionModel.user_id == user_id,
                    TransactionModel.type == 'payment',
                    TransactionModel.status == 'pending'
                ).first() is not None

            applications = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.is_deleted == 0
            ).all()

            apps_list = []
            for app in applications:
                cleaner = self.db.query(UserModel).filter(UserModel.id == app.cleaner_id).first()
                cleaner_data = {
                    'id': app.id,
                    'cleaner_id': app.cleaner_id,
                    'cleaner_name': (
                    app.cleaner_name
                    or PortalService._user_display_name(cleaner)
                    or f'Cleaner {app.cleaner_id}'
                ),
                    'offered_price': app.offered_price,
                    'status': app.status,
                    'status_text': 'Accepted' if app.status == 1 else ('Rejected' if app.status == 2 else 'Pending'),
                    'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else '',
                    'star_level': cleaner.star_level if cleaner else 1,
                    'total_orders': cleaner.total_orders if cleaner else 0,
                    'total_rating': float(cleaner.total_rating) if cleaner and cleaner.total_rating else 5.0,
                    'email': cleaner.email if cleaner else '',
                    'phone': cleaner.phone if cleaner else '',
                    'nationality': cleaner.nationality if cleaner else '',
                    'languages': cleaner.languages if cleaner else '',
                    'bio': cleaner.bio if cleaner else '',
                    'address': cleaner.address if cleaner else '',
                    'avatar_url': cleaner.avatar_url if cleaner else '',
                    'join_date': cleaner.create_time.strftime('%Y-%m-%d') if cleaner and cleaner.create_time else '',
                    'completed_orders': 0,
                    'recent_reviews': []
                }
                if cleaner:
                    completed = self.db.query(ServiceOrderModel).filter(
                        ServiceOrderModel.assigned_staff_id == cleaner.id,
                        ServiceOrderModel.status == 3,
                        ServiceOrderModel.is_deleted == 0
                    ).count()
                    cleaner_data['completed_orders'] = completed
                    reviews = self.db.query(ServiceOrderModel).filter(
                        ServiceOrderModel.assigned_staff_id == cleaner.id,
                        ServiceOrderModel.rating.isnot(None),
                        ServiceOrderModel.is_deleted == 0
                    ).order_by(ServiceOrderModel.actual_complete.desc()).limit(5).all()
                    for review in reviews:
                        guest = self.db.query(UserModel).filter(UserModel.id == review.guest_id).first()
                        cleaner_data['recent_reviews'].append({
                            'rating': self._decode_rating(review.rating),
                            'comment': review.guest_feedback or '',
                            'guest_name': guest.full_name if guest else 'Customer',
                            'create_time': review.actual_complete.strftime('%Y-%m-%d') if review.actual_complete else ''
                        })
                apps_list.append(cleaner_data)

            result.append({
                'id': req.id,
                'order_id': order_id,
                'order_no': order_no,
                'payment_pending': pending_payment,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'guest_address': getattr(req, 'guest_address', None),
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'status_text': self._get_status_text(req.status),
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'is_published': getattr(req, 'is_published', 1),
                'publish_time': req.publish_time.strftime('%Y-%m-%d %H:%M') if getattr(
                    req, 'publish_time', None
                ) else '',
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else '',
                'applications': apps_list
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def approve_cleaner_for_requirement(self, requirement_id: int, cleaner_id: int) -> dict:
        """Customer approves/assigns a cleaner for their requirement"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        if requirement.assigned_cleaner_id:
            return {'success': False, 'message': 'A cleaner has already been assigned'}

        cleaner = self.db.query(UserModel).filter(UserModel.id == cleaner_id).first()
        if not cleaner:
            return {'success': False, 'message': 'Cleaner not found'}

        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == requirement_id,
            CleanerApplicationModel.is_deleted == 0
        ).all()

        for app in applications:
            if app.cleaner_id == cleaner_id:
                app.status = 1
            else:
                app.status = 2

        requirement.assigned_cleaner_id = cleaner_id
        requirement.status = 1

        service_type_id = self._service_type_id_for_requirement(requirement)

        order_no = 'SO' + ''.join(random.choices(string.digits, k=10))
        
        order = ServiceOrderModel(
            order_no=order_no,
            guest_id=requirement.user_id or 0,
            service_type_id=service_type_id,
            requirement_id=requirement_id,
            assigned_staff_id=cleaner_id,
            status=1,
            request_time=datetime.utcnow()
        )
        self.db.add(order)

        notify_user(
            self.db,
            cleaner_id,
            'You were selected by the customer',
            f'Order {order_no} was created for your accepted application.',
            'success',
            '/my-orders',
        )
        if requirement.user_id:
            notify_user(
                self.db,
                requirement.user_id,
                'Order created',
                f'Order {order_no} is assigned to {cleaner.full_name or cleaner.username}.',
                'success',
                '/my-orders',
            )

        self.db.commit()

        return {'success': True, 'message': f'Cleaner {cleaner.full_name or cleaner.username} has been assigned', 'order_id': order.order_id, 'order_no': order_no}

    def get_customer_bookings(self, user_id: int, limit: int = 20, offset: int = 0) -> dict:
        """Get all bookings/orders for a customer with pagination"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == user_id,
            ServiceOrderModel.is_deleted == 0
        )

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
            
            requirement = None
            if order.requirement_id:
                requirement = self.db.query(CustomerRequirementModel).filter(
                    CustomerRequirementModel.id == order.requirement_id,
                    CustomerRequirementModel.is_deleted == 0
                ).first()

            order_data = {
                'id': order.order_id,
                'order_no': order.order_no,
                'service_type': service_type.type_name if service_type else '',
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'assigned_staff_id': order.assigned_staff_id,
                'assigned_staff': self._user_display_name(cleaner),
                'staff_phone': cleaner.phone if cleaner else '',
                'staff_languages': cleaner.languages if cleaner else '',
                'staff_nationality': cleaner.nationality if cleaner else '',
                'rating': self._decode_rating(order.rating),
                'guest_feedback': order.guest_feedback,
                'remarks': order.remarks,
                'service_address': order.service_address,
                'priority': order.priority,
                'scheduled_start': order.scheduled_start.strftime('%Y-%m-%d %H:%M')
                if order.scheduled_start else '',
                'scheduled_end': order.scheduled_end.strftime('%Y-%m-%d %H:%M')
                if order.scheduled_end else '',
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else '',
                'requirement_id': order.requirement_id,
                'requirement': None,
                'payment_amount': self._order_pay_amount_for_guest(order, user_id),
            }
            
            if requirement:
                order_data['requirement'] = {
                    'id': requirement.id,
                    'property_type': requirement.property_type,
                    'bedroom': requirement.bedroom,
                    'bathroom': requirement.bathroom,
                    'living_room': requirement.living_room,
                    'kitchen': requirement.kitchen,
                    'square_footage': requirement.square_footage,
                    'budget': requirement.budget,
                    'preferred_time': requirement.preferred_time,
                    'description': requirement.description,
                    'status': requirement.status,
                    'create_time': requirement.create_time.strftime('%Y-%m-%d %H:%M') if requirement.create_time else ''
                }
            
            result.append(order_data)

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_order_detail(self, order_id: int, user_id: int) -> dict:
        """Get detailed order information for a customer"""
        order = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == order_id,
            ServiceOrderModel.guest_id == user_id,
            ServiceOrderModel.is_deleted == 0
        ).first()
        
        if not order:
            return None
        
        cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
        service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
        
        requirement = None
        if order.requirement_id:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == order.requirement_id,
                CustomerRequirementModel.is_deleted == 0
            ).first()

        payment_rows = self.db.query(TransactionModel).filter(
            TransactionModel.order_id == order_id,
            TransactionModel.user_id == user_id,
            TransactionModel.type == 'payment',
            TransactionModel.is_deleted == 0
        ).order_by(TransactionModel.create_time.desc()).all()

        payment_pending = next((p for p in payment_rows if p.status == 'pending'), None)
        payment_completed = next((p for p in payment_rows if p.status == 'completed'), None)

        payment_info = None
        if payment_completed:
            desc = payment_completed.description or ''
            method = ''
            if ' via ' in desc:
                try:
                    after = desc.split(' via ', 1)[1]
                    method = after.split(' ', 1)[0].strip()
                except (IndexError, ValueError):
                    method = ''
            payment_info = {
                'transaction_id': payment_completed.id,
                'status': 'completed',
                'amount': float(payment_completed.amount) if payment_completed.amount is not None else 0.0,
                'paid_at': payment_completed.create_time.strftime('%Y-%m-%d %H:%M:%S')
                if payment_completed.create_time else '',
                'description': desc,
                'payment_method': method,
            }
        elif payment_pending:
            desc = payment_pending.description or ''
            payment_info = {
                'transaction_id': payment_pending.id,
                'status': 'pending',
                'amount': float(resolve_guest_order_pay_amount(self.db, order, user_id)),
                'paid_at': '',
                'description': desc,
                'payment_method': '',
            }

        return {
            'id': order.order_id,
            'order_no': order.order_no,
            'service_type': service_type.type_name if service_type else '',
            'status': order.status,
            'status_text': self._get_status_text(order.status),
            'assigned_staff_id': order.assigned_staff_id,
            'assigned_staff': self._user_display_name(cleaner),
            'staff_email': cleaner.email if cleaner else '',
            'staff_phone': cleaner.phone if cleaner else '',
            'staff_nationality': cleaner.nationality if cleaner else '',
            'staff_languages': cleaner.languages if cleaner else '',
            'staff_bio': cleaner.bio if cleaner else '',
            'staff_total_rating': float(cleaner.total_rating) if cleaner and cleaner.total_rating else 5.0,
            'staff_star_level': cleaner.star_level if cleaner else 1,
            'rating': self._decode_rating(order.rating),
            'guest_feedback': order.guest_feedback,
            'remarks': order.remarks,
            'service_address': order.service_address or '',
            'priority': order.priority,
            'request_time': order.request_time.strftime('%Y-%m-%d %H:%M') if order.request_time else '',
            'scheduled_start': order.scheduled_start.strftime('%Y-%m-%d %H:%M') if order.scheduled_start else '',
            'scheduled_end': order.scheduled_end.strftime('%Y-%m-%d %H:%M') if order.scheduled_end else '',
            'actual_start': order.actual_start.strftime('%Y-%m-%d %H:%M') if order.actual_start else '',
            'actual_complete': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else '',
            'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
            'requirement_id': order.requirement_id,
            'requirement': {
                'id': requirement.id,
                'property_type': requirement.property_type,
                'bedroom': requirement.bedroom,
                'bathroom': requirement.bathroom,
                'living_room': requirement.living_room,
                'kitchen': requirement.kitchen,
                'lawn': requirement.lawn,
                'car_space': requirement.car_space,
                'square_footage': requirement.square_footage,
                'service_type_name': requirement.service_type_name,
                'budget': requirement.budget,
                'preferred_time': requirement.preferred_time,
                'description': requirement.description,
                'status': requirement.status,
                'create_time': requirement.create_time.strftime('%Y-%m-%d %H:%M') if requirement.create_time else ''
            } if requirement else None,
            'payment': payment_info,
            'payment_amount': self._order_pay_amount_for_guest(order, user_id),
        }

    def get_cleaner_bookings(self, cleaner_id: int, limit: int = 20, offset: int = 0) -> dict:
        """Get all bookings/orders for a cleaner (assigned to this cleaner)"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        )

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
            
            requirement = None
            if order.requirement_id:
                requirement = self.db.query(CustomerRequirementModel).filter(
                    CustomerRequirementModel.id == order.requirement_id,
                    CustomerRequirementModel.is_deleted == 0
                ).first()

            order_data = {
                'id': order.order_id,
                'order_no': order.order_no,
                'service_type': service_type.type_name if service_type else '',
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'guest_id': order.guest_id,
                'guest_name': self._user_display_name(guest),
                'guest_phone': guest.phone if guest else '',
                'guest_email': guest.email if guest else '',
                'rating': self._decode_rating(order.rating),
                'guest_feedback': order.guest_feedback,
                'remarks': order.remarks,
                'service_address': order.service_address or '',
                'priority': order.priority,
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'scheduled_start': order.scheduled_start.strftime('%Y-%m-%d %H:%M') if order.scheduled_start else '',
                'scheduled_end': order.scheduled_end.strftime('%Y-%m-%d %H:%M') if order.scheduled_end else '',
                'actual_start': order.actual_start.strftime('%Y-%m-%d %H:%M') if order.actual_start else '',
                'actual_complete': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else '',
                'requirement_id': order.requirement_id,
                'requirement': None
            }
            
            if requirement:
                order_data['requirement'] = {
                    'id': requirement.id,
                    'property_type': requirement.property_type,
                    'bedroom': requirement.bedroom,
                    'bathroom': requirement.bathroom,
                    'living_room': requirement.living_room,
                    'kitchen': requirement.kitchen,
                    'lawn': requirement.lawn,
                    'car_space': requirement.car_space,
                    'square_footage': requirement.square_footage,
                    'service_type_name': requirement.service_type_name,
                    'budget': requirement.budget,
                    'preferred_time': requirement.preferred_time,
                    'description': requirement.description,
                    'status': requirement.status,
                    'create_time': requirement.create_time.strftime('%Y-%m-%d %H:%M') if requirement.create_time else ''
                }
            
            result.append(order_data)

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_cleaner_order_detail(self, order_id: int, cleaner_id: int) -> dict:
        """Get detailed order information for a cleaner"""
        order = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == order_id,
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        ).first()
        
        if not order:
            return None
        
        guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
        service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()
        
        requirement = None
        if order.requirement_id:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == order.requirement_id,
                CustomerRequirementModel.is_deleted == 0
            ).first()
        
        return {
            'id': order.order_id,
            'order_no': order.order_no,
            'service_type': service_type.type_name if service_type else '',
            'status': order.status,
            'status_text': self._get_status_text(order.status),
            'guest_id': order.guest_id,
            'guest_name': self._user_display_name(guest),
            'guest_phone': guest.phone if guest else '',
            'guest_email': guest.email if guest else '',
            'rating': self._decode_rating(order.rating),
            'guest_feedback': order.guest_feedback,
            'remarks': order.remarks,
            'service_address': order.service_address or '',
            'priority': order.priority,
            'request_time': order.request_time.strftime('%Y-%m-%d %H:%M') if order.request_time else '',
            'scheduled_start': order.scheduled_start.strftime('%Y-%m-%d %H:%M') if order.scheduled_start else '',
            'scheduled_end': order.scheduled_end.strftime('%Y-%m-%d %H:%M') if order.scheduled_end else '',
            'actual_start': order.actual_start.strftime('%Y-%m-%d %H:%M') if order.actual_start else '',
            'actual_complete': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else '',
            'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
            'requirement_id': order.requirement_id,
            'requirement': {
                'id': requirement.id,
                'property_type': requirement.property_type,
                'bedroom': requirement.bedroom,
                'bathroom': requirement.bathroom,
                'living_room': requirement.living_room,
                'kitchen': requirement.kitchen,
                'lawn': requirement.lawn,
                'car_space': requirement.car_space,
                'square_footage': requirement.square_footage,
                'service_type_name': requirement.service_type_name,
                'budget': requirement.budget,
                'preferred_time': requirement.preferred_time,
                'description': requirement.description,
                'status': requirement.status,
                'create_time': requirement.create_time.strftime('%Y-%m-%d %H:%M') if requirement.create_time else ''
            } if requirement else None
        }
