# 🔌 API Integration Guide - Backend to Frontend

## 📋 Backend API Overview

Tu backend FastAPI expone los siguientes endpoints principales:

### 🔐 Authentication (`/auth`)
```typescript
// Login
POST /auth/login
Content-Type: application/x-www-form-urlencoded
Body: { username: string, password: string }
Response: { access_token: string, token_type: "bearer" }

// Register
POST /auth/register
Body: { username: string, email: string, password: string, full_name: string }
Response: User

// Current User
GET /auth/me
Headers: { Authorization: "Bearer <token>" }
Response: User
```

### 📚 Books (`/books`)
```typescript
// List Books
GET /books/
Query: { skip?: number, limit?: number }
Response: Book[]

// Create Book
POST /books/
Body: { title: string, author: string, isbn?: string, genre: string, book_type: string }
Response: Book

// Get Book
GET /books/{book_id}
Response: Book

// Update Book
PUT /books/{book_id}
Body: Partial<Book>
Response: Book

// Delete Book
DELETE /books/{book_id}
Response: 204 No Content
```

### 🔄 Loans (`/loans`)
```typescript
// Request Loan
POST /loans/request
Query: { book_id: string, borrower_id: string }
Response: { loan_id: string, message: string }

// Immediate Loan
POST /loans/loan
Query: { book_id: string, borrower_id: string }
Response: { loan_id: string, message: string }

// Approve Loan
POST /loans/{loan_id}/approve
Query: { lender_id: string }
Response: { loan_id: string, status: string }

// Reject Loan
POST /loans/{loan_id}/reject
Query: { lender_id: string }
Response: { loan_id: string, status: string }

// Return Book
POST /loans/return
Query: { book_id: string }
Response: { message: string }

// List User Loans
GET /loans/
Query: { user_id?: string }
Response: Loan[]

// Loan History
GET /loans/history/book/{book_id}
Response: Loan[]
```

### 👥 Groups (`/groups`)
```typescript
// Create Group
POST /groups/
Body: { name: string, description?: string, is_public: boolean }
Response: Group

// List Groups
GET /groups/
Response: Group[]

// Get Group
GET /groups/{group_id}
Response: Group

// Join Group
POST /groups/{group_id}/join
Response: { message: string }

// Leave Group
POST /groups/{group_id}/leave
Response: { message: string }
```

### 💬 Chat (`/chat`)
```typescript
// Send Message
POST /chat/send
Body: { recipient_id: string, content: string, group_id?: string }
Response: Message

// Get Messages
GET /chat/messages
Query: { user_id?: string, group_id?: string, limit?: number }
Response: Message[]
```

### 🔍 Search (`/search`)
```typescript
// Search Books
GET /search/books
Query: { query: string, limit?: number }
Response: Book[]

// External Search
GET /search/external
Query: { query: string, source?: string }
Response: ExternalBook[]
```

### 📷 Scan (`/scan`)
```typescript
// Scan Barcode
POST /scan/barcode
Body: FormData with image file
Response: { isbn: string, book_info?: Book }

// OCR Text
POST /scan/ocr
Body: FormData with image file
Response: { text: string, extracted_info?: Book }
```

### 👤 Users (`/users`)
```typescript
// Get User
GET /users/{user_id}
Response: User

// Update User
PUT /users/{user_id}
Body: Partial<User>
Response: User

// Search Users
GET /users/search
Query: { query: string }
Response: User[]
```

## 🛠️ Frontend Service Implementation

### 1. Base API Configuration

```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);
```

### 2. Authentication Service

```typescript
// src/services/authService.ts
import { api } from './api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

export const authService = {
  async login(credentials: LoginCredentials) {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
  }
};
```

### 3. Books Service

