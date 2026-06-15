# Hotel Housekeeping Management System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen)](https://vuejs.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-blueviolet)](https://www.sqlalchemy.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)](https://www.mysql.com/)

## Project Description

This is a comprehensive **Hotel Housekeeping Management System** built with FastAPI, Vue.js, SQLAlchemy, and MySQL. The system simulates a real-world cleaning service platform that connects customers, cleaners, and administrators through a complete and structured business workflow.

Key features include:
- User registration and login with JWT authentication and Two-Factor Authentication (2FA).
- Service catalog management with pricing, descriptions, and service details.
- Customer requirements posting and cleaner applications.
- Service order creation, assignment, and tracking.
- Quality inspection and scoring system.
- Virtual wallet and payment processing.
- Complaint handling with evidence submission.
- Role-Based Access Control (RBAC) for Customer, Cleaner, and Admin roles.
- Soft deletes and audit timestamps on all entities.

## Features

### User Management
- Registration and login with JWT authentication.
- Optional Two-Factor Authentication (TOTP) during registration.
- Role assignment (Customer, Cleaner, Admin).
- Profile management with ratings and statistics.

### Service Management
- Service types with pricing and descriptions.
- Service details with step-by-step processes.
- Customer requirements posting with property details.
- Cleaner applications for posted requirements.

### Order Processing
- Service booking with date/time scheduling.
- Automatic cleaner assignment or manual assignment by admin.
- Order status tracking: Pending → Assigned → In Progress → Completed.
- Before/after photo uploads for service verification.

### Quality Inspection
- Inspector reviews completed services.
- Scoring system (threshold-based pass/fail).
- Reinspection workflow for failed inspections.
- Cleaners can be reassigned for failed inspections.

### Payment and Wallet
- Virtual wallet system for customers and cleaners.
- Automatic fee calculation based on service type.
- Transaction history and balance tracking.
- Wallet balance management.

### Complaint Handling
- Customer complaint submission with evidence.
- Admin review and resolution process.
- Multiple resolution types: full refund, partial compensation, or closure.

### Role-Based Access Control (RBAC)
- Roles: Customer (Guest), Cleaner, Admin, Manager.
- Permissions linked to roles and menus.
- API-level access control.
- Flexible authorization framework.

### Notifications
- In-app notification system.
- Notifications triggered on order status changes, applications, and complaints.

## Architecture

The system follows a **layered architecture** design:
![Architecture](/submit/tech_architecture.jpg "Architecture")

### Design Patterns

- **Dependency Injection**: FastAPI's `Depends()` for service and database injection.
- **Observer Pattern**: Implemented for notifications on status changes.
- **Repository Pattern**: CRUD operations abstracted in service layer.
- **Factory Pattern**: Database connection factory for different environments.

### ER Diagram

The complete database entity-relationship diagram.
![db_design](/submit/db_design.jpg "db_design")

### Business Flow

The complete business workflow diagrams.
![business_architeture](/submit/business_architeture.jpg "business_architeture")

## Database Design

The database is designed for a **hotel housekeeping management system** following **3NF (Third Normal Form)**:

### Core Tables
- **`user`**: User profiles with authentication, ratings, and statistics.
- **`service_type`**: Service catalog with pricing information.
- **`service_order`**: Service orders with scheduling, status, and assignment.
- **`customer_requirement`**: Customer-posted cleaning requirements.
- **`cleaner_application`**: Cleaner responses to requirements.

### RBAC Tables
- **`role`**: User roles (Customer, Cleaner, Admin, Manager).
- **`permission`**: Granular permissions (e.g., `service_type:read`, `order:create`).
- **`menu`**: UI navigation structure.
- **`user_role`, `role_permission`, `role_menu`**: Relationship tables.

### Finance Tables
- **`wallet`**: User virtual balances.
- **`transaction`**: Payment records linked to orders.

