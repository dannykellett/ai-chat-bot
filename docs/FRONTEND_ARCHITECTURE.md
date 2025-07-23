# Frontend Architecture Design

**Version:** 1.0
**Date:** July 22, 2025

---

## Table of Contents
1. [Overview](#overview)
2. [React Architecture](#react-architecture)
3. [Streamlit Architecture](#streamlit-architecture)
4. [Component Design System](#component-design-system)
5. [State Management](#state-management)
6. [Data Flow](#data-flow)
7. [Styling Strategy](#styling-strategy)
8. [Performance Optimization](#performance-optimization)
9. [Testing Strategy](#testing-strategy)

---

## Overview

This document outlines the frontend architecture for both React and Streamlit implementations, focusing on component design, state management, and user experience patterns.

### Design Principles
- **Component Reusability**: Build once, use everywhere
- **Type Safety**: TypeScript for React, type hints for Streamlit
- **Accessibility First**: WCAG 2.1 AA compliance
- **Performance**: Optimized rendering and data fetching
- **Learning Focus**: Clear patterns for educational purposes

---

## React Architecture

### 2.1 Project Structure

```
frontend-react/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Generic components
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   ├── Button.stories.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   └── LoadingSpinner/
│   │   ├── chat/            # Chat-specific components
│   │   │   ├── ChatMessage/
│   │   │   ├── ChatInput/
│   │   │   ├── MessageList/
│   │   │   └── StreamingIndicator/
│   │   ├── sidebar/         # Sidebar components
│   │   │   ├── Sidebar/
│   │   │   ├── ConversationList/
│   │   │   └── ConversationItem/
│   │   └── upload/          # File upload components
│   │       ├── FileUpload/
│   │       ├── FilePreview/
│   │       └── DragDropZone/
│   │
│   ├── features/            # Feature-based modules
│   │   ├── chat/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types/
│   │   ├── session/
│   │   └── files/
│   │
│   ├── hooks/               # Global custom hooks
│   │   ├── useApi.ts
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   └── useMediaQuery.ts
│   │
│   ├── layouts/             # Layout components
│   │   ├── MainLayout/
│   │   └── AuthLayout/
│   │
│   ├── lib/                 # External library configs
│   │   ├── axios.ts
│   │   └── markdown.ts
│   │
│   ├── pages/               # Route components
│   │   ├── ChatPage.tsx
│   │   └── ErrorPage.tsx
│   │
│   ├── services/            # API services
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── endpoints.ts
│   │   ├── chat/
│   │   ├── session/
│   │   └── files/
│   │
│   ├── store/               # State management
│   │   ├── index.ts
│   │   ├── slices/
│   │   └── middleware/
│   │
│   ├── styles/              # Global styles
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── tailwind.css
│   │
│   ├── types/               # TypeScript types
│   │   ├── api.types.ts
│   │   ├── chat.types.ts
│   │   └── global.d.ts
│   │
│   ├── utils/               # Utility functions
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── validators.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
│
├── public/                  # Static assets
├── tests/                   # Test setup
│   ├── setup.ts
│   └── utils.tsx
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

### 2.2 Component Architecture

#### Base Component Pattern
```typescript
// components/common/Button/Button.tsx
import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        ghost: 'hover:bg-gray-100 hover:text-gray-900',
        danger: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4',
        lg: 'h-12 px-6 text-base',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant,
    size,
    fullWidth,
    isLoading,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props
  }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <LoadingSpinner className="mr-2 h-4 w-4" />
        ) : leftIcon ? (
          <span className="mr-2">{leftIcon}</span>
        ) : null}
        {children}
        {rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

#### Complex Component Example
```typescript
// components/chat/ChatMessage/ChatMessage.tsx
import React, { memo } from 'react';
import { format } from 'date-fns';
import { cn } from '@/utils/cn';
import { Message } from '@/types/chat.types';
import { MarkdownRenderer } from '@/components/common/MarkdownRenderer';
import { FileAttachment } from '@/components/upload/FileAttachment';
import { Avatar } from '@/components/common/Avatar';
import { CopyButton } from '@/components/common/CopyButton';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  showTimestamp?: boolean;
  onRetry?: () => void;
  onEdit?: () => void;
  className?: string;
}

export const ChatMessage = memo<ChatMessageProps>(({
  message,
  isStreaming = false,
  showTimestamp = true,
  onRetry,
  onEdit,
  className,
}) => {
  const isUser = message.role === 'user';
  const isError = message.status === 'error';

  return (
    <div
      className={cn(
        'group relative flex gap-3 p-4 hover:bg-gray-50',
        isUser && 'flex-row-reverse',
        className
      )}
      data-testid={`message-${message.id}`}
    >
      {/* Avatar */}
      <Avatar
        src={isUser ? undefined : '/ai-avatar.svg'}
        alt={isUser ? 'User' : 'AI Assistant'}
        fallback={isUser ? 'U' : 'AI'}
        className="flex-shrink-0"
      />

      {/* Message Content */}
      <div className={cn('flex-1 space-y-2', isUser && 'text-right')}>
        {/* Header */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="font-medium">
            {isUser ? 'You' : 'Assistant'}
          </span>
          {showTimestamp && (
            <time dateTime={message.created_at}>
              {format(new Date(message.created_at), 'HH:mm')}
            </time>
          )}
        </div>

        {/* Message Body */}
        <div
          className={cn(
            'inline-block rounded-lg px-4 py-2',
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900',
            isError && 'bg-red-100 text-red-900'
          )}
        >
          <MarkdownRenderer
            content={message.content}
            className={isUser ? 'prose-invert' : ''}
          />

          {/* Streaming Indicator */}
          {isStreaming && (
            <span className="inline-flex ml-1">
              <span className="animate-pulse">▋</span>
            </span>
          )}
        </div>

        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {message.attachments.map((file) => (
              <FileAttachment key={file.id} file={file} />
            ))}
          </div>
        )}

        {/* Actions */}
        <div className={cn(
          'flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity',
          isUser ? 'justify-end' : 'justify-start'
        )}>
          {!isUser && (
            <CopyButton
              text={message.content}
              className="text-xs"
            />
          )}
          {isUser && onEdit && (
            <button
              onClick={onEdit}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Edit
            </button>
          )}
          {isError && onRetry && (
            <button
              onClick={onRetry}
              className="text-xs text-red-600 hover:text-red-700"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
});

ChatMessage.displayName = 'ChatMessage';
```

### 2.3 Custom Hooks

#### useChat Hook
```typescript
// features/chat/hooks/useChat.ts
import { useCallback, useRef, useState } from 'react';
import { useChatStore } from '@/store';
import { useSession } from '@/features/session/hooks/useSession';
import { chatService } from '@/services/chat';
import { Message, StreamEvent } from '@/types/chat.types';

export const useChat = (conversationId?: string) => {
  const { session } = useSession();
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamedContent, setStreamedContent] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const {
    messages,
    addMessage,
    updateMessage,
    setError,
    clearError,
  } = useChatStore();

  const sendMessage = useCallback(async (
    content: string,
    fileIds?: string[]
  ) => {
    if (!session || isStreaming) return;

    clearError();
    setIsStreaming(true);
    setStreamedContent('');

    // Add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      attachments: fileIds ? fileIds.map(id => ({ id })) : undefined,
    };

    addMessage(userMessage);

    // Create abort controller
    abortControllerRef.current = new AbortController();

    try {
      // Start streaming
      const stream = chatService.streamMessage({
        message: content,
        conversation_id: conversationId,
        session_id: session.id,
        file_ids: fileIds,
      }, abortControllerRef.current.signal);

      let assistantMessageId: string | null = null;
      let accumulatedContent = '';

      for await (const event of stream) {
        switch (event.type) {
          case 'start':
            assistantMessageId = event.message_id;
            addMessage({
              id: assistantMessageId,
              role: 'assistant',
              content: '',
              created_at: new Date().toISOString(),
            });
            break;

          case 'token':
            accumulatedContent += event.content;
            setStreamedContent(accumulatedContent);
            if (assistantMessageId) {
              updateMessage(assistantMessageId, {
                content: accumulatedContent,
              });
            }
            break;

          case 'end':
            setIsStreaming(false);
            if (assistantMessageId && event.usage) {
              updateMessage(assistantMessageId, {
                usage: event.usage,
              });
            }
            break;

          case 'error':
            throw new Error(event.error.message);
        }
      }
    } catch (error) {
      setIsStreaming(false);
      if (error.name !== 'AbortError') {
        setError(error.message || 'Failed to send message');
      }
    }
  }, [session, isStreaming, conversationId]);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    messages,
    isStreaming,
    streamedContent,
    sendMessage,
    stopStreaming,
  };
};
```

#### useFileUpload Hook
```typescript
// features/files/hooks/useFileUpload.ts
import { useState, useCallback } from 'react';
import { fileService } from '@/services/files';
import { useSession } from '@/features/session/hooks/useSession';

interface UploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

export const useFileUpload = (options?: {
  maxSize?: number;
  acceptedTypes?: string[];
  onUploadComplete?: (fileId: string) => void;
}) => {
  const { session } = useSession();
  const [uploads, setUploads] = useState<Map<string, UploadProgress>>(new Map());

  const uploadFile = useCallback(async (file: File) => {
    if (!session) return;

    const uploadId = `${file.name}-${Date.now()}`;

    // Validate file
    if (options?.maxSize && file.size > options.maxSize) {
      setUploads(prev => new Map(prev).set(uploadId, {
        file,
        progress: 0,
        status: 'error',
        error: `File size exceeds ${options.maxSize / 1024 / 1024}MB limit`,
      }));
      return;
    }

    // Start upload
    setUploads(prev => new Map(prev).set(uploadId, {
      file,
      progress: 0,
      status: 'uploading',
    }));

    try {
      const response = await fileService.uploadFile(
        file,
        session.id,
        (progress) => {
          setUploads(prev => new Map(prev).set(uploadId, {
            file,
            progress,
            status: 'uploading',
          }));
        }
      );

      setUploads(prev => new Map(prev).set(uploadId, {
        file,
        progress: 100,
        status: 'completed',
      }));

      options?.onUploadComplete?.(response.file.id);

      return response.file;
    } catch (error) {
      setUploads(prev => new Map(prev).set(uploadId, {
        file,
        progress: 0,
        status: 'error',
        error: error.message,
      }));
      throw error;
    }
  }, [session, options]);

  const removeUpload = useCallback((uploadId: string) => {
    setUploads(prev => {
      const next = new Map(prev);
      next.delete(uploadId);
      return next;
    });
  }, []);

  return {
    uploads: Array.from(uploads.entries()),
    uploadFile,
    removeUpload,
  };
};
```

---

## Streamlit Architecture

### 3.1 Project Structure

```
frontend-streamlit/
├── app.py                   # Main application entry
├── components/              # Reusable components
│   ├── __init__.py
│   ├── chat_message.py      # Message display component
│   ├── chat_input.py        # Input with file upload
│   ├── sidebar.py           # Sidebar management
│   └── file_handler.py      # File upload handling
├── services/                # API communication
│   ├── __init__.py
│   ├── api_client.py        # Base API client
│   ├── chat_service.py      # Chat operations
│   └── session_service.py   # Session management
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── markdown.py          # Markdown rendering
│   ├── state.py             # Session state helpers
│   └── config.py            # Configuration
├── styles/                  # Custom CSS
│   └── main.css
├── requirements.txt
└── .env.example
```

### 3.2 Streamlit Components

#### Main Application Structure
```python
# app.py
import streamlit as st
from components import sidebar, chat_message, chat_input
from services import ChatService, SessionService
from utils import init_session_state, load_custom_css

# Page config
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Initialize session state
init_session_state()

# Initialize services
@st.cache_resource
def get_services():
    session_service = SessionService()
    chat_service = ChatService()
    return session_service, chat_service

session_service, chat_service = get_services()

# Layout
col1, col2 = st.columns([1, 3])

with col1:
    # Sidebar
    selected_conversation = sidebar.render(
        session_service=session_service,
        current_conversation=st.session_state.current_conversation
    )

    if selected_conversation != st.session_state.current_conversation:
        st.session_state.current_conversation = selected_conversation
        st.rerun()

with col2:
    # Main chat area
    st.title("AI Assistant")

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display messages
        if st.session_state.messages:
            for message in st.session_state.messages:
                chat_message.render(message)
        else:
            st.info("Start a conversation by typing a message below!")

    # Input area
    user_input, uploaded_files = chat_input.render()

    if user_input:
        # Handle message sending
        handle_send_message(user_input, uploaded_files)
```

#### Component Example
```python
# components/chat_message.py
import streamlit as st
from datetime import datetime
from utils.markdown import render_markdown

def render(message: dict):
    """Render a chat message with proper styling"""

    # Determine message alignment and styling
    is_user = message['role'] == 'user'
    avatar = "🧑" if is_user else "🤖"

    # Create message container
    with st.container():
        col1, col2, col3 = st.columns([1, 10, 1])

        if is_user:
            # User message (right-aligned)
            with col2:
                st.markdown(
                    f"""
                    <div class="message-container user-message">
                        <div class="message-content">
                            {render_markdown(message['content'])}
                        </div>
                        <div class="message-metadata">
                            {format_timestamp(message['created_at'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col3:
                st.markdown(avatar)
        else:
            # Assistant message (left-aligned)
            with col1:
                st.markdown(avatar)
            with col2:
                # Handle streaming
                if message.get('is_streaming', False):
                    with st.empty():
                        render_streaming_message(message)
                else:
                    st.markdown(
                        f"""
                        <div class="message-container assistant-message">
                            <div class="message-content">
                                {render_markdown(message['content'])}
                            </div>
                            <div class="message-metadata">
                                {format_timestamp(message['created_at'])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Render attachments if any
        if message.get('attachments'):
            render_attachments(message['attachments'])

def render_streaming_message(message: dict):
    """Handle streaming message display"""
    placeholder = st.empty()

    # This would be connected to actual streaming
    for chunk in message.get('stream', []):
        message['content'] += chunk
        placeholder.markdown(
            render_markdown(message['content']) + "▋"
        )

def render_attachments(attachments: list):
    """Render file attachments"""
    with st.expander(f"📎 {len(attachments)} file(s) attached"):
        for attachment in attachments:
            st.text(f"📄 {attachment['filename']} ({attachment['size_human']})")

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%I:%M %p")
```

### 3.3 State Management in Streamlit

```python
# utils/state.py
import streamlit as st
from typing import Any, Dict, List
import uuid

def init_session_state():
    """Initialize Streamlit session state with defaults"""

    defaults = {
        # Session management
        'session_id': None,
        'session_token': None,

        # Chat state
        'current_conversation': None,
        'conversations': [],
        'messages': [],
        'is_streaming': False,

        # UI state
        'show_sidebar': True,
        'input_disabled': False,
        'pending_files': [],

        # Settings
        'theme': 'light',
        'markdown_enabled': True,
        'auto_scroll': True,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

class ConversationManager:
    """Manage conversation state in Streamlit"""

    @staticmethod
    def create_new():
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        st.session_state.current_conversation = conversation_id
        st.session_state.messages = []
        return conversation_id

    @staticmethod
    def load_conversation(conversation_id: str, messages: List[Dict]):
        """Load an existing conversation"""
        st.session_state.current_conversation = conversation_id
        st.session_state.messages = messages

    @staticmethod
    def add_message(message: Dict):
        """Add a message to current conversation"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        st.session_state.messages.append({
            'id': str(uuid.uuid4()),
            'conversation_id': st.session_state.current_conversation,
            'created_at': datetime.now().isoformat(),
            **message
        })

    @staticmethod
    def update_last_message(content: str):
        """Update the last message (for streaming)"""
        if st.session_state.messages:
            st.session_state.messages[-1]['content'] = content
```

---

## Component Design System

### 4.1 Design Tokens

```typescript
// styles/tokens.ts
export const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
  },
  spacing: {
    xs: '0.5rem',
    sm: '0.75rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  typography: {
    fontFamily: {
      sans: 'Inter, system-ui, -apple-system, sans-serif',
      mono: 'Fira Code, monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
    },
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  },
};
```

### 4.2 Component Library

```typescript
// Component Categories and Examples

// Layout Components
- Container: Responsive container with max-width
- Grid: Flexible grid system
- Stack: Vertical/horizontal spacing utility
- Divider: Visual separator

// Navigation Components
- Navbar: Top navigation bar
- Sidebar: Collapsible sidebar
- Breadcrumb: Navigation trail
- Tabs: Tab navigation

// Input Components
- TextInput: Basic text input
- TextArea: Multi-line input
- Select: Dropdown selection
- Checkbox: Binary choice
- Radio: Single selection from group
- Switch: Toggle switch
- Slider: Range selection
- DatePicker: Date selection
- FilePicker: File selection

// Feedback Components
- Alert: Informational messages
- Toast: Temporary notifications
- Progress: Progress indicators
- Skeleton: Loading placeholders
- Spinner: Loading animation

// Overlay Components
- Modal: Dialog overlay
- Popover: Contextual overlay
- Tooltip: Hover information
- Drawer: Slide-out panel

// Data Display Components
- Table: Data tables
- Card: Content container
- Badge: Status indicators
- Avatar: User representation
- Chip: Compact elements

// Typography Components
- Heading: Semantic headings
- Text: Body text
- Code: Inline code
- Pre: Code blocks

// Utility Components
- Portal: Render outside DOM hierarchy
- Transition: Animation wrapper
- ErrorBoundary: Error handling
- LazyLoad: Deferred loading
```

---

## State Management

### 5.1 Zustand Store Architecture

```typescript
// store/index.ts
import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { createChatSlice, ChatSlice } from './slices/chatSlice';
import { createSessionSlice, SessionSlice } from './slices/sessionSlice';
import { createUISlice, UISlice } from './slices/uiSlice';

export type RootState = ChatSlice & SessionSlice & UISlice;

export const useStore = create<RootState>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((...a) => ({
          ...createChatSlice(...a),
          ...createSessionSlice(...a),
          ...createUISlice(...a),
        }))
      ),
      {
        name: 'chatbot-store',
        partialize: (state) => ({
          // Only persist specific parts
          session: state.session,
          theme: state.theme,
        }),
      }
    )
  )
);
```

### 5.2 Slice Example

```typescript
// store/slices/chatSlice.ts
import { StateCreator } from 'zustand';
import { produce } from 'immer';
import { Message, Conversation } from '@/types/chat.types';

export interface ChatSlice {
  // State
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Record<string, Message[]>; // Keyed by conversation ID
  isLoading: boolean;
  error: string | null;

  // Actions
  setConversations: (conversations: Conversation[]) => void;
  selectConversation: (id: string) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (conversationId: string, messageId: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const createChatSlice: StateCreator<ChatSlice> = (set, get) => ({
  // Initial state
  conversations: [],
  currentConversation: null,
  messages: {},
  isLoading: false,
  error: null,

  // Actions
  setConversations: (conversations) =>
    set((state) => {
      state.conversations = conversations;
    }),

  selectConversation: (id) =>
    set((state) => {
      state.currentConversation =
        state.conversations.find(c => c.id === id) || null;
    }),

  addMessage: (conversationId, message) =>
    set((state) => {
      if (!state.messages[conversationId]) {
        state.messages[conversationId] = [];
      }
      state.messages[conversationId].push(message);

      // Update conversation metadata
      const conversation = state.conversations.find(c => c.id === conversationId);
      if (conversation) {
        conversation.message_count += 1;
        conversation.updated_at = new Date().toISOString();
      }
    }),

  updateMessage: (conversationId, messageId, updates) =>
    set((state) => {
      const messages = state.messages[conversationId];
      if (messages) {
        const messageIndex = messages.findIndex(m => m.id === messageId);
        if (messageIndex !== -1) {
          messages[messageIndex] = { ...messages[messageIndex], ...updates };
        }
      }
    }),

  deleteMessage: (conversationId, messageId) =>
    set((state) => {
      const messages = state.messages[conversationId];
      if (messages) {
        state.messages[conversationId] = messages.filter(m => m.id !== messageId);
      }
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () => set({
    conversations: [],
    currentConversation: null,
    messages: {},
    isLoading: false,
    error: null,
  }),
});
```

---

## Data Flow

### 6.1 Application Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Action   │────▶│   Component     │────▶│   Custom Hook   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   UI Update     │◀────│   Store Update  │◀────│   API Service   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   Backend API   │
                                                 └─────────────────┘
```

### 6.2 Streaming Data Flow

```typescript
// Streaming message flow
User Input → API Request → SSE Connection → Token Stream → Store Updates → UI Renders

// Implementation
const streamFlow = async (message: string) => {
  // 1. User sends message
  const userMessage = createUserMessage(message);
  store.addMessage(userMessage);

  // 2. Start SSE connection
  const stream = await api.streamChat(message);

  // 3. Create assistant message placeholder
  const assistantMessage = createAssistantMessage();
  store.addMessage(assistantMessage);

  // 4. Process stream tokens
  for await (const token of stream) {
    // 5. Update message content
    store.updateMessage(assistantMessage.id, {
      content: assistantMessage.content + token
    });

    // 6. UI automatically re-renders
  }
};
```

---

## Styling Strategy

### 7.1 Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          ...colors.primary
        },
        gray: {
          ...colors.gray
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};
```

### 7.2 CSS Architecture

```
styles/
├── base/
│   ├── reset.css       # CSS reset/normalize
│   ├── typography.css  # Base typography
│   └── utilities.css   # Utility classes
├── components/
│   ├── buttons.css     # Button styles
│   ├── forms.css       # Form styles
│   └── cards.css       # Card styles
├── themes/
│   ├── light.css       # Light theme variables
│   └── dark.css        # Dark theme variables
└── main.css            # Main entry point
```

---

## Performance Optimization

### 8.1 React Optimization Techniques

```typescript
// 1. Code Splitting
const ChatPage = lazy(() => import('./pages/ChatPage'));

// 2. Memoization
const MemoizedMessage = memo(ChatMessage, (prev, next) => {
  return prev.message.id === next.message.id &&
         prev.message.content === next.message.content;
});

// 3. Virtual Scrolling for long message lists
import { VariableSizeList as List } from 'react-window';

const MessageList = ({ messages }) => (
  <List
    height={600}
    itemCount={messages.length}
    itemSize={(index) => getMessageHeight(messages[index])}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <ChatMessage message={messages[index]} />
      </div>
    )}
  </List>
);

// 4. Debounced search
const debouncedSearch = useMemo(
  () => debounce((query: string) => {
    searchConversations(query);
  }, 300),
  []
);

// 5. Image optimization
const OptimizedImage = ({ src, alt, ...props }) => (
  <img
    src={src}
    alt={alt}
    loading="lazy"
    decoding="async"
    {...props}
  />
);
```

### 8.2 Bundle Optimization

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui', 'class-variance-authority'],
          'utils': ['date-fns', 'lodash-es'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
```

---

## Testing Strategy

### 9.1 Component Testing

```typescript
// ChatMessage.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatMessage } from './ChatMessage';

describe('ChatMessage', () => {
  const mockMessage = {
    id: '1',
    role: 'user',
    content: 'Hello, world!',
    created_at: '2025-07-22T10:00:00Z',
  };

  it('renders user message correctly', () => {
    render(<ChatMessage message={mockMessage} />);

    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
  });

  it('shows copy button for assistant messages', async () => {
    const assistantMessage = { ...mockMessage, role: 'assistant' };
    render(<ChatMessage message={assistantMessage} />);

    const copyButton = screen.getByRole('button', { name: /copy/i });
    expect(copyButton).toBeInTheDocument();

    await userEvent.click(copyButton);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Hello, world!');
  });

  it('displays streaming indicator when streaming', () => {
    render(<ChatMessage message={mockMessage} isStreaming />);

    expect(screen.getByText('▋')).toBeInTheDocument();
  });
});
```

### 9.2 Integration Testing

```typescript
// useChat.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from './useChat';
import { chatService } from '@/services/chat';

jest.mock('@/services/chat');

describe('useChat', () => {
  it('sends message and updates state', async () => {
    const mockStream = [
      { type: 'start', message_id: '123' },
      { type: 'token', content: 'Hello' },
      { type: 'token', content: ' there' },
      { type: 'end', usage: { total_tokens: 10 } },
    ];

    chatService.streamMessage.mockReturnValue(mockStream);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hi');
    });

    await waitFor(() => {
      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[1].content).toBe('Hello there');
    });
  });
});
```

---

## Summary

This frontend architecture provides:

1. **Clear Structure**: Well-organized code with separation of concerns
2. **Type Safety**: Full TypeScript support in React
3. **Reusability**: Component-based architecture
4. **Performance**: Optimized rendering and data fetching
5. **Accessibility**: WCAG compliance built-in
6. **Testing**: Comprehensive testing strategy
7. **Learning Focus**: Clear patterns for educational purposes
8. **Scalability**: Architecture that can grow with the application