```typescript
// src/services/booksService.ts
import { api } from './api';

export interface BookCreateData {
  title: string;
  author: string;
  isbn?: string;
  genre: string;
  book_type: 'physical' | 'digital';
  description?: string;
}

export const booksService = {
  async getBooks(skip = 0, limit = 20) {
    const response = await api.get('/books/', {
      params: { skip, limit }
    });
    return response.data;
  },

  async createBook(data: BookCreateData) {
    const response = await api.post('/books/', data);
    return response.data;
  },

  async getBook(bookId: string) {
    const response = await api.get(`/books/${bookId}`);
    return response.data;
  },

  async updateBook(bookId: string, data: Partial<BookCreateData>) {
    const response = await api.put(`/books/${bookId}`, data);
    return response.data;
  },

  async deleteBook(bookId: string) {
    await api.delete(`/books/${bookId}`);
  },

  async uploadCover(bookId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/books/${bookId}/cover`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};
```

### 4. Loans Service

```typescript
// src/services/loansService.ts
import { api } from './api';

export const loansService = {
  async requestLoan(bookId: string, borrowerId: string) {
    const response = await api.post('/loans/request', null, {
      params: { book_id: bookId, borrower_id: borrowerId }
    });
    return response.data;
  },

  async createImmediateLoan(bookId: string, borrowerId: string) {
    const response = await api.post('/loans/loan', null, {
      params: { book_id: bookId, borrower_id: borrowerId }
    });
    return response.data;
  },

  async approveLoan(loanId: string, lenderId: string) {
    const response = await api.post(`/loans/${loanId}/approve`, null, {
      params: { lender_id: lenderId }
    });
    return response.data;
  },

  async rejectLoan(loanId: string, lenderId: string) {
    const response = await api.post(`/loans/${loanId}/reject`, null, {
      params: { lender_id: lenderId }
    });
    return response.data;
  },

  async returnBook(bookId: string) {
    const response = await api.post('/loans/return', null, {
      params: { book_id: bookId }
    });
    return response.data;
  },

  async getUserLoans(userId?: string) {
    const response = await api.get('/loans/', {
      params: userId ? { user_id: userId } : {}
    });
    return response.data;
  },

  async getBookHistory(bookId: string) {
    const response = await api.get(`/loans/history/book/${bookId}`);
    return response.data;
  }
};
```

### 5. Groups Service

```typescript
// src/services/groupsService.ts
import { api } from './api';

export interface GroupCreateData {
  name: string;
  description?: string;
  is_public: boolean;
}

export const groupsService = {
  async createGroup(data: GroupCreateData) {
    const response = await api.post('/groups/', data);
    return response.data;
  },

  async getGroups() {
    const response = await api.get('/groups/');
    return response.data;
  },

  async getGroup(groupId: string) {
    const response = await api.get(`/groups/${groupId}`);
    return response.data;
  },

  async joinGroup(groupId: string) {
    const response = await api.post(`/groups/${groupId}/join`);
    return response.data;
  },

  async leaveGroup(groupId: string) {
    const response = await api.post(`/groups/${groupId}/leave`);
    return response.data;
  }
};
```

### 6. Chat Service

```typescript
// src/services/chatService.ts
import { api } from './api';

export interface MessageData {
  recipient_id: string;
  content: string;
  group_id?: string;
}

export const chatService = {
  async sendMessage(data: MessageData) {
    const response = await api.post('/chat/send', data);
    return response.data;
  },

  async getMessages(userId?: string, groupId?: string, limit = 50) {
    const response = await api.get('/chat/messages', {
      params: { user_id: userId, group_id: groupId, limit }
    });
    return response.data;
  }
};
```

### 7. Search Service

```typescript
// src/services/searchService.ts
import { api } from './api';

export const searchService = {
  async searchBooks(query: string, limit = 20) {
    const response = await api.get('/search/books', {
      params: { query, limit }
    });
    return response.data;
  },

  async searchExternal(query: string, source?: string) {
    const response = await api.get('/search/external', {
      params: { query, source }
    });
    return response.data;
  }
};
```

### 8. Scan Service

```typescript
// src/services/scanService.ts
import { api } from './api';

