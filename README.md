# QrEntry

QrEntry is a Django-based event ticket booking and attendance management system. Users can browse events, book tickets, receive QR-backed confirmations, and download ticket PDFs. Organizers can create events, review bookings, and scan tickets at entry.

## Live Website

Website: [https://qrentry-1-4yfa.onrender.com/](https://qrentry-1-4yfa.onrender.com/)

Note: this URL is inferred from the Render service name in `render.yaml`. If your deployed app uses a different hostname, update this link.

## Features

- User signup and login with role selection for `participant` or `organiser`
- Google login support through `django-allauth`
- Event creation with image upload, date, location, price, and capacity
- Event discovery with search, date filters, price filter, and pagination
- Ticket booking flow with generated ticket IDs and QR codes
- Organizer booking view and QR-based attendance scanning
- Ticket PDF download using ReportLab
- Email-ready booking flow with console email backend by default
- Admin panel through Django admin

## Tech Stack

- Backend: Django 5
- Database: SQLite for local development, `DATABASE_URL` support for production databases
- Authentication: Django auth + `django-allauth`
- Media and static files: WhiteNoise, uploaded event images, generated QR assets
- PDF generation: ReportLab
- QR generation: `qrcode` + Pillow
- Deployment: Render + Gunicorn

## Project Structure

```text
QrEntry-main/
|-- core/                 # Models, views, forms, templates, QR logic
|-- event_system/         # Django settings, URLs, WSGI/ASGI
|-- static/               # Static assets
|-- media/                # Uploaded images and generated files
|-- build.sh              # Render build script
|-- render.yaml           # Render blueprint
|-- manage.py
|-- requirements.txt
```

## Core Models

- `Profile`: links a Django user to a role (`organiser` or `participant`)
- `Event`: stores event details including capacity, price, and optional image
- `Booking`: stores the booked event, ticket ID, status, and QR file path
- `Payment`: stores simulated payment records
- `CheckinLog`: stores check-in activity

## Main Routes

### Pages

- `/` home page
- `/events/` event listing
- `/events/<id>/` event detail
- `/bookings/` participant bookings
- `/events/create/` organizer event creation
- `/organizer/bookings/` organizer booking dashboard
- `/scan/` attendance scan page
- `/scan-qr/` camera QR scanner
- `/login/`, `/signup/`, `/logout/`
- `/password-reset/` and related reset flows

### JSON and utility endpoints

- `/api/events/` list events
- `/api/events/<id>/` event details
- `/api/book/<event_id>/` create booking
- `/api/qr/<booking_id>/` download QR image
- `/api/payment-webhook/` simulated payment webhook
- `/download-pdf/<booking_id>/` download ticket PDF

## Local Setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and adjust values as needed.

Important variables:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

Default local database:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Run migrations

```powershell
python manage.py migrate
```

### 5. Create an admin user

```powershell
python manage.py createadmin
```

Default fallback credentials used by the custom management command:

- Username: `admin`
- Password: `admin123`

### 6. Start the development server

```powershell
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Email Behavior

The project uses Django's console email backend by default, which means booking and password reset emails are printed to the terminal in local development.

To send real emails, configure SMTP values in `.env`.

## Deployment on Render

This repository already includes:

- `render.yaml`
- `build.sh`

`build.sh` runs:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Render steps

1. Create a new Blueprint service on Render from this GitHub repository.
2. Let Render provision the web service and database defined in `render.yaml`.
3. Set the correct production values for:
   - `ALLOWED_HOSTS`
   - `CSRF_TRUSTED_ORIGINS`
   - `SECRET_KEY`
   - email variables if you want live email delivery
4. Deploy the service.

Production start command:

```bash
gunicorn event_system.wsgi --bind 0.0.0.0:$PORT
```

## Notes

- The app is server-rendered with Django templates. It does not use React in the current codebase.
- Local development uses SQLite by default, not MySQL.
- Payment handling in this repository is simulated for development and demo purposes.
- Static files are served with WhiteNoise, and uploaded/generated media is stored under `media/`.
