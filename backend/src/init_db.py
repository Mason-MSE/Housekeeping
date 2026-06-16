# init_db.py - MySQL database initialization
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from database import engine
from model.Base import Base
from model.complaint import ComplaintEvidenceModel, ComplaintModel


def ensure_portal_schema_extensions() -> None:
    """Add columns used by portal admin / customer publish flows if missing (idempotent)."""
    try:
        with engine.begin() as conn:
            def _has_column(table: str, column: str) -> bool:
                """Check whether a column exists in the given table."""
                q = text(
                    """
                    SELECT COUNT(*) FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = :t AND COLUMN_NAME = :c
                    """
                )
                return bool(conn.execute(q, {'t': table, 'c': column}).scalar())

            if not _has_column('service_type', 'market_price'):
                conn.execute(
                    text('ALTER TABLE service_type ADD COLUMN market_price DECIMAL(10,2) NULL AFTER price')
                )
                print('[init] Added service_type.market_price')
            if not _has_column('customer_requirement', 'is_published'):
                conn.execute(
                    text(
                        'ALTER TABLE customer_requirement ADD COLUMN is_published INT NOT NULL DEFAULT 1 '
                        'AFTER assigned_cleaner_id'
                    )
                )
                print('[init] Added customer_requirement.is_published')
            if not _has_column('customer_requirement', 'publish_time'):
                conn.execute(
                    text(
                        'ALTER TABLE customer_requirement ADD COLUMN publish_time DATETIME NULL '
                        'AFTER is_published'
                    )
                )
                print('[init] Added customer_requirement.publish_time')
            if not _has_column('customer_requirement', 'guest_address'):
                conn.execute(
                    text(
                        'ALTER TABLE customer_requirement ADD COLUMN guest_address VARCHAR(500) NULL '
                        'AFTER guest_email'
                    )
                )
                print('[init] Added customer_requirement.guest_address')
            if not _has_column('service_order', 'service_address'):
                conn.execute(
                    text(
                        'ALTER TABLE service_order ADD COLUMN service_address VARCHAR(500) NULL '
                        "COMMENT 'On-site address (portal / home cleaning)'"
                    )
                )
                print('[init] Added service_order.service_address')
            if not _has_column('service_order', 'requirement_id'):
                conn.execute(
                    text(
                        'ALTER TABLE service_order ADD COLUMN requirement_id INT NULL '
                        "COMMENT 'Linked customer_requirement when applicable' AFTER service_type_id"
                    )
                )
                print('[init] Added service_order.requirement_id')
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f'[init] Warning: portal schema extensions: {exc}')


def ensure_cleaning_services_rbac() -> None:
    """Register cleaning_service permissions, API rows, menu, and role grants (idempotent).

    Mirrors ``sql/add_cleaning_services_rbac.sql`` so portal/menu and ``/api/service-type`` use RBAC.
    """
    sql_path = Path(__file__).resolve().parent / 'sql' / 'add_cleaning_services_rbac.sql'
    if not sql_path.is_file():
        print('[init] Skipping cleaning services RBAC: sql/add_cleaning_services_rbac.sql missing')
        return
    try:
        raw = sql_path.read_text(encoding='utf-8')
        statements: list[str] = []
        for chunk in raw.split(';'):
            lines: list[str] = []
            for line in chunk.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('--'):
                    continue
                lines.append(line)
            stmt = '\n'.join(lines).strip()
            if stmt:
                statements.append(stmt)
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
        print('[init] Cleaning services RBAC ensured')
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f'[init] Warning: cleaning services RBAC: {exc}')


def ensure_complaint_tables() -> None:
    """Create ``complaint`` and ``complaint_evidence`` in the active DB if they do not exist.

    Uses the same ``DB_NAME`` as ``database.py`` (e.g. housekeeping_new). Safe to call on every
    startup (CREATE IF NOT EXISTS semantics via SQLAlchemy checkfirst).
    """
    try:
        Base.metadata.create_all(
            bind=engine,
            tables=[ComplaintModel.__table__, ComplaintEvidenceModel.__table__],
        )
        print('[init] Complaint tables ready: complaint, complaint_evidence')
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f'[init] Warning: could not ensure complaint tables: {exc}')


