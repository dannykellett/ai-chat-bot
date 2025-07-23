# Quick Start: Immediate Next Steps

## 🚀 Start Here - First Commands to Run

### 1. Create .gitignore (2 minutes)
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
.env
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
.ruff_cache/

# Database
*.db
*.sqlite
*.sqlite3

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Frontend
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
build/
dist/
*.log

# Environment
.env
.env.local
.env.*.local

# Uploads
uploads/
temp/

# Streamlit
.streamlit/cache/
.streamlit/secrets.toml
EOF
```

### 2. Create Initial Project Structure (5 minutes)
```bash
# Create all directories
mkdir -p backend/{models,repositories,services,api/v1,schemas,utils}
mkdir -p streamlit_app/{pages,components,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p scripts docker migrations

# Create __init__.py files
find backend streamlit_app tests -type d -exec touch {}/__init__.py \;

# Create main files
touch backend/main.py backend/config.py backend/database.py backend/constants.py
touch streamlit_app/main.py
touch tests/conftest.py
```

### 3. Set Up Environment Variables (2 minutes)
```bash
# Create .env.example
cat > .env.example << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Database Configuration
DATABASE_URL=sqlite:///./chatbot.db

# Application Settings
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=txt,md,pdf,py,js,ts,jsx,tsx
EOF

# Copy to .env for local development
cp .env.example .env
```

### 4. Update pyproject.toml (Already exists, update it)
```bash
# The pyproject.toml content from PHASE_0_TASKS.md should be copied here
# This includes all dependencies and tool configurations
```

### 5. Create Makefile (2 minutes)
```bash
cat > Makefile << 'EOF'
.PHONY: help install dev-install test lint format run-backend run-streamlit migrate clean

help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  dev-install   Install all dependencies including dev"
	@echo "  test          Run tests"
	@echo "  lint          Run linting"
	@echo "  format        Format code"
	@echo "  run-backend   Run FastAPI backend"
	@echo "  run-streamlit Run Streamlit app"
	@echo "  migrate       Run database migrations"
	@echo "  clean         Clean up generated files"

install:
	uv pip install -e .

dev-install:
	uv pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=backend --cov-report=html

lint:
	ruff check backend/ tests/
	mypy backend/

format:
	ruff format backend/ tests/

run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-streamlit:
	streamlit run streamlit_app/main.py

migrate:
	alembic upgrade head

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov .ruff_cache
EOF
```

### 6. Install Dependencies (5 minutes)
```bash
# First, ensure UV is installed
# pip install uv  # if not already installed

# Install all dependencies including dev
make dev-install

# Or manually:
# uv pip install -e ".[dev]"
```

### 7. Set Up Pre-commit (2 minutes)
```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
EOF

# Install pre-commit hooks
pre-commit install
```

### 8. Create Initial FastAPI App (3 minutes)
```bash
cat > backend/main.py << 'EOF'
"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

app = FastAPI(
    title="AI Chatbot API",
    description="Educational AI chatbot with streaming responses",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Chatbot API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
EOF
```

### 9. Create Basic Configuration (2 minutes)
```bash
cat > backend/config.py << 'EOF'
"""Application configuration."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "your-secret-key-here"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Database
    database_url: str = "sqlite:///./chatbot.db"

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    # File Upload
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = ["txt", "md", "pdf", "py", "js", "ts", "jsx", "tsx"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
EOF
```

### 10. Verify Everything Works (2 minutes)
```bash
# Test that the backend runs
make run-backend
# Visit http://localhost:8000 in browser - should see JSON response

# In another terminal, test linting
make lint

# Test formatting
make format

# Create a test commit to verify pre-commit
git add .
git commit -m "Initial project setup"
```

## 🎯 Total Time: ~30 minutes

## ✅ Checklist - What You Should Have
- [ ] .gitignore file created
- [ ] Project structure with all directories
- [ ] Environment variables configured (.env and .env.example)
- [ ] Dependencies installed via UV
- [ ] Makefile with useful commands
- [ ] Pre-commit hooks configured
- [ ] Basic FastAPI app that runs
- [ ] Configuration management set up

## 📌 Next Step: Start Phase 1
Once the above is complete, you're ready to start building:
1. Create database models (Chat, Message, Session)
2. Set up SQLAlchemy and Alembic
3. Implement repository pattern
4. Build first API endpoints
5. Create initial Streamlit UI

## 🚨 Common Issues & Solutions

### UV Not Installed
```bash
pip install uv
```

### Port 8000 Already in Use
```bash
# Change port in Makefile or run with:
uvicorn backend.main:app --reload --port 8001
```

### OpenAI API Key Missing
```bash
# Edit .env file and add your actual API key
# Get one from: https://platform.openai.com/api-keys
```

### Import Errors
```bash
# Make sure you're in the project root and installed with -e flag
uv pip install -e ".[dev]"
```
