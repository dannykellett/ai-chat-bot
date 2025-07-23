# AI Chatbot API Specification

**Version:** 1.0
**Base URL:** `https://api.chatbot.example.com`
**API Version:** `/api/v1`

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Headers](#common-headers)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Endpoints](#endpoints)
   - [Session Management](#session-management)
   - [Chat Operations](#chat-operations)
   - [Conversation Management](#conversation-management)
   - [File Operations](#file-operations)
   - [Health & Status](#health--status)
7. [Streaming Responses](#streaming-responses)
8. [WebSocket Events](#websocket-events)
9. [Data Models](#data-models)

---

## Overview

The AI Chatbot API provides a RESTful interface for managing chat sessions, conversations, and file uploads. The API supports real-time streaming responses using Server-Sent Events (SSE).

### API Principles
- RESTful design
- JSON request/response bodies
- UUID v4 for all identifiers
- ISO 8601 timestamps
- Consistent error responses
- Streaming support via SSE

---

## Authentication

The API uses session-based authentication with JWT tokens. Sessions are anonymous and don't require user registration.

### Session Token
```http
Authorization: Bearer <session_token>
```

Or via cookie:
```http
Cookie: session_token=<token>
```

### Token Lifecycle
- **Creation**: Via `POST /api/v1/sessions`
- **Duration**: 30 days
- **Renewal**: Automatic on activity
- **Validation**: On every request

---

## Common Headers

### Request Headers
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>  # Optional, for request tracking
```

### Response Headers
```http
Content-Type: application/json
X-Request-ID: <uuid>
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1627849200
```

---

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional context
    },
    "timestamp": "2025-07-22T10:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid session |
| `FORBIDDEN` | 403 | Access denied to resource |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `PAYLOAD_TOO_LARGE` | 413 | Request body too large |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | Invalid content type |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

Rate limits are applied per session:
- **Requests**: 20 per minute, 100 per hour
- **Streaming**: 5 concurrent streams
- **File Uploads**: 10 per hour

### Rate Limit Headers
```http
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1627849200
Retry-After: 60  # When rate limited
```

---

## Endpoints

### Session Management

#### Create Session
```http
POST /api/v1/sessions
```

**Request Body:**
```json
{
  "user_agent": "Mozilla/5.0...",  // Optional
  "timezone": "America/New_York"   // Optional
}
```

**Response:** `201 Created`
```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-07-22T10:00:00Z",
    "expires_at": "2025-08-21T10:00:00Z"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Session Info
```http
GET /api/v1/sessions/current
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-07-22T10:00:00Z",
    "last_accessed": "2025-07-22T10:30:00Z",
    "expires_at": "2025-08-21T10:00:00Z",
    "conversation_count": 5,
    "message_count": 42
  }
}
```

#### Delete Session
```http
DELETE /api/v1/sessions/current
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

### Chat Operations

#### Send Message (Streaming)
```http
POST /api/v1/chat
Authorization: Bearer <token>
Content-Type: application/json
Accept: text/event-stream
```

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "optional-conversation-id",
  "context": {
    "file_ids": ["file1-id", "file2-id"],
    "system_prompt": "You are a helpful assistant",  // Optional
    "temperature": 0.7,  // Optional, 0.0-1.0
    "max_tokens": 1000   // Optional
  }
}
```

**Response:** `200 OK` (SSE Stream)
```
data: {"type": "start", "conversation_id": "...", "message_id": "..."}

data: {"type": "token", "content": "Hello"}

data: {"type": "token", "content": "! I'm"}

data: {"type": "token", "content": " doing"}

data: {"type": "token", "content": " well"}

data: {"type": "token", "content": ", thank"}

data: {"type": "token", "content": " you"}

data: {"type": "token", "content": "!"}

data: {"type": "end", "finish_reason": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 8}}

data: [DONE]
```

#### Send Message (Non-Streaming)
```http
POST /api/v1/chat/complete
Authorization: Bearer <token>
```

**Request Body:** Same as streaming

**Response:** `200 OK`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "id": "msg-123",
    "role": "assistant",
    "content": "Hello! I'm doing well, thank you!",
    "created_at": "2025-07-22T10:00:00Z"
  },
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

#### Stop Generation
```http
POST /api/v1/chat/stop
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "msg-123"
}
```

**Response:** `200 OK`

---

### Conversation Management

#### List Conversations
```http
GET /api/v1/conversations?limit=20&offset=0&order_by=updated_at&order=desc
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (int): Max results (default: 20, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `order_by` (string): Sort field (created_at|updated_at|title)
- `order` (string): Sort order (asc|desc)
- `is_active` (bool): Filter by active status

**Response:** `200 OK`
```json
{
  "conversations": [
    {
      "id": "conv-123",
      "title": "Hello, how are you?",
      "created_at": "2025-07-22T10:00:00Z",
      "updated_at": "2025-07-22T10:30:00Z",
      "message_count": 10,
      "is_active": true,
      "last_message": {
        "role": "assistant",
        "content": "I'm doing well, thank you!",
        "created_at": "2025-07-22T10:30:00Z"
      }
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

#### Get Conversation
```http
GET /api/v1/conversations/{conversation_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "conversation": {
    "id": "conv-123",
    "title": "Hello, how are you?",
    "created_at": "2025-07-22T10:00:00Z",
    "updated_at": "2025-07-22T10:30:00Z",
    "message_count": 10,
    "is_active": true
  }
}
```

#### Get Conversation Messages
```http
GET /api/v1/conversations/{conversation_id}/messages?limit=50&before=<message_id>
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (int): Max messages (default: 50, max: 100)
- `before` (string): Get messages before this ID
- `after` (string): Get messages after this ID

**Response:** `200 OK`
```json
{
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Hello, how are you?",
      "created_at": "2025-07-22T10:00:00Z",
      "attachments": []
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "I'm doing well, thank you!",
      "created_at": "2025-07-22T10:00:05Z",
      "attachments": [],
      "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 8
      }
    }
  ],
  "pagination": {
    "has_more": true,
    "oldest_id": "msg-1",
    "newest_id": "msg-10"
  }
}
```

#### Update Conversation
```http
PATCH /api/v1/conversations/{conversation_id}
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "New conversation title",
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "conversation": {
    "id": "conv-123",
    "title": "New conversation title",
    "is_active": false,
    "updated_at": "2025-07-22T11:00:00Z"
  }
}
```

#### Delete Conversation
```http
DELETE /api/v1/conversations/{conversation_id}
Authorization: Bearer <token>
```

**Response:** `204 No Content`

#### Create New Conversation
```http
POST /api/v1/conversations
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Optional title",
  "first_message": "Hello!"  // Optional, creates first message
}
```

**Response:** `201 Created`
```json
{
  "conversation": {
    "id": "conv-456",
    "title": "Optional title",
    "created_at": "2025-07-22T11:00:00Z",
    "message_count": 1
  }
}
```

---

### File Operations

#### Upload File
```http
POST /api/v1/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: File content (max 10MB)
- `purpose`: "chat_context" | "reference"

**Supported File Types:**
- Text: `.txt`, `.md`
- Code: `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`
- Documents: `.pdf`
- Data: `.csv`

**Response:** `201 Created`
```json
{
  "file": {
    "id": "file-123",
    "filename": "document.pdf",
    "size": 102400,
    "type": "application/pdf",
    "purpose": "chat_context",
    "created_at": "2025-07-22T10:00:00Z",
    "extracted_text": "Document content...",
    "metadata": {
      "pages": 10,
      "word_count": 1500
    }
  }
}
```

#### Get File Info
```http
GET /api/v1/files/{file_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "file": {
    "id": "file-123",
    "filename": "document.pdf",
    "size": 102400,
    "type": "application/pdf",
    "purpose": "chat_context",
    "created_at": "2025-07-22T10:00:00Z",
    "usage_count": 3,
    "last_used": "2025-07-22T10:30:00Z"
  }
}
```

#### List Files
```http
GET /api/v1/files?limit=20&offset=0
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "files": [
    {
      "id": "file-123",
      "filename": "document.pdf",
      "size": 102400,
      "type": "application/pdf",
      "created_at": "2025-07-22T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "limit": 20,
    "offset": 0
  }
}
```

#### Delete File
```http
DELETE /api/v1/files/{file_id}
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

### Health & Status

#### Health Check
```http
GET /api/v1/health
```

No authentication required.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-07-22T10:00:00Z",
  "services": {
    "database": "healthy",
    "openai": "healthy",
    "file_storage": "healthy"
  },
  "uptime_seconds": 3600
}
```

#### API Info
```http
GET /api/v1/info
```

**Response:** `200 OK`
```json
{
  "api_version": "v1",
  "supported_models": ["gpt-4o-mini"],
  "features": {
    "streaming": true,
    "file_upload": true,
    "max_file_size": 10485760,
    "supported_file_types": [".txt", ".md", ".pdf", ".py", ".js", ".json"]
  },
  "rate_limits": {
    "requests_per_minute": 20,
    "requests_per_hour": 100,
    "concurrent_streams": 5
  }
}
```

---

## Streaming Responses

### Server-Sent Events Format

The chat endpoint uses SSE for streaming responses. Each event is a JSON object:

```typescript
interface StreamEvent {
  type: 'start' | 'token' | 'error' | 'end';
  // Additional fields based on type
}
```

### Event Types

#### Start Event
```json
{
  "type": "start",
  "conversation_id": "conv-123",
  "message_id": "msg-456",
  "model": "gpt-4o-mini"
}
```

#### Token Event
```json
{
  "type": "token",
  "content": "Hello",
  "index": 0
}
```

#### Error Event
```json
{
  "type": "error",
  "error": {
    "code": "STREAM_ERROR",
    "message": "Connection interrupted"
  }
}
```

#### End Event
```json
{
  "type": "end",
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

### Client Implementation Example

```javascript
const eventSource = new EventSource('/api/v1/chat', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'start':
      console.log('Stream started:', data.message_id);
      break;
    case 'token':
      process.stdout.write(data.content);
      break;
    case 'end':
      console.log('\nStream ended:', data.finish_reason);
      eventSource.close();
      break;
    case 'error':
      console.error('Stream error:', data.error);
      eventSource.close();
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

---

## WebSocket Events (Future Enhancement)

*Note: WebSocket support is planned for future versions for bidirectional communication.*

### Connection
```
wss://api.chatbot.example.com/ws?token=<session_token>
```

### Event Types
- `message.new`
- `message.update`
- `conversation.update`
- `typing.start`
- `typing.stop`

---

## Data Models

### Core Types

```typescript
// Base types
type UUID = string;  // UUID v4
type ISODateTime = string;  // ISO 8601

// Enums
type MessageRole = 'user' | 'assistant' | 'system';
type FileType = 'text' | 'code' | 'document' | 'data';
type ConversationStatus = 'active' | 'archived';

// Session
interface Session {
  id: UUID;
  created_at: ISODateTime;
  last_accessed: ISODateTime;
  expires_at: ISODateTime;
  metadata?: {
    user_agent?: string;
    ip_address?: string;
  };
}

// Conversation
interface Conversation {
  id: UUID;
  session_id: UUID;
  title: string;
  created_at: ISODateTime;
  updated_at: ISODateTime;
  message_count: number;
  is_active: boolean;
  metadata?: Record<string, any>;
}

// Message
interface Message {
  id: UUID;
  conversation_id: UUID;
  role: MessageRole;
  content: string;
  created_at: ISODateTime;
  attachments?: Attachment[];
  usage?: TokenUsage;
  metadata?: {
    model?: string;
    temperature?: number;
  };
}

// File/Attachment
interface Attachment {
  id: UUID;
  filename: string;
  size: number;
  type: string;  // MIME type
  created_at: ISODateTime;
  extracted_text?: string;
}

// Token Usage
interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

// Error
interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: ISODateTime;
  request_id?: UUID;
}

// Pagination
interface Pagination {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
```

---

## API Client Examples

### Python
```python
import requests
import sseclient

class ChatbotClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def send_message(self, message: str, conversation_id: str = None):
        response = requests.post(
            f"{self.base_url}/api/v1/chat",
            headers={**self.headers, "Accept": "text/event-stream"},
            json={
                "message": message,
                "conversation_id": conversation_id
            },
            stream=True
        )

        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            if data.get("type") == "token":
                yield data["content"]
```

### TypeScript
```typescript
class ChatbotClient {
  constructor(
    private baseUrl: string,
    private token: string
  ) {}

  async *sendMessage(
    message: string,
    conversationId?: string
  ): AsyncGenerator<string> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      })
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'token') {
            yield data.content;
          }
        }
      }
    }
  }
}
```

---

## Best Practices

### Request Guidelines
1. Always include a `User-Agent` header
2. Use UUID v4 for client-generated IDs
3. Implement exponential backoff for retries
4. Handle rate limits gracefully
5. Close SSE connections properly

### Security Recommendations
1. Always use HTTPS in production
2. Store tokens securely (HttpOnly cookies preferred)
3. Validate file types before upload
4. Implement request signing for sensitive operations
5. Monitor for abnormal usage patterns

### Performance Tips
1. Use streaming for long responses
2. Batch operations when possible
3. Implement client-side caching
4. Compress large payloads
5. Use pagination for list endpoints

---

## Changelog

### Version 1.0.0 (2025-07-22)
- Initial API specification
- Core endpoints for chat, conversations, and files
- SSE streaming support
- Anonymous session management
- File upload with text extraction

---

## Support

For API support and questions:
- GitHub Issues: https://github.com/example/ai-chatbot/issues
- API Status: https://status.chatbot.example.com
- Documentation: https://docs.chatbot.example.com
