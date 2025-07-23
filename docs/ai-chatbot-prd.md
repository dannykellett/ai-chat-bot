# Product Requirements Document (PRD)
# AI Chatbot Application

**Version:** 1.0
**Date:** July 22, 2025
**Status:** Draft

---

## Executive Summary

This PRD outlines the development of an open-source AI chatbot application designed primarily as a learning project. It features dual frontend implementations (Streamlit and React), a FastAPI backend with OpenAI GPT-4o Mini integration, streaming responses, and simple deployment options. The project emphasizes simplicity, learning opportunities, and practical implementation patterns.

---

## 1. Objective and Scope

### 1.1 Purpose
Build a simple, educational AI chatbot application that demonstrates modern web development patterns, streaming architecture, and provides a platform for learning frontend development through practical implementation.

### 1.2 Project Goals
- **Learning Objective**: Master React development by building alongside a Streamlit reference implementation
- **Technical Demonstration**: Showcase FastAPI streaming capabilities with OpenAI integration
- **Open Source Contribution**: Create a well-documented starter template for the community
- **Deployment Simplicity**: Run anywhere - VPS, local machine, or budget hosting

### 1.3 Scope

**In Scope:**
- FastAPI backend with OpenAI GPT-4o Mini integration
- SSE-based streaming responses
- Dual frontend: Streamlit (reference) and React (learning focus)
- Anonymous session-based chat management
- SQLite for chat history persistence
- Markdown rendering in chat interface
- File upload support for context
- Docker deployment for portability
- Comprehensive documentation for learners

**Out of Scope:**
- User authentication system
- Complex AI features (RAG, function calling)
- Export functionality
- Analytics or monitoring
- Multi-language support
- Mobile native apps
- Enterprise features

### 1.4 Success Criteria
- Clean, understandable code that serves as a learning resource
- Both frontends achieve feature parity
- Easy deployment on any VPS with Docker
- Well-documented for open-source contributors
- Positive feedback from learners using the project

---

## 2. Technical Context

### 2.1 Learning Focus
This project serves as a practical introduction to:
- Modern Python web development with FastAPI
- Real-time streaming architectures
- React development patterns and best practices
- Docker containerization
- Working with AI APIs

### 2.2 Open Source Considerations
- **License**: MIT License for maximum flexibility
- **Documentation**: Comprehensive README, inline code comments
- **Contributing Guidelines**: Welcome beginners and experienced developers
- **Code Style**: Clear, educational coding patterns over clever optimizations

---

## 3. User Personas & Use Cases

### 3.1 Primary Persona: The Learner Developer

**Profile:**
- Backend developer learning frontend technologies
- Comfortable with Python, new to React
- Wants practical, working examples
- Values clear documentation and code comments

**Goals:**
- Understand React by comparing with Streamlit implementation
- Learn streaming architecture patterns
- Build portfolio project
- Contribute to open source

### 3.2 Use Cases

1. **Learning by Comparison**
   - Implement feature in Streamlit first
   - Port the same feature to React
   - Compare approaches and patterns

2. **Chat Interaction**
   - Start anonymous chat session
   - Send messages with markdown formatting
   - Upload files for context
   - See AI responses stream in real-time

3. **Development Workflow**
   - Clone repository
   - Run with Docker or locally
   - Modify and experiment
   - Deploy to personal VPS

---

## 4. Core Features

### 4.1 Chat Functionality
- **Streaming Responses**: Real-time token-by-token display
- **Markdown Support**: Render formatted text, code blocks, lists
- **File Uploads**: Accept text files, PDFs, images for context
- **Session Management**: Anonymous sessions with localStorage/cookies
- **Chat History**: Simple SQLite storage per session

### 4.2 Frontend Features

**Both Frontends Include:**
- Chat interface with message bubbles
- Sidebar for chat history
- New chat button
- File upload interface
- Markdown preview
- Loading/typing indicators
- Error handling with user-friendly messages

