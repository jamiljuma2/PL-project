# Assignment Marketplace Backend (Django + DRF)

API-first backend powering a frontend-only assignment marketplace connecting students, writers, and admins.

## Tech Stack
- Django 4.2 LTS, DRF
- PostgreSQL (SQLite dev), JWT (SimpleJWT)
- Celery + Redis (optional)
- File storage: local dev, S3-compatible prod
- Whitenoise (static), Gunicorn (Linux prod)
- Lipana M-Pesa STK Push

## Setup
1. Update `.env` with PostgreSQL + S3 + Email config.
2. Install deps in venv (already installed in this workspace).
3. Run migrations and start server.

```bash
# Windows
C:/Users/jumaj/OneDrive/Desktop/PL-Project/.venv/Scripts/python.exe manage.py migrate
C:/Users/jumaj/OneDrive/Desktop/PL-Project/.venv/Scripts/python.exe manage.py runserver
```

## Environment
See [.env](.env). Key vars: `SECRET_KEY`, `DB_*` (PostgreSQL), `DEFAULT_FILE_STORAGE` (S3), `AWS_*`, `CELERY_*`, `LIPANA_*`, `EMAIL_*`, `ALLOWED_FILE_EXTENSIONS`, `MAX_FILE_SIZE_MB`.

## Apps & Modules
- `accounts`: custom `User` with roles, `Wallet`, `Rating`, `Notification`, auth endpoints
- `assignments`: `Assignment`, `AssignmentFile`, `TaskClaim`, `Submission`
- `subscriptions`: writer subscriptions with daily claim limits
- `payments`: wallet ledger, Lipana integration and callback
- `adminpanel`: admin APIs and action logs

## Auth Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/refresh
- POST /api/auth/password-reset
- POST /api/auth/verify-email
- GET  /api/auth/me
- GET  /api/ratings/me

## Student APIs
- POST /api/assignments/
- GET  /api/assignments/my
- GET  /api/wallet/
- POST /api/wallet/topup
- GET  /api/notifications/

## Writer APIs
- POST /api/subscriptions/pay
- GET  /api/subscriptions/status
- GET  /api/tasks/available
- POST /api/tasks/{id}/claim
- POST /api/submissions/
- GET  /api/earnings/
- GET  /api/ratings/me

## Admin APIs
- GET  /api/admin/assignments
- POST /api/admin/assignments/{id}/approve
- POST /api/admin/assignments/{id}/reject
- GET  /api/admin/submissions
- POST /api/admin/submissions/{id}/approve
- POST /api/admin/payments/release
- GET  /api/admin/users
- PATCH /api/admin/users/{id}

## Workflow
1. Student creates assignment (files accepted, uuid storage)
2. Admin approves → visible to writers
3. Writer claims (limits enforced by subscription)
4. Writer submits
5. Admin approves submission → payment release, rating +5, badge update

## File Uploads
- Accept all formats; size stored; UUID naming
- Separate paths: `student/...` and `writer/...`

## Lipana STK
- Trigger via `POST /api/wallet/topup` and `POST /api/subscriptions/pay`
- Callback: `POST /api/payments/lipana/callback` with HMAC `X-Lipana-Signature`
- Idempotent processing; updates wallet/subscription status

## Email
- Verification and password reset emails sent via Celery tasks.
- Configure SMTP in `.env` (`EMAIL_*`).

## Celery
Start worker (Redis broker, django-db results):
```bash
C:/Users/jumaj/OneDrive/Desktop/PL-Project/.venv/Scripts/python.exe -m celery -A marketplace worker -l info
```

## Deployment
- Set `DEBUG=False`, configure `ALLOWED_HOSTS`
- Use PostgreSQL and S3-compatible storage
- Serve with Gunicorn + Whitenoise (Linux): `gunicorn marketplace.wsgi:application`

