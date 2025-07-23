# Phase 0: Project Infrastructure Tasks

## Immediate Setup Tasks (Day 1-2)

### 1. Development Environment Configuration

#### Create .gitignore
```bash
# Task: Create comprehensive .gitignore for Python/React project
# Time: 15 minutes
# Priority: Critical
```

**Implementation Steps:**
1. Create .gitignore with Python-specific ignores
2. Add React/Node.js specific patterns
3. Include IDE-specific files (VSCode, PyCharm)
4. Add environment and secret files

**Acceptance Criteria:**
- [ ] Python artifacts ignored (__pycache__, *.pyc, .pytest_cache)
- [ ] Virtual environment excluded (venv/, env/)
- [ ] Node modules excluded (node_modules/)
- [ ] Environment files protected (.env, .env.local)
- [ ] IDE files ignored (.vscode/, .idea/)

#### Set Up Environment Variables
```bash
# Task: Create environment configuration
# Time: 30 minutes
# Priority: Critical
```

**Implementation Steps:**
1. Create .env.example with all required variables
2. Create .env for local development
3. Document each environment variable
4. Set up environment validation

**Required Variables:**
```
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Database Configuration
DATABASE_URL=sqlite:///./chatbot.db
# DATABASE_URL=postgresql://user:pass@localhost/chatbot  # Production

# Application Settings
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=txt,md,pdf,py,js,ts,jsx,tsx

# API Settings
API_RATE_LIMIT=60
API_TIMEOUT_SECONDS=30
```

### 2. Python Package Management

#### Initialize UV Package Manager
```bash
# Task: Set up UV and create initial dependencies
# Time: 45 minutes
# Priority: High
```

**Create pyproject.toml:**
```toml
[project]
name = "ai-chatbot"
version = "0.1.0"
description = "Educational AI chatbot with FastAPI and dual frontends"
requires-python = ">=3.12"
dependencies = [
    # Core
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "python-dotenv>=1.0.0",

    # Database
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "aiosqlite>=0.19.0",  # For async SQLite

    # OpenAI
    "openai>=1.0.0",

    # Utilities
    "pydantic>=2.4.0",
    "pydantic-settings>=2.0.0",
    "python-multipart>=0.0.6",  # For file uploads
    "aiofiles>=23.2.0",

    # Streamlit
    "streamlit>=1.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.6.0",
    "ruff>=0.1.0",
    "pre-commit>=3.5.0",
    "httpx>=0.25.0",  # For testing
    "factory-boy>=3.3.0",  # For test fixtures
]

prod = [
    "psycopg2-binary>=2.9.0",  # PostgreSQL
    "gunicorn>=21.2.0",
    "redis>=5.0.0",  # For caching
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "B", "C90", "UP", "S"]
ignore = ["E501"]  # Line length handled by formatter
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

### 3. Project Structure Creation

#### Create Directory Structure
```bash
# Task: Set up comprehensive project structure
# Time: 30 minutes
# Priority: High
```

**Directory Structure:**
```
ai-chat-bot/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── session.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── session.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── openai.py
│   │   └── session.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chats.py
│   │   │   ├── messages.py
│   │   │   └── sessions.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── session.py
│   ├── utils/               # Utilities
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   └── constants.py         # Application constants
├── streamlit_app/           # Streamlit frontend
│   ├── __init__.py
│   ├── main.py
│   ├── pages/
│   ├── components/
│   └── utils/
├── frontend/                # React frontend (Phase 3)
│   ├── src/
│   ├── public/
│   └── package.json
├── migrations/              # Alembic migrations
│   └── alembic.ini
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                 # Utility scripts
│   ├── setup_dev.sh
│   └── seed_data.py
├── docker/                  # Docker configurations
│   ├── backend.Dockerfile
│   ├── streamlit.Dockerfile
│   └── docker-compose.yml
├── docs/                    # Documentation
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── Makefile
```

### 4. Development Tools Setup

#### Create Makefile
```bash
# Task: Create Makefile for common commands
# Time: 20 minutes
# Priority: Medium
```

**Makefile Content:**
```makefile
.PHONY: help install dev-install test lint format run-backend run-streamlit migrate

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

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"
```

#### Set Up Pre-commit Hooks
```bash
# Task: Configure pre-commit for code quality
# Time: 20 minutes
# Priority: Medium
```

**Create .pre-commit-config.yaml:**
```yaml
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

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

### 5. Initial Documentation

#### Create README.md
```bash
# Task: Create project README
# Time: 30 minutes
# Priority: Medium
```

**README Template:**
```markdown
# AI Chatbot with Dual Frontends

An educational project demonstrating modern web development with FastAPI backend
and dual frontends (Streamlit and React).

## Features
- 🤖 AI-powered chat using OpenAI GPT-4o Mini
- 🚀 FastAPI backend with async support
- 🎨 Dual frontends: Streamlit (reference) and React (learning)
- 📁 File upload and processing support
- 💾 SQLite/PostgreSQL database with session management
- 🔄 Real-time streaming responses

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (for React frontend)
- UV package manager

### Installation
\```bash
# Clone the repository
git clone <repository-url>
cd ai-chat-bot

# Install dependencies
make dev-install

# Copy environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Run database migrations
make migrate

# Start the backend
make run-backend

# In another terminal, start Streamlit
make run-streamlit
\```

### Development
See [IMPLEMENTATION_WORKFLOW.md](docs/IMPLEMENTATION_WORKFLOW.md) for detailed development guide.

## Architecture
See [SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) for technical architecture details.

## License
MIT
```

## Summary of Phase 0 Tasks

### Day 1 Tasks (4-5 hours)
1. ✅ Create comprehensive .gitignore (15 min)
2. ✅ Set up environment configuration (30 min)
3. ✅ Initialize UV and update pyproject.toml (45 min)
4. ✅ Create project directory structure (30 min)
5. ✅ Create Makefile (20 min)
6. ✅ Set up pre-commit hooks (20 min)
7. ✅ Create initial README (30 min)

### Day 2 Tasks (3-4 hours)
1. 📋 Install all dependencies with UV
2. 📋 Verify pre-commit hooks work
3. 📋 Create initial logger configuration
4. 📋 Set up basic FastAPI app structure
5. 📋 Create initial database configuration
6. 📋 Run first test to verify setup

## Next Steps After Phase 0
Once infrastructure is complete, proceed to Phase 1:
1. Implement FastAPI application with proper structure
2. Create SQLAlchemy models for Chat, Message, Session
3. Set up Alembic migrations
4. Implement first API endpoint with tests
5. Begin Streamlit UI development

## Success Criteria for Phase 0
- [ ] All dependencies installed successfully
- [ ] Pre-commit hooks running on commits
- [ ] Project structure created and organized
- [ ] Environment variables configured
- [ ] Development commands working (make commands)
- [ ] Initial documentation in place
