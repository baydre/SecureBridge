# SecureBridge Dev Container

This directory contains the development container configuration for SecureBridge, enabling consistent development environments using GitHub Codespaces or VS Code Remote Containers.

## What's Included

### Base Image
- Python 3.10 development environment
- Non-root user (`vscode`) for security
- Git and GitHub CLI pre-installed

### Pre-installed Tools
- **Python Package Manager**: pip and uv (for faster installs)
- **Testing**: pytest, pytest-asyncio, httpx
- **Linting & Formatting**: black, ruff
- **Database Tools**: PostgreSQL client, SQLite3

### VS Code Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Ruff (charliermarsh.ruff)
- isort (ms-python.isort)
- Even Better TOML (tamasfe.even-better-toml)
- YAML (redhat.vscode-yaml)
- Error Lens (usernamehw.errorlens)
- GitLens (eamodio.gitlens)
- GitHub Pull Requests (github.vscode-pull-request-github)
- Docker (ms-azuretools.vscode-docker)

### Port Forwarding
- Port 8000: FastAPI application

## Getting Started

### Using GitHub Codespaces

1. Navigate to the repository on GitHub
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on [branch]"
5. Wait for the container to build and the post-create script to run

### Using VS Code Remote Containers

1. Install the "Remote - Containers" extension in VS Code
2. Open the repository folder in VS Code
3. Press `F1` and select "Remote-Containers: Reopen in Container"
4. Wait for the container to build

### First Time Setup

After the container is created, you'll need to:

1. **Configure environment variables**:
   ```bash
   # The .env file is created from .env.example
   # Add the generated keys to .env
   nano .env
   ```

2. **Generate secure keys** (if not already done):
   ```bash
   python generate_keys.py
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Development Workflow

### Running the Application
```bash
uvicorn app.main:app --reload
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Formatting
```bash
# Format code with black
black app/ tests/

# Check formatting
black app/ tests/ --check
```

### Linting
```bash
# Lint with ruff
ruff check app/ tests/

# Auto-fix issues
ruff check app/ tests/ --fix
```

### Database Management
```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"
```

## Customization

### Adding Python Packages
1. Add the package to `requirements.txt` or `pyproject.toml`
2. Rebuild the container or run:
   ```bash
   pip install -r requirements.txt
   ```

### Adding VS Code Extensions
1. Edit `.devcontainer/devcontainer.json`
2. Add extension ID to the `extensions` array
3. Rebuild the container

### Modifying Container Configuration
1. Edit `.devcontainer/Dockerfile` for system-level changes
2. Edit `.devcontainer/devcontainer.json` for VS Code settings
3. Rebuild the container to apply changes

## Troubleshooting

### Container Build Fails
- Check Docker daemon is running
- Verify internet connection
- Try rebuilding: `F1` → "Remote-Containers: Rebuild Container"

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Errors
```bash
# Delete and recreate database
rm securebridge.db
uvicorn app.main:app --reload
```

### Permission Issues
The container runs as the `vscode` user (non-root) for security. If you need root access:
```bash
sudo <command>
```

## Resources

- [VS Code Remote Containers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Dev Container Specification](https://containers.dev/)
