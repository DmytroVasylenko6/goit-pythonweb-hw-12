# Contacts API

REST API for contact management with authentication and authorization.

## Local Setup and Running

1. Install Poetry if not already installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd goit-pythonweb-hw-12
```

3. Install dependencies:

```bash
poetry lock
```

```bash
poetry install
```

4. Activate Poetry virtual environment:
```bash
poetry env activate
```

5. Start PostgreSQL using Docker
```bash
docker-compose up -d
```

6. Apply migrations:
```bash
poetry run alembic revision --autogenerate -m 'Init'
poetry run alembic upgrade head
```

7. Start the server:
```bash
poetry run uvicorn main:app
```

## Running with Docker

1. Build and start containers:
```bash
docker-compose up --build
```

2. Apply migrations:
```bash
docker-compose exec web poetry run alembic upgrade head
```

## Important Notes

1. **Environment Variables**:
   - Make sure to set up all required environment variables in the `.env` file
   - Never commit the `.env` file to version control
   - For production, use secure secrets management

2. **Database**:
   - Ensure PostgreSQL is running before starting the application
   - For production, use a managed database service
   - Regularly backup your database

3. **Email Configuration**:
   - For Gmail, you need to generate an "App Password"
   - Enable 2FA in your Google account first
   - Use a dedicated email account for the application

4. **Security**:
   - Change default JWT secret in production
   - Use strong passwords for all services
   - Enable HTTPS in production
   - Regularly update dependencies

5. **Development**:
   - Use `--reload` flag during development for auto-reloading
   - Check logs for debugging
   - Use proper error handling in production

## API Documentation

After starting the server, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

