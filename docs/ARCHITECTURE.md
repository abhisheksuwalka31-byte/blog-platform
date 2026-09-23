# System Architecture & Technical Design

This document details the architecture, design principles, security model, and data contracts of the **BlogVerse Platform**.

---

## 1. High-Level Architecture

The platform follows a layered, modular architecture built on **FastAPI**, **SQLAlchemy 2.0 ORM**, and **SQLite (Write-Ahead Logging mode)**, pairing a decoupled **REST API Layer** with a Server-Side Rendered **Web UI Layer**.

```mermaid
graph TD
    subgraph ClientLayer ["Client Layer"]
        Browser["Desktop & Mobile Web Browsers"]
        APIClient["API Clients / Curl / Postman"]
    end

    subgraph AppLayer ["FastAPI Application (app/)"]
        AuthMiddleware["JWT & Session Auth Dependency"]
        WebRouter["SSR Web Router (Jinja2 + Tailwind)"]
        APIRouter["API v1 Routers (Auth, Posts, Comments, Likes)"]
        MarkdownEngine["Markdown Rendering Engine"]
    end

    subgraph DomainLayer ["Domain Layer"]
        Models["SQLAlchemy ORM Entities"]
        Schemas["Pydantic v2 Schemas (Serialization & Validation)"]
    end

    subgraph DataLayer ["Persistence Layer"]
        SQLite[("SQLite Engine (WAL Mode / blog.db)")]
    end

    Browser -->|HTTP Cookies / HTML| WebRouter
    Browser -->|Async Fetch API| APIRouter
    APIClient -->|Bearer JWT Header| APIRouter
    
    WebRouter --> AuthMiddleware
    APIRouter --> AuthMiddleware

    WebRouter --> MarkdownEngine
    WebRouter --> Models
    APIRouter --> Schemas
    Schemas --> Models
    Models --> SQLite
```

---

## 2. Entity-Relationship (ER) Model

The relational schema ensures referential integrity, cascading deletions for parent entities, and uniqueness constraints.

```mermaid
erDiagram
    USERS ||--o{ POSTS : "authors"
    USERS ||--o{ COMMENTS : "writes"
    USERS ||--o{ LIKES : "gives"
    POSTS ||--o{ COMMENTS : "contains"
    POSTS ||--o{ LIKES : "receives"

    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
        string full_name
        string bio
        string avatar_url
        datetime created_at
    }

    POSTS {
        int id PK
        string title
        string slug UK
        text summary
        text content
        string tags
        boolean is_published
        int author_id FK
        datetime created_at
        datetime updated_at
    }

    COMMENTS {
        int id PK
        text content
        int post_id FK
        int author_id FK
        datetime created_at
    }

    LIKES {
        int id PK
        int post_id FK
        int user_id FK
        datetime created_at
    }
```

### Constraints & Indexes
- **`USERS.username` & `USERS.email`**: Indexed and unique.
- **`POSTS.slug`**: Indexed and unique for SEO-friendly canonical URLs.
- **`POSTS.is_published`**: Indexed for fast filtering of public articles.
- **`LIKES (post_id, user_id)`**: `UniqueConstraint("post_id", "user_id")` prevents duplicate likes from the same user.
- **Cascades**: When a `Post` is deleted, all child `Comments` and `Likes` are deleted automatically (`cascade="all, delete-orphan"`).

---

## 3. Authentication & Security Model

The system employs a dual-authentication strategy to balance developer ergonomics and browser security:

1. **HttpOnly Cookie Session**:
   - On successful login or registration, the backend sets an `access_token` cookie with `HttpOnly=True` and `SameSite=Lax`.
   - **Protection**: Mitigates Cross-Site Scripting (XSS) attacks by preventing malicious JavaScript from reading the session token directly.
2. **Bearer Authorization Header**:
   - Standard `Authorization: Bearer <jwt_token>` is returned in JSON payloads for API clients, automated test suites, and OpenAPI Swagger UI (`/docs`).
3. **Password Security**:
   - Passwords are encrypted using the industry-standard **bcrypt** adaptive hashing algorithm with an automatically generated salt per user. Plaintext passwords are never logged or stored.
4. **User-Specific Ownership Isolation**:
   - Access to modify or delete a blog post is guarded by verifying that `post.author_id == current_user.id`.
   - A non-author attempting a `PUT` or `DELETE` request is rejected with `HTTP 403 Forbidden`.
   - Draft posts (`is_published=False`) are inaccessible to public visitors or other logged-in users; only the original author can access draft URLs.

---

## 4. Component Structure

```
blog-platform/
├── app/
│   ├── api/                 # REST API layer
│   │   ├── deps.py          # FastAPI dependencies (Auth, DB session)
│   │   └── v1/              # Versioned API endpoints
│   │       ├── auth.py      # Registration, login, token, me
│   │       ├── posts.py     # Posts CRUD & public list
│   │       ├── comments.py  # Comment creation & deletion
│   │       └── likes.py     # Like toggle & status
│   ├── core/                # Configuration and foundational services
│   │   ├── config.py        # Settings via Pydantic BaseSettings
│   │   ├── database.py      # SQLAlchemy engine, SessionLocal, Base
│   │   └── security.py      # Bcrypt hashing & JWT signing/decoding
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   └── like.py
│   ├── routers/             # Web UI Server-Rendered router
│   │   └── web.py
│   ├── schemas/             # Pydantic validation & response models
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   └── like.py
│   └── templates/           # Jinja2 HTML templates styled with Tailwind
│       ├── base.html
│       ├── index.html
│       ├── post_detail.html
│       ├── dashboard.html
│       ├── editor.html
│       ├── login.html
│       └── register.html
├── docs/                    # Technical & delivery documentation
│   ├── ARCHITECTURE.md
│   ├── API_SPECIFICATION.md
│   └── DEMO_SCRIPT.md
├── tests/                   # Automated pytest suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_social.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
├── seed.py
└── README.md
```

---

## 5. Scalability & Deployment Pathways

While configured out of the box with zero-configuration SQLite for instant local execution, the architecture is production-ready for horizontal scaling:

- **Database Swap**: Setting `DATABASE_URL=postgresql://user:pass@host:5432/db` in `.env` immediately switches the database to PostgreSQL with zero code changes thanks to SQLAlchemy abstraction.
- **Stateless Authentication**: JWT tokens are cryptographically signed and stateless, allowing multiple backend application containers behind a load balancer (e.g., NGINX, AWS ALB) without sticky sessions.
- **Static & CDN Assets**: Tailwind and FontAwesome are delivered via high-availability CDNs, while static assets can be offloaded to Cloudflare or S3/CloudFront.
