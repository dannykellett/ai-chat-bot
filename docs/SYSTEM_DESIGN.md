# AI Chatbot System Design Document

**Version:** 1.0
**Date:** July 22, 2025
**Status:** Initial Design

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture Design](#2-architecture-design)
3. [Backend Design](#3-backend-design)
4. [Frontend Design](#4-frontend-design)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [Streaming Architecture](#7-streaming-architecture)
8. [Session Management](#8-session-management)
9. [File Processing Pipeline](#9-file-processing-pipeline)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Security Design](#11-security-design)
12. [Performance Considerations](#12-performance-considerations)
13. [Error Handling Strategy](#13-error-handling-strategy)
14. [Testing Strategy](#14-testing-strategy)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
├─────────────────────────┬───────────────────────────────────────┤
│   Streamlit Frontend    │         React Frontend                │
│   (Reference Impl)      │      (Learning Focus)                 │
└───────────┬─────────────┴────────────┬──────────────────────────┘
            │                          │
            │     HTTP/HTTPS/SSE       │
            └──────────┬───────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                    API Gateway (Nginx)                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                  FastAPI Application                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    API Layer                            │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │   Chat   │  │  Files   │  │ Sessions │            │    │
│  │  │ Endpoint │  │ Endpoint │  │ Endpoint │            │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘            │    │
│  └───────┼──────────────┼─────────────┼───────────────────┘    │
│          │              │             │                         │
│  ┌───────▼──────────────▼─────────────▼───────────────────┐    │
│  │                 Service Layer                           │    │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐ │    │
│  │  │ OpenAI  │  │Streaming│  │   File   │  │ Session │ │    │
│  │  │ Service │  │ Service │  │Processor │  │ Manager │ │    │
│  │  └────┬────┘  └────┬────┘  └────┬─────┘  └────┬────┘ │    │
│  └───────┼─────────────┼────────────┼──────────────┼──────┘    │
│          │             │            │              │           │
│  ┌───────▼─────────────▼────────────▼──────────────▼──────┐    │
│  │              Data Access Layer                         │    │
│  │        SQLAlchemy ORM with Repository Pattern          │    │
│  └────────────────────────┬───────────────────────────────┘    │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                ┌───────────▼────────────┐
                │  SQLite Database       │
                │  ┌─────────────────┐   │
                │  │    Sessions     │   │
                │  ├─────────────────┤   │
                │  │  Conversations  │   │
                │  ├─────────────────┤   │
                │  │    Messages     │   │
                │  ├─────────────────┤   │
                │  │  File Uploads   │   │
                │  └─────────────────┘   │
                └────────────────────────┘
```

### 1.2 Component Responsibilities

- **Client Layer**: User interface and interaction
- **API Gateway**: Request routing, SSL termination, load balancing
- **FastAPI Application**: Business logic and request handling
- **Service Layer**: Core functionality implementation
- **Data Access Layer**: Database abstraction and persistence
- **Database**: Data storage and retrieval

---

## 2. Architecture Design

### 2.1 Design Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Single Responsibility**: Each component has one clear purpose
3. **Dependency Injection**: Loose coupling through DI
4. **Clean Architecture**: Business logic independent of frameworks
5. **Event-Driven**: Streaming responses using SSE
6. **Stateless Design**: Session state in database/client

### 2.2 Technology Stack

```yaml
Backend:
  Language: Python 3.11+
  Framework: FastAPI
  ORM: SQLAlchemy (async)
  Database: SQLite (dev), PostgreSQL (prod option)
  Package Manager: UV
  Async: asyncio, aiofiles

Frontend:
  Streamlit:
    Language: Python
    Framework: Streamlit
    State: Session State

  React:
    Language: TypeScript/JavaScript
    Framework: React 18+
    State: Context API / Zustand
    Styling: Tailwind CSS
    Build: Vite

Infrastructure:
  Containerization: Docker
  Orchestration: Docker Compose
  Reverse Proxy: Nginx
  Process Manager: Gunicorn/Uvicorn
```

### 2.3 Architectural Patterns

- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Dependency Injection**: FastAPI's dependency system
- **Event Streaming**: Server-Sent Events for real-time
- **Session Facade**: Anonymous user management

---

## 3. Backend Design

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection setup
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py         # Chat endpoints
│   │   │   ├── conversations.py # Conversation management
│   │   │   ├── files.py        # File upload handling
│   │   │   └── sessions.py     # Session management
│   │   └── deps.py             # API dependencies
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and env vars
│   │   ├── security.py         # Security utilities
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── file_upload.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── file_upload.py
│   │   └── chat.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── openai_service.py   # OpenAI integration
│   │   ├── streaming_service.py # SSE streaming
│   │   ├── chat_service.py     # Chat orchestration
│   │   ├── file_service.py     # File processing
│   │   └── session_service.py  # Session management
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   ├── session_repo.py
│   │   ├── conversation_repo.py
│   │   ├── message_repo.py
│   │   └── file_upload_repo.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── database.py         # Database connection
│       ├── validators.py       # Input validation
│       └── file_utils.py       # File handling
│
├── migrations/                 # Database migrations
├── tests/                      # Test suite
├── requirements.txt
├── .env.example
└── Dockerfile
```

### 3.2 Service Layer Design

```python
# services/chat_service.py
class ChatService:
    def __init__(
        self,
        openai_service: OpenAIService,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        file_service: FileService
    ):
        self.openai = openai_service
        self.conversations = conversation_repo
        self.messages = message_repo
        self.files = file_service

    async def process_chat_message(
        self,
        session_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        file_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[StreamToken, None]:
        """
        Main chat processing pipeline:
        1. Validate session
        2. Create/retrieve conversation
        3. Process file attachments
        4. Build context from history
        5. Stream AI response
        6. Save messages
        """
        # Implementation details...
```

### 3.3 Repository Pattern Implementation

```python
# repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, schema: CreateSchemaType) -> ModelType:
        db_obj = self.model(**schema.dict())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: str) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
```

---

## 4. Frontend Design

### 4.1 React Architecture

```
frontend-react/
├── src/
│   ├── components/             # UI Components
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── chat/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatContainer.tsx
│   │   │   └── MessageList.tsx
│   │   ├── sidebar/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ConversationList.tsx
│   │   │   └── ConversationItem.tsx
│   │   └── upload/
│   │       ├── FileUpload.tsx
│   │       └── FilePreview.tsx
│   │
│   ├── hooks/                  # Custom Hooks
│   │   ├── useChat.ts          # Chat logic
│   │   ├── useStreaming.ts     # SSE handling
│   │   ├── useSession.ts       # Session management
│   │   └── useFileUpload.ts    # File handling
│   │
│   ├── services/               # API Services
│   │   ├── api.ts              # Base API client
│   │   ├── chatService.ts      # Chat endpoints
│   │   ├── fileService.ts      # File uploads
│   │   └── sessionService.ts   # Session handling
│   │
│   ├── store/                  # State Management
│   │   ├── chatStore.ts        # Zustand store
│   │   └── types.ts            # Store types
│   │
│   ├── types/                  # TypeScript Types
│   │   ├── chat.ts
│   │   ├── api.ts
│   │   └── index.ts
│   │
│   ├── utils/                  # Utilities
│   │   ├── constants.ts
│   │   ├── storage.ts          # localStorage wrapper
│   │   └── markdown.ts         # Markdown parsing
│   │
│   ├── styles/                 # Styling
│   │   ├── globals.css
│   │   └── tailwind.css
│   │
│   ├── App.tsx                 # Main App
│   ├── main.tsx               # Entry point
│   └── vite-env.d.ts
│
├── public/                     # Static assets
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile
```

### 4.2 Component Design

```typescript
// components/chat/ChatMessage.tsx
interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isStreaming
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`
        max-w-[70%] p-4 rounded-lg
        ${isUser
          ? 'bg-blue-500 text-white'
          : 'bg-gray-100 text-gray-800'}
      `}>
        <MarkdownRenderer content={message.content} />
        {message.files && <FileAttachments files={message.files} />}
        {isStreaming && <StreamingIndicator />}
      </div>
    </div>
  );
};
```

### 4.3 State Management Design

```typescript
// store/chatStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ChatState {
  // State
  session: Session | null;
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isStreaming: boolean;
  error: string | null;

  // Actions
  initializeSession: () => Promise<void>;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  sendMessage: (content: string, files?: File[]) => Promise<void>;
  createNewConversation: () => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        session: null,
        conversations: [],
        currentConversation: null,
        messages: [],
        isStreaming: false,
        error: null,

        // Action implementations...
      }),
      {
        name: 'chat-storage',
        partialize: (state) => ({
          session: state.session
        }),
      }
    )
  )
);
```

### 4.4 Custom Hooks Design

```typescript
// hooks/useStreaming.ts
export const useStreaming = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamedContent, setStreamedContent] = useState('');
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStreaming = useCallback(async (
    endpoint: string,
    payload: ChatRequest
  ) => {
    setIsStreaming(true);
    setStreamedContent('');

    try {
      // Create SSE connection
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            setStreamedContent(prev => prev + data.token);

            if (data.finished) {
              setIsStreaming(false);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setIsStreaming(false);
    }
  }, []);

  const stopStreaming = useCallback(() => {
    eventSourceRef.current?.close();
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    streamedContent,
    startStreaming,
    stopStreaming,
  };
};
```

---

## 5. Database Design

### 5.1 Entity Relationship Diagram

```
┌─────────────────┐
│    sessions     │
├─────────────────┤
│ id (PK)         │
│ created_at      │
│ last_accessed   │
│ user_agent      │
│ ip_address      │
└────────┬────────┘
         │ 1
         │
         │ *
┌────────▼────────┐         ┌─────────────────┐
│ conversations   │         │  file_uploads   │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ session_id (FK) │         │ message_id (FK) │
│ title           │         │ filename        │
│ created_at      │         │ file_type       │
│ updated_at      │         │ file_size       │
│ is_active       │         │ file_path       │
│ message_count   │         │ extracted_text  │
└────────┬────────┘         │ created_at      │
         │ 1                └─────────────────┘
         │                            ▲ *
         │ *                          │
┌────────▼────────┐                   │ 1
│    messages     │───────────────────┘
├─────────────────┤
│ id (PK)         │
│ conversation_id │
│ role            │
│ content         │
│ created_at      │
│ token_count     │
│ model_name      │
└─────────────────┘
```

### 5.2 Database Models

```python
# models/base.py
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# models/session.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel

class Session(BaseModel):
    __tablename__ = "sessions"

    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")

# models/conversation.py
class Conversation(BaseModel):
    __tablename__ = "conversations"

    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    title = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)

    # Relationships
    session = relationship("Session", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

### 5.3 Database Indexes and Optimization

```sql
-- Performance indexes
CREATE INDEX idx_sessions_last_accessed ON sessions(last_accessed DESC);
CREATE INDEX idx_conversations_session_updated ON conversations(session_id, updated_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_file_uploads_message ON file_uploads(message_id);

-- Composite indexes for common queries
CREATE INDEX idx_active_conversations ON conversations(session_id, is_active, updated_at DESC);
CREATE INDEX idx_recent_messages ON messages(conversation_id, created_at DESC);
```

---

## 6. API Design

### 6.1 RESTful Endpoints

```yaml
Chat Endpoints:
  POST /api/v1/chat:
    description: Send message and receive streaming response
    body:
      message: string
      conversation_id?: string
      session_id: string
      file_ids?: string[]
    response: SSE stream

  POST /api/v1/chat/feedback:
    description: Submit feedback for a message
    body:
      message_id: string
      feedback: positive | negative
      comment?: string

Conversation Endpoints:
  GET /api/v1/conversations:
    description: List conversations for session
    query:
      session_id: string
      limit?: number = 20
      offset?: number = 0
    response:
      conversations: Conversation[]
      total: number

  GET /api/v1/conversations/{id}:
    description: Get conversation with messages
    response:
      conversation: Conversation
      messages: Message[]

  DELETE /api/v1/conversations/{id}:
    description: Delete conversation

  PATCH /api/v1/conversations/{id}:
    description: Update conversation (title, etc)
    body:
      title?: string

File Endpoints:
  POST /api/v1/files/upload:
    description: Upload file for processing
    content-type: multipart/form-data
    body:
      file: File
      session_id: string
    response:
      file_id: string
      extracted_text?: string

  GET /api/v1/files/{id}:
    description: Get file metadata

  DELETE /api/v1/files/{id}:
    description: Delete uploaded file

Session Endpoints:
  POST /api/v1/sessions:
    description: Create new session
    body:
      user_agent?: string
    response:
      session: Session

  GET /api/v1/sessions/{id}:
    description: Validate session

Health Check:
  GET /api/v1/health:
    description: Service health status
    response:
      status: ok | degraded | down
      version: string
      uptime: number
```

### 6.2 API Error Responses

```typescript
interface APIError {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    request_id: string;
  };
}

// Error codes
enum ErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  SESSION_NOT_FOUND = "SESSION_NOT_FOUND",
  CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND",
  FILE_TOO_LARGE = "FILE_TOO_LARGE",
  UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE",
  RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",
  OPENAI_ERROR = "OPENAI_ERROR",
  INTERNAL_ERROR = "INTERNAL_ERROR",
}
```

---

## 7. Streaming Architecture

### 7.1 Server-Sent Events Implementation

```python
# services/streaming_service.py
from typing import AsyncGenerator
import json
import asyncio
from fastapi import Response
from fastapi.responses import StreamingResponse

class StreamingService:
    def __init__(self, openai_service: OpenAIService):
        self.openai = openai_service

    async def stream_chat_response(
        self,
        messages: List[dict],
        model: str = "gpt-4o-mini"
    ) -> AsyncGenerator[str, None]:
        """Generate SSE formatted streaming response"""
        try:
            # Get streaming response from OpenAI
            stream = await self.openai.create_chat_completion_stream(
                messages=messages,
                model=model
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content

                    # Format as SSE
                    data = {
                        "token": token,
                        "finished": False,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(data)}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'finished': True})}\n\n"

        except Exception as e:
            # Send error through SSE
            error_data = {
                "error": str(e),
                "finished": True
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    def create_sse_response(
        self,
        generator: AsyncGenerator[str, None]
    ) -> StreamingResponse:
        """Create FastAPI streaming response with proper headers"""
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable Nginx buffering
            }
        )
```

### 7.2 Client-Side SSE Handling

```typescript
// services/streamingClient.ts
export class StreamingClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async *streamChat(
    payload: ChatRequest
  ): AsyncGenerator<StreamToken, void, unknown> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // Keep the last incomplete line in buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data as StreamToken;

            if (data.finished) {
              return;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  }
}
```

---

## 8. Session Management

### 8.1 Anonymous Session Design

```python
# services/session_service.py
from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import jwt, JWTError

class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository,
        secret_key: str,
        session_duration: timedelta = timedelta(days=30)
    ):
        self.sessions = session_repo
        self.secret_key = secret_key
        self.session_duration = session_duration

    async def create_session(
        self,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> tuple[Session, str]:
        """Create new anonymous session and return session + token"""
        # Create session in database
        session = await self.sessions.create({
            "user_agent": user_agent,
            "ip_address": ip_address
        })

        # Generate JWT token
        token_data = {
            "session_id": session.id,
            "exp": datetime.utcnow() + self.session_duration
        }
        token = jwt.encode(token_data, self.secret_key, algorithm="HS256")

        return session, token

    async def validate_session(self, token: str) -> Optional[Session]:
        """Validate session token and update last accessed time"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            session_id = payload.get("session_id")

            if not session_id:
                return None

            session = await self.sessions.get(session_id)
            if session:
                # Update last accessed time
                await self.sessions.update_last_accessed(session_id)

            return session

        except JWTError:
            return None
```

### 8.2 Session Middleware

```python
# api/middleware.py
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class SessionMiddleware:
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
        self.security = HTTPBearer(auto_error=False)

    async def __call__(self, request: Request) -> Optional[Session]:
        # Try to get session from cookie first
        session_token = request.cookies.get("session_token")

        # Fallback to Authorization header
        if not session_token:
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if credentials:
                session_token = credentials.credentials

        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session required"
            )

        session = await self.session_service.validate_session(session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )

        return session
```

---

## 9. File Processing Pipeline

### 9.1 File Upload and Processing Flow

```python
# services/file_service.py
from typing import Optional, Dict, Any
import aiofiles
import hashlib
from pathlib import Path

class FileService:
    def __init__(
        self,
        upload_dir: Path,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_extensions: set = {'.txt', '.md', '.pdf', '.py', '.js', '.json'}
    ):
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions
        self.processors = self._init_processors()

    def _init_processors(self) -> Dict[str, FileProcessor]:
        """Initialize file processors for different types"""
        return {
            '.txt': TextFileProcessor(),
            '.md': TextFileProcessor(),
            '.pdf': PDFProcessor(),
            '.py': CodeFileProcessor(),
            '.js': CodeFileProcessor(),
            '.json': CodeFileProcessor(),
        }

    async def process_upload(
        self,
        file: UploadFile,
        session_id: str
    ) -> FileUploadResult:
        """Main file processing pipeline"""
        # 1. Validate file
        await self._validate_file(file)

        # 2. Generate unique filename
        file_hash = await self._calculate_file_hash(file)
        ext = Path(file.filename).suffix.lower()
        stored_filename = f"{session_id}_{file_hash}{ext}"
        file_path = self.upload_dir / stored_filename

        # 3. Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # 4. Extract text content
        processor = self.processors.get(ext, DefaultProcessor())
        extracted_text = await processor.extract_text(file_path)

        # 5. Create file record
        return FileUploadResult(
            filename=file.filename,
            stored_path=str(file_path),
            file_type=ext,
            file_size=len(content),
            extracted_text=extracted_text,
            file_hash=file_hash
        )
```

### 9.2 File Processors

```python
# services/file_processors.py
from abc import ABC, abstractmethod
import PyPDF2
import aiofiles

class FileProcessor(ABC):
    @abstractmethod
    async def extract_text(self, file_path: Path) -> str:
        """Extract text content from file"""
        pass

class TextFileProcessor(FileProcessor):
    async def extract_text(self, file_path: Path) -> str:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()

class PDFProcessor(FileProcessor):
    async def extract_text(self, file_path: Path) -> str:
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)

class CodeFileProcessor(FileProcessor):
    async def extract_text(self, file_path: Path) -> str:
        # Add syntax highlighting markers for better context
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            lang = file_path.suffix[1:]  # Remove dot
            return f"```{lang}\n{content}\n```"
```

---

## 10. Deployment Architecture

### 10.1 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend-react
      - frontend-streamlit
    networks:
      - chatbot-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SESSION_SECRET=${SESSION_SECRET}
      - DATABASE_URL=sqlite+aiosqlite:///./data/chat.db
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    networks:
      - chatbot-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend-react:
    build:
      context: ./frontend-react
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=http://backend:8000
    networks:
      - chatbot-network

  frontend-streamlit:
    build:
      context: ./frontend-streamlit
      dockerfile: Dockerfile
    environment:
      - API_URL=http://backend:8000
    networks:
      - chatbot-network

networks:
  chatbot-network:
    driver: bridge

volumes:
  data:
  uploads:
```

### 10.2 Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream react {
        server frontend-react:3000;
    }

    upstream streamlit {
        server frontend-streamlit:8501;
    }

    server {
        listen 80;
        server_name _;

        # React frontend (default)
        location / {
            proxy_pass http://react;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Streamlit frontend
        location /streamlit {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # SSE specific settings
            proxy_set_header Connection '';
            proxy_buffering off;
            proxy_cache off;
            chunked_transfer_encoding off;
        }

        # File uploads
        client_max_body_size 10M;
    }
}
```

### 10.3 Production Dockerfile Examples

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy requirements first for better caching
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/uploads

# Run migrations
RUN alembic upgrade head

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 11. Security Design

### 11.1 Security Measures

1. **Input Validation**
   - Pydantic models for request validation
   - File type and size restrictions
   - SQL injection prevention via ORM
   - XSS prevention in markdown rendering

2. **Session Security**
   - JWT tokens with expiration
   - HttpOnly cookies for web clients
   - Secure flag in production
   - CSRF protection

3. **API Security**
   - Rate limiting per session
   - Request size limits
   - Timeout configurations
   - Error message sanitization

4. **File Upload Security**
   - Virus scanning (optional)
   - File type validation
   - Isolated storage directory
   - Filename sanitization

### 11.2 Rate Limiting Implementation

```python
# core/rate_limiter.py
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 20,
        requests_per_hour: int = 100
    ):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.requests = defaultdict(list)
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        now = datetime.utcnow()

        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < timedelta(hours=1)
        ]

        # Check per-minute limit
        recent_minute = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < timedelta(minutes=1)
        ]

        if len(recent_minute) >= self.rpm:
            return False

        # Check per-hour limit
        if len(self.requests[identifier]) >= self.rph:
            return False

        # Record this request
        self.requests[identifier].append(now)
        return True
```

---

## 12. Performance Considerations

### 12.1 Optimization Strategies

1. **Database Optimization**
   - Connection pooling
   - Query optimization with proper indexes
   - Lazy loading relationships
   - Batch operations where possible

2. **Caching Strategy**
   - Redis for session data (production)
   - In-memory caching for file metadata
   - HTTP caching headers
   - CDN for static assets

3. **Async Operations**
   - Fully async database operations
   - Concurrent file processing
   - Non-blocking I/O throughout
   - Background task processing

4. **Frontend Optimization**
   - Code splitting in React
   - Lazy loading components
   - Image optimization
   - Bundle size monitoring

### 12.2 Monitoring and Metrics

```python
# utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter(
    'chatbot_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'chatbot_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

active_sessions = Gauge(
    'chatbot_active_sessions',
    'Number of active sessions'
)

streaming_connections = Gauge(
    'chatbot_streaming_connections',
    'Number of active streaming connections'
)

# Metrics middleware
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

---

## 13. Error Handling Strategy

### 13.1 Global Error Handler

```python
# core/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

class ChatbotException(Exception):
    """Base exception for all custom exceptions"""
    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)

class SessionNotFoundException(ChatbotException):
    def __init__(self, session_id: str):
        super().__init__(
            f"Session {session_id} not found",
            status_code=404,
            code="SESSION_NOT_FOUND"
        )

class RateLimitExceededException(ChatbotException):
    def __init__(self):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=429,
            code="RATE_LIMIT_EXCEEDED"
        )

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""

    if isinstance(exc, ChatbotException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url)
                }
            }
        )

    # Log unexpected errors
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url)
            }
        }
    )
```

### 13.2 Graceful Degradation

```python
# services/fallback_service.py
class FallbackService:
    """Provide fallback responses when primary services fail"""

    async def get_fallback_response(self, error_type: str) -> str:
        fallbacks = {
            "openai_unavailable": "I'm temporarily unable to process your request. Please try again in a moment.",
            "rate_limit": "You've sent too many messages. Please wait a bit before sending more.",
            "file_processing": "I couldn't process the uploaded file. Please try a different format.",
            "database_error": "I'm having trouble accessing conversation history right now."
        }

        return fallbacks.get(
            error_type,
            "Something went wrong. Please try again or start a new conversation."
        )
```

---

## 14. Testing Strategy

### 14.1 Test Structure

```
tests/
├── unit/
│   ├── test_services/
│   │   ├── test_chat_service.py
│   │   ├── test_file_service.py
│   │   └── test_session_service.py
│   ├── test_repositories/
│   └── test_utils/
├── integration/
│   ├── test_api/
│   │   ├── test_chat_endpoints.py
│   │   └── test_file_endpoints.py
│   └── test_database/
├── e2e/
│   ├── test_chat_flow.py
│   └── test_file_upload_flow.py
└── conftest.py
```

### 14.2 Testing Approach

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.utils.database import Base

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = AsyncSessionLocal(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.fixture
async def client(test_db):
    """Create test client with test database"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Example test
async def test_create_chat_session(client: AsyncClient):
    response = await client.post("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session" in data
    assert "id" in data["session"]
```

---

## Summary

This comprehensive system design provides:

1. **Clear Architecture**: Well-defined layers with specific responsibilities
2. **Scalable Design**: Can grow from SQLite to PostgreSQL, single server to distributed
3. **Learning-Friendly**: Clean code structure ideal for educational purposes
4. **Production-Ready Patterns**: Professional patterns that can be used in real applications
5. **Comprehensive Error Handling**: Graceful degradation and user-friendly errors
6. **Security First**: Built-in security measures appropriate for the use case
7. **Performance Optimized**: Async throughout, with caching and optimization strategies
8. **Testing Strategy**: Complete testing approach from unit to e2e

The design balances simplicity for learning with professional patterns that can scale, making it an ideal open-source educational project that can also serve as a foundation for production applications.