**React-Specific Learning Features:**
- Component-based architecture
- State management with useState/useContext
- Custom hooks for chat logic
- Modern CSS with Tailwind
- TypeScript for type safety (optional)

### 4.3 Backend Features
- FastAPI with automatic API documentation
- Streaming endpoints using SSE
- File processing pipeline
- Session management
- SQLite integration
- Comprehensive error handling
- Environment-based configuration

---

## 5. Technical Implementation

### 5.1 Backend Architecture

**FastAPI Structure:**
```python
/backend
  /app
    __init__.py
    main.py          # FastAPI app setup
    /api
      chat.py        # Chat endpoints
      files.py       # File upload handling
      sessions.py    # Session management
      conversations.py # Conversation CRUD
    /services
      openai.py      # OpenAI integration
      streaming.py   # SSE implementation
      file_processor.py # File text extraction
    /models
      schemas.py     # Pydantic models
      database.py    # SQLAlchemy models
    /utils
      db.py          # Database connection
      auth.py        # Session validation
```

**Key Libraries:**
- `fastapi`: Web framework
- `openai`: Official OpenAI SDK
- `python-multipart`: File uploads
- `aiofiles`: Async file operations
- `sqlalchemy`: ORM for database
- `python-jose`: Session tokens
- `pypdf`: PDF text extraction
- `pillow`: Image processing
- Managed with `uv` package manager

### 5.2 Frontend Architecture

**Streamlit (Reference Implementation):**
- Single `app.py` file for simplicity
- Sidebar for chat management
- Main area for chat interface
- Built-in session state management

**React (Learning Implementation):**
```
/frontend-react
  /src
    /components
      ChatMessage.jsx    # Individual message component
      ChatInput.jsx      # Input with file upload
      Sidebar.jsx        # Chat history
      FileUpload.jsx     # Drag-drop file handler
      MarkdownRenderer.jsx # Markdown display
    /hooks
      useChat.js         # Custom hook for chat logic
      useStreaming.js    # SSE handling
      useSession.js      # Session management
    /services
      api.js             # Backend communication
      storage.js         # localStorage wrapper
    /types
      chat.ts            # TypeScript interfaces
    /styles
      tailwind.css       # Styling
    App.jsx              # Main application
```

### 5.3 Database Layer