### Support Tables
- **`complaint`**: Customer complaint records with evidence.
- **`inspection`**: Service quality inspections.
- **`notification`**: User notifications.

All tables include `is_deleted`, `create_time`, and `modify_time` fields for auditability and soft deletes.

See `docs/er_diagram.md` for the complete ER diagram.

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/Percy-MSE800/MSE800_Assessment_2.git
cd MSE800_Assessment_2
```

2. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd src
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# backend/.env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=housekeeping_new
```

5. Create database:
```sql
CREATE DATABASE housekeeping_new CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. Initialize database:
```bash
python -m init_db
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Development Mode

**Backend:**
```bash
cd backend/src
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5174` with API proxy to backend.

### Production Mode

1. Build frontend:
```bash
cd frontend
npm run build
```

2. Configure Nginx:

```nginx
# /etc/nginx/conf.d/housekeeping.conf
server {
    listen 80;
    server_name 32.192.68.2;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /var/www/housekeeping/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

3. Start backend:
```bash
cd backend/src
nohup python -m uvicorn app:app --host 0.0.0.0 --port 8000 > /var/log/housekeeping.log 2>&1 &
```

## API Documentation

Access Swagger UI for interactive API documentation:
- **URL**: `http://localhost:8000/docs` (development)
- **URL**: `http://32.192.68.2/docs` (production)
- **Redoc**: `http://localhost:8000/redoc`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login/json` | POST | User login (JSON) |
| `/api/auth/register` | POST | User registration |
| `/api/auth/verify-2fa` | POST | Two-factor verification |
| `/api/portal/services` | GET | List service types |
| `/api/portal/order` | POST | Create service order |
| `/api/portal/requirements` | GET | Browse requirements |
| `/api/portal/cleaners` | GET | List cleaners |
| `/api/portal/apply` | POST | Apply for requirement |
| `/api/complaint` | POST | Submit complaint |
| `/api/wallet/balance` | GET | Get wallet balance |

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Guest | guest | admin123 |
| Cleaner | cleaner1 | admin123 |

## Use Examples

### Register a User
```json
POST /api/auth/register
{
    "username": "newuser",
    "password": "securepassword",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "guest"
}
```

### Login
```json
POST /api/auth/login/json
{
    "username": "guest",
    "password": "admin123"
}
```

### Create Service Order
```json
POST /api/portal/order
Headers: Authorization: Bearer <token>
{
    "service_type_id": 1,
    "guest_name": "John Doe",
    "guest_phone": "+1234567890",
    "guest_email": "john@example.com",
    "service_address": "123 Main St",
    "scheduled_time": "2026-03-25T10:00:00",
    "scheduled_duration_hours": 2,
    "remarks": "Please clean the living room",
    "priority": 0
}
```

### Browse Requirements
```
GET /api/portal/requirements
```

### Apply for Requirement
```json
POST /api/portal/apply
Headers: Authorization: Bearer <token>
{
    "requirement_id": 1,
    "cleaner_id": 4,
    "cleaner_name": "John Smith",
    "offered_price": 80.00,
    "message": "I can complete this task"
}
```

## Documentation

Additional documentation available in the `submit/` directory:

- `db_design.jpg` - Database entity-relationship diagram
- `business_flow.jpg` - Business workflow diagrams
- `business_architecture.jpg` - Business architecture overview
- `tech_architecture.jpg` - Technical architecture
- `maintenance_support.pdf` - Maintenance and support guide

## Testing

Run backend tests:
```bash
cd backend/src
pytest
```

Test API endpoints:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"admin123"}'

# Get services
curl http://localhost:8000/api/portal/services

# Get requirements
curl http://localhost:8000/api/portal/requirements
```

## License

This project is for academic purposes (MSE800 Assessment 2).

## Author

- **Qingchao Li / Worarat Suwanwattana**
- **Email**: 270758686@yoobeestudent.ac.nz /270718902@yoobeestudent.ac.nz
