# SecureBridge

A production-ready FastAPI application implementing a **dual authentication system** supporting both JWT-based user authentication and API key-based service-to-service authentication. Built for modern microservices architectures requiring flexible authentication strategies.

## 🌟 Features

### 🔐 Dual Authentication System
- **User Authentication**: JWT-based authentication for human users with access and refresh tokens
- **Service Authentication**: API key-based authentication for service-to-service communication
- **Flexible Middleware**: Support for both authentication methods in a single endpoint

### 👤 User Management
- User registration and login with email/password
- Secure password hashing with bcrypt
- JWT token generation (access and refresh tokens)
- Role-based access control (RBAC)
- User profile management

### 🔑 API Key Management
- Generate secure API keys with custom permissions
- Set expiration dates and auto-expiration handling
- Revoke and renew API keys
- Permission-based access control
- Track key usage with last-accessed timestamps
- Encrypted API key storage

### 🛡️ Security Features
- Password hashing with bcrypt
- JWT token validation and expiration
- API key encryption at rest
- CORS configuration
- Rate limiting support
- Token refresh mechanism

### 🏗️ Architecture
- Clean architecture with separation of concerns
- Service layer for business logic
- Middleware for authentication
- Pydantic schemas for validation
- SQLAlchemy ORM for database operations
- Comprehensive test coverage

## 📁 Project Structure

```
SecureBridge/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Shared dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py            # User authentication routes
│   │       └── keys.py            # API key management routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection
│   │   └── security.py            # Security utilities
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py    # Authentication middleware
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User database model
│   │   └── api_key.py             # API key database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # User Pydantic schemas
│   │   ├── api_key.py             # API key Pydantic schemas
│   │   └── auth.py                # Auth response schemas
│   └── services/
│       ├── __init__.py
│       └── auth_service.py        # Authentication business logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test configuration
│   ├── test_auth.py               # Authentication tests
│   └── test_keys.py               # API key tests
├── .env.example                    # Environment variables template
├── .gitignore
├── generate_keys.py                # Security key generator
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Python dependencies
├── README.md
└── SETUP.md                        # Quick setup guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- uv (recommended) or pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/baydre/SecureBridge.git
cd SecureBridge
```

2. **Install dependencies**
```bash
# Using uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

3. **Generate secure keys**
```bash
python generate_keys.py
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with the generated keys
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

#### User Registration
```bash
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepass123"
}
```

#### User Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

#### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Refresh Token
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

### API Key Management Endpoints

#### Create API Key
```bash
POST /api/v1/keys/create
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "service_name": "my-service",
  "description": "Production API key",
  "permissions": ["read:data", "write:data"],
  "expires_in_days": 90
}
```

#### List API Keys
```bash
GET /api/v1/keys/list
Authorization: Bearer <access_token>
```

#### Verify API Key
```bash
GET /api/v1/keys/verify/test
Authorization: Bearer <api_key>
```

#### Revoke API Key
```bash
PATCH /api/v1/keys/{key_id}/revoke
Authorization: Bearer <access_token>
```

#### Renew API Key
```bash
PATCH /api/v1/keys/{key_id}/renew
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "expires_in_days": 180
}
```

#### Delete API Key
```bash
DELETE /api/v1/keys/{key_id}
Authorization: Bearer <access_token>
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install dev dependencies
uv pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Application
APP_NAME=SecureBridge
DEBUG=True
API_VERSION=v1

# Security
SECRET_KEY=<generated-secret-key>
API_KEY_ENCRYPTION_KEY=<generated-encryption-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./securebridge.db

# API Keys
API_KEY_DEFAULT_EXPIRATION_DAYS=90
API_KEY_PREFIX=sbk_
```

## 🏗️ Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLAlchemy (supports PostgreSQL, SQLite, MySQL)
- **Authentication**: Python-JOSE (JWT), bcrypt (password hashing)
- **Encryption**: Cryptography (Fernet)
- **Validation**: Pydantic
- **Testing**: pytest, httpx
- **Package Manager**: uv

## 🔒 Security Best Practices

1. **Always use HTTPS in production**
2. **Rotate API keys regularly**
3. **Use strong, unique encryption keys**
4. **Implement rate limiting**
5. **Monitor authentication failures**
6. **Keep dependencies updated**
7. **Never commit `.env` file to version control**
8. **Use environment-specific configurations**

## 📊 Usage Examples

### Example 1: User Authentication Flow
```python
# 1. Register new user
response = requests.post("http://localhost:8000/api/v1/auth/signup", json={
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepass123"
})
tokens = response.json()["tokens"]

# 2. Access protected endpoint
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
```

### Example 2: Service-to-Service Authentication
```python
# 1. Create API key (as authenticated user)
headers = {"Authorization": f"Bearer {user_access_token}"}
response = requests.post("http://localhost:8000/api/v1/keys/create", 
    headers=headers,
    json={
        "service_name": "analytics-service",
        "permissions": ["read:data", "write:logs"],
        "expires_in_days": 90
    }
)
api_key = response.json()["api_key"]

# 2. Use API key for service authentication
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("http://localhost:8000/api/v1/keys/verify/test", headers=headers)
```

## 🚢 Deployment

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t securebridge .
docker run -p 8000:8000 --env-file .env securebridge
```

### Production Considerations
- Use PostgreSQL instead of SQLite
- Set `DEBUG=False`
- Enable HTTPS/TLS
- Configure proper CORS origins
- Set up monitoring and logging
- Implement rate limiting
- Use environment-specific secrets

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM capabilities
- The Python community for amazing libraries

## 📧 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/baydre/SecureBridge/issues)
- Check the [API documentation](http://localhost:8000/docs)

## 🗺️ Roadmap

- [ ] Token blacklisting for logout
- [ ] Email notifications for key expiration
- [ ] API key usage analytics dashboard
- [ ] Multi-factor authentication (MFA)
- [ ] OAuth2 integration
- [ ] WebSocket support with authentication
- [ ] API rate limiting per key
- [ ] Audit log endpoints
- [ ] Key rotation automation