**Database Access Pattern:**
```python
# backend/app/utils/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async SQLAlchemy setup for SQLite
DATABASE_URL = "sqlite+aiosqlite:///./chat.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**Repository Pattern Example:**
```python
# backend/app/services/conversation_service.py
class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        session_id: str,
        first_message: str
    ) -> Conversation:
        # Create with auto-generated title from first message
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        # Implementation...

    async def get_conversations(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        # Get recent conversations for session
        # Implementation...
```

### 5.4 Deployment Structure
```
/docker
  docker-compose.yml     # Full stack setup
  Dockerfile.backend     # Python/FastAPI image
  Dockerfile.react       # Node/React image
  nginx.conf            # Reverse proxy config
```

---

## 6. Development Approach

### 6.1 Iterative Development
Since this is a learning project without timeline constraints:

**Phase 1: Basic Foundation**
- FastAPI backend with simple chat endpoint
- OpenAI integration with streaming
- Basic Streamlit UI
- Docker setup

**Phase 2: Feature Enhancement**
- File upload support
- Markdown rendering
- Chat history with SQLite
- Improved error handling

**Phase 3: React Implementation**
- Set up React project
- Port Streamlit features one by one
- Add styling with Tailwind
- Implement custom hooks

**Phase 4: Polish & Documentation**
- Code cleanup and comments
- Comprehensive README
- Deployment guides
- Contributing guidelines

### 6.2 Learning Milestones
Each phase includes specific learning goals:
- Understanding async Python and streaming
- Mastering React hooks and state management
- Working with modern frontend tooling
- Implementing real-time features
- Managing deployment and DevOps

### 6.3 Open Source Development
- Start with "good enough" and iterate
- Welcome contributions at any skill level
- Focus on code clarity over optimization
- Extensive inline documentation

---

## 7. Simplified Infrastructure

### 7.1 Development Setup
```bash
# Clone and run locally
git clone <repo>
cd ai-chatbot

# Backend
cd backend
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (Streamlit)
cd frontend-streamlit
uv pip install streamlit
streamlit run app.py

# Frontend (React)
cd frontend-react
npm install
npm run dev
```

### 7.2 Deployment Options

**Option 1: Single VPS with Docker**
```bash
# On your VPS
docker-compose up -d
```

**Option 2: Separate Services**
- Backend on small VPS (1GB RAM)
- Frontend on Vercel/Netlify (free tier)
- SQLite file persisted on VPS

**Option 3: Local/Home Server**
- Raspberry Pi or old laptop
- Dynamic DNS for access
- Perfect for learning

### 7.3 Environment Configuration
```env
# .env file
OPENAI_API_KEY=sk-...
SESSION_SECRET=random-string-here
DATABASE_URL=sqlite:///./chat.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
```

---

## 8. User Interface Design

### 8.1 Streamlit Interface
```
┌─────────────────────────────────────────┐
│  AI Chatbot (Streamlit)                 │
├─────────────┬───────────────────────────┤
│             │                           │
│  Sidebar    │   Chat Messages          │
│             │                           │
│  [New Chat] │   User: Hello!           │
│             │                           │
│  History:   │   AI: Hi! How can I      │
│  - Chat 1   │   help you today?         │
│  - Chat 2   │                           │
│             │   [File Upload]           │
│             │   [Type message...]       │
│             │   [Send]                  │
└─────────────┴───────────────────────────┘
```

### 8.2 React Interface Goals
- Modern chat bubble design
- Smooth animations
- Responsive layout
- Dark/light mode toggle
- File drag-and-drop
- Real-time typing indicators

### 8.3 Key UI Components
1. **Message Component**: Renders markdown, shows timestamp
2. **Input Component**: Text area with file attachment
3. **Sidebar**: Collapsible on mobile, chat list
4. **Loading States**: Skeleton screens, spinners
5. **Error Boundaries**: Graceful error handling

---

## 9. Key Technical Decisions

### 9.1 Why These Technologies?

**FastAPI**
- Modern Python framework with automatic API docs
- Built-in async support for streaming
- Easy to understand for Python developers
- Great for learning API development

**Server-Sent Events (SSE)**
- Simpler than WebSockets for one-way streaming
- Built-in browser support
- Easy to implement and debug
- Perfect for AI response streaming

**SQLite**
- Zero configuration database
- File-based, easy to backup
- Sufficient for single-user or small deployments
- Can upgrade to PostgreSQL later if needed

**React (not React Native)**
- Web-first approach is simpler to learn
- Huge ecosystem and community
- Transferable skills to many projects
- Works on all devices via browser

### 9.2 Architecture Decisions

**Monorepo Structure**
```
ai-chatbot/
├── backend/
├── frontend-streamlit/
├── frontend-react/
├── docker/
├── docs/
└── README.md
```

**Session-Based Architecture**
- No user accounts to manage
- Simple cookie/localStorage for continuity
- Each session has isolated chat history
- Easy to clear and start fresh

### 9.3 Learning Path Optimization
1. Start with Streamlit (fastest to see results)
2. Understand the backend API
3. Build React components incrementally
4. Compare implementations side-by-side

---

## 10. Documentation & Community

### 10.1 Documentation Structure
```
docs/
├── README.md              # Project overview, quick start
├── INSTALLATION.md        # Detailed setup instructions
├── DEPLOYMENT.md          # VPS and Docker deployment
├── API.md                 # Backend API documentation
├── ARCHITECTURE.md        # Technical design decisions
├── LEARNING_PATH.md       # Guide for learners
└── CONTRIBUTING.md        # How to contribute
```

### 10.2 Code Documentation Standards
- Docstrings for all functions
- Comments explaining "why" not "what"
- Type hints in Python
- JSDoc comments in JavaScript
- Example usage in documentation

### 10.3 Community Building
- GitHub Issues for questions and bugs
- Discussions for feature ideas
- Welcome first-time contributors
- "Good first issue" labels
- Code review with teaching mindset

### 10.4 Example Code Structure
```python
# backend/app/services/streaming.py
async def stream_chat_response(
    message: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    """
    Stream AI response token by token using OpenAI API.

    This function demonstrates:
    - Async generators in Python
    - OpenAI streaming API usage
    - Error handling in async context

    Args:
        message: User's chat message
        session_id: Anonymous session identifier

    Yields:
        str: Individual tokens as they're generated

    Example:
        async for token in stream_chat_response("Hello", "123"):
            print(token, end="", flush=True)
    """
    # Implementation here...
```

---

## 11. Appendix

### 11.1 Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Streamlit UI   │     │    React UI     │
│                 │     │                 │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │   HTTP/SSE           │
         └───────────┬───────────┘
                     │
           ┌─────────▼─────────┐
           │                   │
           │  FastAPI Backend  │
           │                   │
           │  ┌─────────────┐  │
           │  │  Endpoints  │  │
           │  │  /chat      │  │
           │  │  /history   │  │
           │  └─────────────┘  │
           │                   │
           │  ┌─────────────┐  │
           │  │   Services  │  │
           │  │  Streaming  │  │
           │  │  Chat Mgmt  │  │
           │  └─────────────┘  │
           └─────────┬─────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐           ┌──────▼──────┐
    │         │           │             │
    │ OpenAI  │           │  Database   │
    │  API    │           │  (SQLite)   │
    │         │           │             │
    └─────────┘           └─────────────┘
```

### 11.2 Database Schema

**SQLite Schema Design:**

```sql
-- Sessions table: Anonymous user sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,  -- UUID v4
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT  -- For rate limiting
);

-- Conversations table: Chat threads
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,  -- UUID v4
    session_id TEXT NOT NULL,
    title TEXT,  -- Auto-generated from first message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    message_count INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Messages table: Individual chat messages
CREATE TABLE messages (
    id TEXT PRIMARY KEY,  -- UUID v4
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    token_count INTEGER,  -- For usage tracking
    model_name TEXT,  -- Track which model was used
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- File uploads table: Attached files
CREATE TABLE file_uploads (
    id TEXT PRIMARY KEY,  -- UUID v4
    message_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT NOT NULL,  -- Local storage path
    extracted_text TEXT,  -- Extracted content for context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_sessions_last_accessed ON sessions(last_accessed);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_file_uploads_message ON file_uploads(message_id);
```

**Pydantic Models (Backend):**

```python
# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID

class SessionCreate(BaseModel):
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class Session(BaseModel):
    id: str
    created_at: datetime
    last_accessed: datetime
    user_agent: Optional[str]
    ip_address: Optional[str]

class ConversationCreate(BaseModel):
    session_id: str
    title: Optional[str] = None

class Conversation(BaseModel):
    id: str
    session_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    message_count: int = 0

class MessageCreate(BaseModel):
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    model_name: Optional[str] = "gpt-4o-mini"

class Message(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime
    token_count: Optional[int]
    model_name: Optional[str]

class FileUploadCreate(BaseModel):
    message_id: str
    filename: str
    file_type: str
    file_size: int
    file_path: str
    extracted_text: Optional[str]

class FileUpload(BaseModel):
    id: str
    message_id: str
    filename: str
    file_type: str
    file_size: int
    file_path: str
    extracted_text: Optional[str]
    created_at: datetime

# API Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    session_id: str
    files: Optional[List[str]] = Field(default_factory=list)  # File IDs

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    # Response will be streamed, this is for metadata

class ConversationListResponse(BaseModel):
    conversations: List[Conversation]
    total: int

class MessageHistoryResponse(BaseModel):
    messages: List[Message]
    conversation: Conversation
```

**Frontend TypeScript Interfaces (React):**

```typescript
// frontend-react/src/types/chat.ts

export interface Session {
  id: string;
  createdAt: Date;
  lastAccessed: Date;
}

export interface Conversation {
  id: string;
  sessionId: string;
  title: string | null;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  messageCount: number;
}

export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: Date;
  tokenCount?: number;
  modelName?: string;
  files?: FileUpload[];  // Attached files
}

export interface FileUpload {
  id: string;
  messageId: string;
  filename: string;
  fileType: string;
  fileSize: number;
  extractedText?: string;
  createdAt: Date;
}

// API Types
export interface ChatRequest {
  message: string;
  conversationId?: string;
  sessionId: string;
  files?: string[];  // File IDs
}

export interface StreamToken {
  token: string;
  finished: boolean;
  messageId?: string;
  conversationId?: string;
}

// Frontend State Types
export interface ChatState {
  currentConversation: Conversation | null;
  conversations: Conversation[];
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
}
```

**Session Storage Structure:**

```javascript
// localStorage structure
{
  "chatbot_session": {
    "sessionId": "uuid-v4",
    "createdAt": "2025-07-22T10:00:00Z",
    "currentConversationId": "uuid-v4" | null
  }
}

// Cookies (for backend session tracking)
chatbot_session_id=uuid-v4; HttpOnly; Secure; SameSite=Strict
```

### 11.3 API Contracts

**POST /api/chat**
```json
Request:
{
  "message": "string",
  "session_id": "string",
  "conversation_id": "string"
}

Response: SSE Stream
data: {"token": "Hello", "finished": false}
data: {"token": " there", "finished": false}
data: {"token": "!", "finished": true}
```

**GET /api/conversations**
```json
Response:
{
  "conversations": [
    {
      "id": "string",
      "title": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

### 11.3 Technology Stack Details

**Backend:**
- Python 3.11+
- FastAPI 0.111+
- OpenAI Python SDK
- SQLite/PostgreSQL
- Redis (production)
- UV package manager

**Frontend (React):**
- React 18+
- TypeScript 5+
- Tailwind CSS
- Axios for API calls
- React Router
- Zustand/Redux for state

**Infrastructure:**
- Docker 24+
- Docker Compose
- Nginx (reverse proxy)
- GitHub Actions (CI/CD)

### 11.4 File Upload Processing

**Supported File Types:**
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (text extraction)
- `.py`, `.js`, `.json` - Code files
- Images - For future OCR support

**Processing Pipeline:**
```python
# Pseudocode for file handling
async def process_upload(file: UploadFile):
    # 1. Validate file type and size
    # 2. Extract text content
    # 3. Add to message context
    # 4. Include in AI prompt
```

### 11.5 Example Deployment Script

```bash
#!/bin/bash
# deploy.sh - Simple VPS deployment

# Pull latest code
git pull origin main

# Build and restart containers
docker-compose down
docker-compose build
docker-compose up -d

# Check health
sleep 10
curl http://localhost:8000/health || echo "Deployment failed!"
```

### 11.6 Learning Resources

**For FastAPI:**
- Official FastAPI documentation
- Real Python FastAPI tutorials
- This project's `/docs/LEARNING_PATH.md`

**For React:**
- React official tutorial
- Comparing Streamlit and React implementations
- Custom hooks examples in this project

**For Deployment:**
- Docker basics in `/docs/DEPLOYMENT.md`
- VPS setup guides
- Nginx reverse proxy configuration

---

## Next Steps

1. **Set up development environment** - Start with the backend and Streamlit
2. **Join the community** - Star the repo, open issues, ask questions
3. **Build incrementally** - Don't try to implement everything at once
4. **Document your journey** - Help others learn from your experience
5. **Have fun learning!** - This is a judgment-free learning project

Remember: This PRD is a living document. As an open-source learning project, it should evolve based on community needs and contributions. The goal is not perfection but education and practical implementation.

**Happy Coding! 🚀**
