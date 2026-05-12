## Important Notice for Users

### Keeping the Boilerplate Updated

This boilerplate is a living project that requires regular updates to maintain its effectiveness and security. As a Backend Python Developer using this boilerplate, it is your responsibility to contribute to its maintenance and improvement.

**Required Contributions:**
- Security patches
- Dependency updates
- Bug fixes
- Feature enhancements
- Documentation updates

Submit your updates via Pull Requests with clear descriptions of changes. The repository administrators will review and merge valid contributions.

# Django Project Boilerplate

A production-ready Django boilerplate with pre-configured settings for AWS S3, PostgreSQL, Redis, CORS, and comprehensive security features.

## Table of Contents
- [Features](#features)
  - [Core](#core)
  - [Security](#security)
  - [User Management](#user-management)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup](#docker-setup)
- [Admin Panel](#admin-panel)
- [API Endpoints](#api-endpoints)
  - [Authentication & Accounts](#authentication--accounts)
  - [Products](#products)
  - [Warehouses](#warehouses)
  - [Inventory](#inventory)
  - [Orders](#orders)
  - [Notifications](#notifications)
  - [Audit Logs](#audit-logs)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [AWS S3 Configuration](#aws-s3-configuration)
  - [CORS Configuration](#cors-configuration)
- [Development Guidelines](#development-guidelines)
- [Production Deployment](#production-deployment)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

## Features

### Core
- Django 5.1.5
- Django REST Framework
- PostgreSQL database
- AWS S3 integration for static and media files
- Redis for caching
- Structured API versioning
- Docker and Docker Compose support

### Security
- Token-based authentication
- Rate limiting (Anonymous and User-based)
- CORS configuration
- Structured project layout

### User Management
- Custom User model
- Username based authentication
- Registration and authentication APIs
- User profile management
- Token-based session handling

## Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- AWS Account (for S3)
- Docker (optional)

## Project Structure
```
├── accounts/                   # User management app
│   ├── api/                    # API endpoints
│   │   └── v1/                 # Version 1 APIs
│   │       ├── __init__.py
│   │       ├── serializers.py  # Request/Response serializers
│   │       ├── urls.py         # API URL routing
│   │       └── views.py        # API view logic
│   ├── managers.py             # Custom user manager
│   ├── models.py               # User model
│   └── urls.py                 # Main app URL routing
├── base/                       # Main application directory
├── core/                       # Project configuration
│   ├── middleware/             # Custom middleware
│   ├── api_urls.py             # Global API URL routing
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI configuration
├── logs/                       # Application logs
├── .env.example                # Environment variables template
├── .env                        # Main Environment variables
├── requirements.txt            # Project dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
└── manage.py                   # Django management script
└── README.md                   # Project documentation
```


## Quick Start

### Local Development Setup

1. Clone and setup repository:
```bash
# Clone the boilerplate
git clone [repository-url] your-project-name
cd your-project-name

# Remove existing git repository
rm -rf .git

# Initialize new git repository
git init

# Create initial commit
git add .
git commit -m "Initial commit from boilerplate"

# Add your remote repository
git remote add origin your-repository-url
git branch -M main
git push -u origin main
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
```
Edit `.env` with your specific configuration.

5. Setup PostgreSQL database:
```bash
# Create database
createdb dj_boilerplate
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

### Docker Setup

1. Configure environment variables in `.env`

2. Build and run:
```bash
docker-compose up --build
```

## Admin Panel

The Django Admin panel is accessible at:

```
http://localhost:8000/admin/
```

It uses [Jazzmin](https://django-jazzmin.readthedocs.io/) for an enhanced UI. Log in with your superuser credentials.

**Models available in Admin:**

| Section | URL |
|---|---|
| Users | `/admin/accounts/user/` |
| Products | `/admin/products/product/` |
| Warehouses | `/admin/warehouses/warehouse/` |
| Inventory | `/admin/inventory/inventory/` |
| Orders (with inline items) | `/admin/orders/order/` |
| Notifications | `/admin/notifications/notification/` |
| Audit Logs | `/admin/audit_logs/auditlog/` |

---

## API Endpoints

Base URL pattern: `/api/<app>/v1/`

**Authentication:** Token-based. Include `Authorization: Token <your-token>` header on protected routes.

**Rate Limits:**
- Anonymous users: 100 requests/day
- Authenticated users: 1000 requests/day

---

### Authentication & Accounts

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/accounts/v1/register/` | Register a new user | No |
| POST | `/api/accounts/v1/login/` | Login and receive auth token | No |
| POST | `/api/accounts/v1/logout/` | Logout (invalidates token) | Yes |
| GET | `/api/accounts/v1/profile/` | Get current user profile | Yes |
| PATCH | `/api/accounts/v1/profile/` | Update current user profile | Yes |

---

### Products

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/products/v1/` | List all products (paginated, filterable, searchable) | No |
| POST | `/api/products/v1/` | Create a product | Admin only |
| GET | `/api/products/v1/{id}/` | Retrieve a product | No |
| PUT | `/api/products/v1/{id}/` | Update a product | Admin only |
| PATCH | `/api/products/v1/{id}/` | Partial update a product | Admin only |
| DELETE | `/api/products/v1/{id}/` | Delete a product | Admin only |

> Product list results are Redis-cached for performance.

---

### Warehouses

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/warehouses/v1/` | List all warehouses | Admin only |
| POST | `/api/warehouses/v1/` | Create a warehouse | Admin only |
| GET | `/api/warehouses/v1/{id}/` | Retrieve a warehouse | Admin only |
| PUT | `/api/warehouses/v1/{id}/` | Update a warehouse | Admin only |
| PATCH | `/api/warehouses/v1/{id}/` | Partial update a warehouse | Admin only |
| DELETE | `/api/warehouses/v1/{id}/` | Delete a warehouse | Admin only |

---

### Inventory

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/inventory/v1/` | List inventory (filterable by `warehouse` and `product`) | Admin only |
| POST | `/api/inventory/v1/` | Create an inventory record | Admin only |
| GET | `/api/inventory/v1/{id}/` | Retrieve an inventory record | Admin only |
| PUT | `/api/inventory/v1/{id}/` | Update an inventory record | Admin only |
| PATCH | `/api/inventory/v1/{id}/` | Partial update an inventory record | Admin only |
| DELETE | `/api/inventory/v1/{id}/` | Delete an inventory record | Admin only |

---

### Orders

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/orders/v1/` | List orders (users see own; admins see all) | Yes |
| POST | `/api/orders/v1/` | Place a new order | Yes |
| GET | `/api/orders/v1/{id}/` | Retrieve an order | Yes |
| PATCH | `/api/orders/v1/{id}/status/` | Update order status | Admin only |

**Order status transitions:**

```
PENDING → CONFIRMED
PENDING → CANCELLED
CONFIRMED → COMPLETED
```

`CANCELLED` and `COMPLETED` are terminal states — no further transitions allowed.

---

### Notifications

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/notifications/v1/` | List notifications for the authenticated user | Yes |

---

### Audit Logs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/audit-logs/v1/` | List audit logs (users see logs for their orders; admins see all) | Yes |

## Configuration

### Environment Variables
```plaintext
# Core
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOST=your-domain

# Database
DATABASE_NAME=dj_boilerplate
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# AWS
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=your-region
```

## AWS S3 Configuration

1. Create an S3 bucket in AWS Console
2. Configure IAM user with the following S3 permissions:
   - `s3:ListBucket` / `s3:GetBucketLocation` on the bucket ARN
   - `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:HeadObject` on `bucket/*`
3. Update `.env` with AWS credentials
4. Run collectstatic to upload static files directly to S3:
```bash
python manage.py collectstatic --noinput
```

> **Note (Django 5.1+):** The legacy `STATICFILES_STORAGE` and `DEFAULT_FILE_STORAGE` settings are deprecated.
> This boilerplate uses the modern `STORAGES` dictionary in `settings.py`:
> ```python
> STORAGES = {
>     "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
>     "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
> }
> ```

## CORS Configuration

CORS is pre-configured to allow all origins in development. For production:

1. Set `CORS_ALLOW_ALL_ORIGINS = False` in settings.py
2. Configure specific origins:
```python
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
]
```

### Logging
- Rotating file logs
- Console logging

## Development Guidelines

1. API Versioning:
   - Place new API versions in appropriate version folders
   - Follow the established pattern in `accounts/api/v1/`

2. Security:
   - Always use environment variables for sensitive data
   - Implement rate limiting for new endpoints
   - Add appropriate authentication classes

3. Error Handling:
   - Use try-except blocks with proper logging
   - Return appropriate HTTP status codes
   - Follow DRF exception handling patterns

## Production Deployment

1. Security Checklist:
   - Set `DEBUG=False`
   - Configure allowed hosts
   - Enable HTTPS
   - Set proper CORS origins
   - Configure proper AWS permissions

2. Performance:
   - Enable Redis caching
   - Configure proper logging levels
   - Set appropriate rate limits

3. Monitoring:
   - Configure error logging
   - Setup request logging
   - Monitor resource usage

## Changelog

### v1.1.0 — 2026-05-03

#### 🚀 Improvements
- **AWS S3 Static Files** — Migrated from the deprecated `STATICFILES_STORAGE` / `DEFAULT_FILE_STORAGE` settings to the modern Django 5.1 `STORAGES` dictionary. Static files now upload directly to S3 via `collectstatic`.
- **S3 Compatibility** — Set `AWS_DEFAULT_ACL = None` and `AWS_S3_SIGNATURE_VERSION = 's3v4'` to resolve `403 Forbidden` errors on newer AWS regions (e.g. `eu-north-1`).
- **Init File** — Created `base/models/__init__.py` for importing purposes.


## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Author

- Parikshit Rathore
- Senior Software Engineer
- Dianapps

## Acknowledgments

- Django
- Django REST Framework
- Other contributors

