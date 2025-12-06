# SecureBridge - Quick Setup Guide

## Installation Steps

1. **Install dependencies using uv (recommended):**
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip install -r requirements.txt
```

2. **Generate secure keys:**
```bash
python generate_keys.py
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add the generated keys
```

4. **Initialize the database:**
```bash
# The database will be created automatically on first run
# Or run migrations if using Alembic:
alembic upgrade head
```

5. **Run the application:**
```bash
uvicorn app.main:app --reload
```

6. **Access the API:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

Test the authentication endpoints:

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "testpass123"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## Running Tests

```bash
# Install dev dependencies
uv pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

## Troubleshooting

If you encounter import errors:
```bash
# Make sure all dependencies are installed
uv pip install -r requirements.txt --force-reinstall
```

If database errors occur:
```bash
# Delete the database file and restart
rm securebridge.db
uvicorn app.main:app --reload
```