export const scanService = {
  async scanBarcode(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/scan/barcode', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async scanOCR(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/scan/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};
```

## 🔄 React Query Integration

### 1. Query Client Setup

```typescript
// src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

### 2. Custom Hooks

```typescript
// src/hooks/useBooks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { booksService } from '../services/booksService';

export const useBooks = (skip = 0, limit = 20) => {
  return useQuery({
    queryKey: ['books', skip, limit],
    queryFn: () => booksService.getBooks(skip, limit),
  });
};

export const useBook = (bookId: string) => {
  return useQuery({
    queryKey: ['book', bookId],
    queryFn: () => booksService.getBook(bookId),
    enabled: !!bookId,
  });
};

export const useCreateBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: booksService.createBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useUpdateBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ bookId, data }: { bookId: string; data: any }) =>
      booksService.updateBook(bookId, data),
    onSuccess: (_, { bookId }) => {
      queryClient.invalidateQueries({ queryKey: ['book', bookId] });
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};
```

### 3. Loans Hooks

```typescript
// src/hooks/useLoans.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { loansService } from '../services/loansService';

export const useUserLoans = (userId?: string) => {
  return useQuery({
    queryKey: ['loans', userId],
    queryFn: () => loansService.getUserLoans(userId),
  });
};

export const useRequestLoan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ bookId, borrowerId }: { bookId: string; borrowerId: string }) =>
      loansService.requestLoan(bookId, borrowerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
};

export const useApproveLoan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ loanId, lenderId }: { loanId: string; lenderId: string }) =>
      loansService.approveLoan(loanId, lenderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
    },
  });
};
```

## 🌐 WebSocket Integration (Chat)

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../stores/authStore';

export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (!user) return;

    const ws = new WebSocket(`${url}?token=${localStorage.getItem('access_token')}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
    };

    return () => {
      ws.close();
    };
  }, [url, user]);

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  return { socket, messages, isConnected, sendMessage };
};
```

## 🔧 Error Handling

```typescript
// src/utils/errorHandler.ts
import { AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

export const handleApiError = (error: AxiosError) => {
  if (error.response?.status === 401) {
    toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
    localStorage.removeItem('access_token');
    window.location.href = '/auth/login';
    return;
  }

  if (error.response?.status === 403) {
    toast.error('No tienes permisos para realizar esta acción.');
    return;
  }

  if (error.response?.status === 404) {
    toast.error('Recurso no encontrado.');
    return;
  }

  if (error.response?.status >= 500) {
    toast.error('Error del servidor. Intenta nuevamente más tarde.');
    return;
  }

  const message = error.response?.data?.detail || 'Error inesperado';
  toast.error(message);
};
```

## 📝 Usage Examples

### Authentication Flow
```typescript
// Login component
const { mutate: login, isLoading } = useMutation({
  mutationFn: authService.login,
  onSuccess: (data) => {
    localStorage.setItem('access_token', data.access_token);
    router.push('/dashboard');
  },
  onError: handleApiError,
});
```

### Books Management
```typescript
// Books list component
const { data: books, isLoading } = useBooks();
const { mutate: createBook } = useCreateBook();

const handleCreateBook = (bookData) => {
  createBook(bookData, {
    onSuccess: () => toast.success('Libro creado exitosamente'),
    onError: handleApiError,
  });
};
```

### Real-time Chat
```typescript
// Chat component
const { messages, sendMessage, isConnected } = useWebSocket('ws://localhost:8000/ws/chat');

const handleSendMessage = (content: string) => {
  sendMessage({
    type: 'message',
    content,
    recipient_id: selectedUser.id,
  });
};
```

Esta guía te proporciona todo lo necesario para integrar tu frontend con el backend FastAPI existente de manera eficiente y escalable.
