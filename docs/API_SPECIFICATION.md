# REST API Specification & Contract Reference

All REST endpoints are rooted under `/api/v1`. Interactive Swagger UI documentation is accessible at `http://127.0.0.1:8000/docs`.

---

## 1. Authentication Endpoints

### Register User
- **Endpoint**: `POST /api/v1/auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123",
    "full_name": "Alice Chen",
    "bio": "Software Engineer"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "full_name": "Alice Chen",
      "bio": "Software Engineer",
      "avatar_url": "https://api.dicebear.com/...",
      "created_at": "2026-09-23T14:00:00Z"
    }
  }
  ```

---

### User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "username_or_email": "alice@example.com",
    "password": "password123"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "full_name": "Alice Chen",
      "avatar_url": "https://api.dicebear.com/..."
    }
  }
  ```

---

### Get Current User Profile
- **Endpoint**: `GET /api/v1/auth/me`
- **Access**: Authenticated (Bearer Token or Cookie)
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "full_name": "Alice Chen",
    "bio": "Software Engineer",
    "avatar_url": "https://api.dicebear.com/...",
    "created_at": "2026-09-23T14:00:00Z"
  }
  ```

---

## 2. Posts Endpoints

### List Published Posts
- **Endpoint**: `GET /api/v1/posts`
- **Access**: Public (Unauthenticated)
- **Query Parameters**:
  - `q` (string, optional): Full-text search across title, summary, content
  - `tag` (string, optional): Filter by tag
  - `author` (string, optional): Filter by author username
  - `skip` (int, default: 0): Pagination offset
  - `limit` (int, default: 20): Page size
- **Response** (`200 OK`):
  ```json
  [
    {
      "id": 1,
      "title": "Building High-Performance APIs with FastAPI",
      "slug": "building-high-performance-apis-fastapi",
      "summary": "An in-depth guide on async APIs...",
      "tags": "python,fastapi,backend",
      "is_published": true,
      "author_id": 1,
      "created_at": "2026-09-23T14:00:00Z",
      "updated_at": "2026-09-23T14:00:00Z",
      "reading_time_minutes": 4,
      "likes_count": 12,
      "comments_count": 3,
      "author": {
        "id": 1,
        "username": "alice",
        "full_name": "Alice Chen",
        "avatar_url": "https://api.dicebear.com/..."
      },
      "is_liked_by_viewer": false
    }
  ]
  ```

---

### Get Post Detail
- **Endpoint**: `GET /api/v1/posts/{id_or_slug}`
- **Access**: Public for published articles; Author-only for drafts
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "title": "Building High-Performance APIs with FastAPI",
    "slug": "building-high-performance-apis-fastapi",
    "content": "## Introduction...",
    "content_html": "<h2>Introduction</h2>...",
    "tags": "python,fastapi,backend",
    "is_published": true,
    "reading_time_minutes": 4,
    "likes_count": 12,
    "comments_count": 3,
    "author": { ... },
    "is_liked_by_viewer": true,
    "comments": [
      {
        "id": 1,
        "content": "Great explanation!",
        "post_id": 1,
        "author_id": 2,
        "created_at": "2026-09-23T14:15:00Z",
        "author": { "username": "bob", "full_name": "Bob Martinez" }
      }
    ]
  }
  ```

---

### Create Post
- **Endpoint**: `POST /api/v1/posts`
- **Access**: Authenticated
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Scaling Distributed Caches",
    "summary": "Practical techniques for multi-region caching.",
    "content": "# Caching Strategies\n\nCache invalidation is hard...",
    "tags": "caching,redis,systems",
    "is_published": true
  }
  ```
- **Response** (`201 Created`): Returns the created post object.

---

### Update Own Post
- **Endpoint**: `PUT /api/v1/posts/{id}`
- **Access**: Authenticated (Author only; returns `403 Forbidden` if another user attempts edit)
- **Request Body**:
  ```json
  {
    "title": "Updated Title",
    "content": "Updated markdown content...",
    "is_published": true
  }
  ```
- **Response** (`200 OK`): Returns updated post object.

---

### Delete Own Post
- **Endpoint**: `DELETE /api/v1/posts/{id}`
- **Access**: Authenticated (Author only; returns `403 Forbidden` if another user attempts deletion)
- **Response** (`200 OK`):
  ```json
  {
    "message": "Blog post deleted successfully.",
    "id": 1
  }
  ```

---

## 3. Social Endpoints (Likes & Comments)

### Toggle Like
- **Endpoint**: `POST /api/v1/posts/{id}/like`
- **Access**: Authenticated
- **Behavior**: If the user has not liked the post, adds a like. If already liked, removes the like.
- **Response** (`200 OK`):
  ```json
  {
    "liked": true,
    "likes_count": 13,
    "message": "Post liked."
  }
  ```

---

### Add Comment
- **Endpoint**: `POST /api/v1/posts/{id}/comments`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "content": "Excellent breakdown of the WAL mode benefits!"
  }
  ```
- **Response** (`201 Created`): Returns comment object with author details.

---

### Delete Comment
- **Endpoint**: `DELETE /api/v1/comments/{id}`
- **Access**: Authenticated (Allowed for the comment author OR the post author)
- **Response** (`200 OK`):
  ```json
  {
    "message": "Comment deleted successfully.",
    "id": 5
  }
  ```
