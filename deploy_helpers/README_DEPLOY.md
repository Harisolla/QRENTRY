# Deployment helpers for QrEntry

This folder contains helper files to containerize and deploy the Django project.

Files included:
- Dockerfile : build a Docker image that runs migrations, collects static, and starts Django dev server.
- docker-compose.yml : run locally with Docker Compose.
- Procfile : for Heroku-like platforms.
- .dockerignore : files to ignore when building image.

## Quick local Docker run (requires Docker)
1. Build: `docker build -t qrentry .`
2. Run: `docker run -p 8000:8000 --env DEBUG=True qrentry`
3. Open: http://localhost:8000

## Deploy to Render / Railway / Heroku
- Render: create a Web Service, connect repository, set build command `docker build -t render .` or specify Dockerfile, set service type to web, and port 8000.
- Heroku: push repo with Procfile. Make sure to set required environment variables (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS).
- For a production deployment, use Gunicorn + whitenoise, and configure a production database (Postgres) and static file serving.

## Important environment variables to set
- SECRET_KEY
- DEBUG (False in production)
- ALLOWED_HOSTS (e.g. example.com)
- DATABASE_URL (if using Postgres)
- Any social auth keys used in event_system/settings.py

