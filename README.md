# AI Chatbot with Dual Frontends

An educational project demonstrating modern web development with FastAPI backend and dual frontends (Streamlit and React).

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
```bash
# Clone the repository
git clone <repository-url>
cd ai-chat-bot

# Install dependencies
make dev-install

# Copy environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Run database migrations (after implementing)
# make migrate

# Start the backend
make run-backend

# In another terminal, start Streamlit (after implementing)
# make run-streamlit
```

### Development
See [IMPLEMENTATION_WORKFLOW.md](docs/IMPLEMENTATION_WORKFLOW.md) for detailed development guide.

## Architecture
See [SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) for technical architecture details.

## Project Status
✅ Phase 0: Development environment setup (Complete)
⏳ Phase 1: Backend foundation & Streamlit UI (Next)
📋 Phase 2: Enhanced features
📋 Phase 3: React implementation
📋 Phase 4: Production readiness

## License
MIT