def init_database():
    """
    Initialize the MySQL database with tables and initial data.
    """
    ensure_complaint_tables()
    ensure_portal_schema_extensions()
    ensure_cleaning_services_rbac()

    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if initial data already exists
        user_count = db.execute(text("SELECT COUNT(*) FROM user")).scalar()
        if user_count > 0:
            print("Initial data already exists, skipping...")
            return

        # Insert initial data
        # Insert roles
        db.execute(text("""
            INSERT INTO role (role_name) VALUES ('admin'), ('cleaner'), ('guest')
        """))

        # Insert test users (password will be hashed by the application)
        db.execute(text("""
            INSERT INTO user (username, password, full_name, email, phone, role, status)
            VALUES ('admin', 'admin123', 'System Admin', 'admin@hotel.com', '13800000000', 'admin', 1),
                   ('cleaner1', 'admin123', 'Cleaner Zhang San', 'cleaner1@hotel.com', '13900000001', 'cleaner', 1),
                   ('cleaner2', 'admin123', 'Cleaner Li Si', 'cleaner2@hotel.com', '13900000002', 'cleaner', 1),
                   ('guest1', 'admin123', 'Zhang San', 'zhangsan@email.com', '13800000001', 'guest', 1)
        """))

        # Insert user roles
        db.execute(text("""
            INSERT INTO user_role (user_id, role_id) VALUES
            (1, 1),  -- admin user -> admin role
            (2, 2),  -- cleaner1 -> cleaner role
            (3, 2),  -- cleaner2 -> cleaner role
            (4, 3)   -- guest1 -> guest role
        """))

        # Insert rooms
        db.execute(text("""
            INSERT INTO room (room_number, floor, room_type, capacity, price, status)
            VALUES ('1001', 1, 'Single Room', 1, 199.00, 0),
                   ('1002', 1, 'Double Room', 2, 299.00, 1),
                   ('1003', 1, 'Single Room', 1, 199.00, 2),
                   ('1004', 1, 'Suite', 3, 599.00, 3),
                   ('2001', 2, 'Double Room', 2, 299.00, 0),
                   ('2002', 2, 'Double Room', 2, 299.00, 1),
                   ('2003', 2, 'Suite', 3, 599.00, 0),
                   ('3001', 3, 'Deluxe Suite', 4, 999.00, 0)
        """))

        # Insert service types
        db.execute(text("""
            INSERT INTO service_type (type_name, description, standard_time, price)
            VALUES ('Regular Cleaning', 'Standard room cleaning service', 30, 50.00),
                   ('Deep Cleaning', 'Comprehensive deep cleaning', 60, 100.00),
                   ('Bed Sheet Change', 'Replace bed sheets and covers', 15, 20.00),
                   ('Express Cleaning', 'Priority handling', 20, 80.00)
        """))

        # Insert inventory
        db.execute(text("""
            INSERT INTO inventory_item (item_name, category, quantity, min_stock, unit)
            VALUES ('Towel', 'Textile', 150, 50, 'piece'),
                   ('Bed Sheet', 'Textile', 80, 30, 'piece'),
                   ('Toothbrush', 'Toiletries', 200, 100, 'piece'),
                   ('Shampoo', 'Toiletries', 45, 50, 'bottle'),
                   ('Tissue Paper', 'Cleaning Supplies', 300, 100, 'box'),
                   ('Disinfectant', 'Cleaning Supplies', 25, 20, 'bottle')
        """))

        # Insert resources (API endpoints)
        db.execute(text("""
            INSERT INTO resource (resource_name, resource_link, resource_method) VALUES
            -- Auth
            ('Auth:login', '/api/auth/login', 'POST'),
            ('Auth:login-json', '/api/auth/login/json', 'POST'),
            ('Auth:logout', '/api/auth/logout', 'POST'),
            ('Auth:refresh', '/api/auth/refresh', 'POST'),
            
            -- User
            ('User:list', '/api/user/', 'GET'),
            ('User:create', '/api/user/', 'POST'),
            ('User:update', '/api/user/{user_id}', 'PUT'),
            ('User:delete', '/api/user/{user_id}', 'DELETE'),
            ('User:get', '/api/user/{user_id}', 'GET'),
            ('User:by-role', '/api/user/role/{role}', 'GET'),
            ('User:me', '/api/user/me', 'GET'),
            ('User:update-me', '/api/user/me', 'PUT'),
            ('User:2fa-status', '/api/user/me/2fa-status', 'GET'),
            ('User:enable-2fa', '/api/user/me/enable-2fa', 'POST'),
            ('User:verify-2fa', '/api/user/me/verify-2fa', 'POST'),
            ('User:disable-2fa', '/api/user/me/disable-2fa', 'POST'),
            ('User:role-resources', '/api/user/me/role-resources', 'GET'),
            ('User:change-password', '/api/user/change-password', 'POST'),
            ('User:manage', '/api/user/manage', 'POST'),
            
            -- Service Order
            ('ServiceOrder:list', '/api/service-order/', 'GET'),
            ('ServiceOrder:create', '/api/service-order/', 'POST'),
            ('ServiceOrder:update', '/api/service-order/{order_id}', 'PUT'),
            ('ServiceOrder:delete', '/api/service-order/{order_id}', 'DELETE'),
            ('ServiceOrder:get', '/api/service-order/{order_id}', 'GET'),
            ('ServiceOrder:paginated', '/api/service-order/paginated', 'POST'),
            ('ServiceOrder:assign', '/api/service-order/assign/{order_id}', 'POST'),
            ('ServiceOrder:start', '/api/service-order/start/{order_id}', 'POST'),
            ('ServiceOrder:complete', '/api/service-order/complete/{order_id}', 'POST'),
            ('ServiceOrder:rate', '/api/service-order/rate/{order_id}', 'POST'),
            
            -- Room
            ('Room:list', '/api/room/', 'GET'),
            ('Room:create', '/api/room/', 'POST'),
            ('Room:update', '/api/room/{room_id}', 'PUT'),
            ('Room:delete', '/api/room/{room_id}', 'DELETE'),
            ('Room:get', '/api/room/{room_id}', 'GET'),
            ('Room:paginated', '/api/room/paginated', 'POST'),
            
            -- Service Type
            ('ServiceType:list', '/api/service-type/', 'GET'),
            ('ServiceType:create', '/api/service-type/', 'POST'),
            ('ServiceType:update', '/api/service-type/{type_id}', 'PUT'),
            ('ServiceType:delete', '/api/service-type/{type_id}', 'DELETE'),
            
            -- Inventory
            ('Inventory:list', '/api/inventory/', 'GET'),
            ('Inventory:create', '/api/inventory/', 'POST'),
            ('Inventory:update', '/api/inventory/{item_id}', 'PUT'),
            ('Inventory:delete', '/api/inventory/{item_id}', 'DELETE'),
            ('Inventory:paginated', '/api/inventory/paginated', 'POST'),
            
            -- Wallet
            ('Wallet:get', '/api/wallet/', 'GET'),
            ('Wallet:recharge', '/api/wallet/recharge', 'POST'),
            ('Wallet:transactions', '/api/wallet/transactions', 'GET'),
            
            -- Notification
            ('Notification:list', '/api/notification/', 'GET'),
            ('Notification:create', '/api/notification/', 'POST'),
            ('Notification:mark-read', '/api/notification/{notification_id}/read', 'POST'),
            ('Notification:delete', '/api/notification/{id}', 'DELETE'),
            ('Notification:unread-count', '/api/notification/unread-count', 'GET'),
            
            -- Portal
            ('Portal:services', '/api/portal/services', 'GET'),
            ('Portal:rooms', '/api/portal/rooms', 'GET'),
            ('Portal:stats', '/api/portal/stats', 'GET'),
            ('Portal:cleaners', '/api/portal/cleaners', 'GET'),
            ('Portal:requirements', '/api/portal/requirements', 'GET'),
            ('Portal:my-requirements', '/api/portal/my-requirements', 'GET'),
            ('Portal:create-requirement', '/api/portal/requirements', 'POST'),
            ('Portal:admin-requirements', '/api/portal/admin/requirements', 'GET'),
            ('Portal:admin-cleaners', '/api/portal/admin/cleaners', 'GET'),
            ('Portal:assign-requirement', '/api/portal/admin/assign-requirement', 'POST'),
            ('Portal:delete-requirement', '/api/portal/admin/requirement/{requirement_id}', 'DELETE'),
            ('Portal:hide-requirement', '/api/portal/admin/requirement/{requirement_id}/hide', 'POST'),
            ('Portal:company-info', '/api/portal/company-info', 'GET'),
            ('Portal:cleaner-tasks', '/api/portal/admin/tasks', 'GET'),
            
            -- Report
            ('Report:stats', '/api/report/stats', 'GET'),
            ('Report:revenue', '/api/report/revenue', 'GET'),
            ('Report:orders', '/api/report/orders', 'GET'),
            ('Report:cleaners', '/api/report/cleaners', 'GET')
        """))

        # Insert role resources
        # Admin role (role_id=1) gets all resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id)
            SELECT 1, id FROM resource
        """))

        # Cleaner role (role_id=2) gets limited resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id) VALUES
            (2, 5),   -- Auth:login
            (2, 6),   -- Auth:login-json
            (2, 25),  -- ServiceOrder:list
            (2, 31),  -- ServiceOrder:start
            (2, 32),  -- ServiceOrder:complete
            (2, 33),  -- ServiceOrder:rate
            (2, 34),  -- Room:list
            (2, 35),  -- Room:create
            (2, 37),  -- Room:get
            (2, 45),  -- ServiceType:list
            (2, 51),  -- Wallet:get
            (2, 52),  -- Wallet:recharge
            (2, 53),  -- Wallet:transactions
            (2, 54),  -- Notification:list
            (2, 57),  -- Notification:delete
            (2, 60),  -- Portal:my-requirements
            (2, 62),  -- Portal:create-requirement
            (2, 69),  -- Portal:company-info
            (2, 70)   -- Portal:cleaner-tasks
        """))

        # Guest role (role_id=3) gets limited resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id) VALUES
            (3, 5),   -- Auth:login
            (3, 6),   -- Auth:login-json
            (3, 25),  -- ServiceOrder:list
            (3, 26),  -- ServiceOrder:create
            (3, 34),  -- Room:list
            (3, 37),  -- Room:get
            (3, 45),  -- ServiceType:list
            (3, 51),  -- Wallet:get
            (3, 52),  -- Wallet:recharge
            (3, 53),  -- Wallet:transactions
            (3, 54),  -- Notification:list
            (3, 57),  -- Notification:delete
            (3, 60),  -- Portal:my-requirements
            (3, 62),  -- Portal:create-requirement
            (3, 69)   -- Portal:company-info
        """))

        db.commit()
        print("MySQL database initialized successfully with initial data!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
