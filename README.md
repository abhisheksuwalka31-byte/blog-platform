# 🛠️ BlogVerse Platform

> **A production-ready, user-specific blog platform featuring secure authentication, Markdown authoring, ownership isolation, and interactive social features (likes & comments).**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v3-38bdf8.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

---

## ✨ Features

- 🌐 **Public Browsing (No Login Required)**:
  - Anyone can explore published articles, search by title/keywords, filter by tags, and read full posts with comments and like counts.
- 🔐 **Secure Authentication & Ownership**:
  - Registration and login with **bcrypt** password hashing.
  - Hybrid **HttpOnly Cookies** (for browser security against XSS) and **Bearer JWT** (for REST API & Swagger UI).
  - Strict **User Ownership Isolation**: Authors can only edit and delete their own posts; non-owners receive `HTTP 403 Forbidden`.
- ✍️ **Author Studio & Markdown Publishing**:
  - Full Markdown editor with instant live preview.
  - Draft vs Published status control.
  - Auto-generated unique SEO slugs and estimated reading time calculation.
  - Author Dashboard displaying post metrics (total posts, drafts, published, and total likes received).
- ❤️ **Social Interactions (Likes & Comments)**:
  - Logged-in users can like/unlike posts dynamically with instant count updates without page refresh.
  - Community members can leave comments on published articles.
  - Comment deletion restricted to comment author or post owner.
  - Unauthenticated guests attempting to interact are prompted with friendly sign-in modals.
- 📖 **Interactive API Documentation**:
  - Auto-generated interactive Swagger UI at `/docs` and ReDoc at `/redoc`.
- 🧪 **Full Test Coverage**:
  - Automated `pytest` suite testing authentication, permissions, post isolation, and social interactions with an isolated in-memory database.

---

## 🏗️ System Architecture

```
                          +------------------------------------------+
                          |   Browser / REST Client / Mobile App     |
                          +--------------------+---------------------+
                                               |
                                               v
                          +------------------------------------------+
                          |        FastAPI Core Application          |
                          |   (CORS, Error Handlers, Static Files)   |
                          +--------------------+---------------------+
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     v                                                   v
      +------------------------------+                    +------------------------------+
      |      Web UI Router (SSR)     |                    |      REST API v1 Router      |
      |   - Jinja2 HTML Templates    |                    |   - /auth (register, login)  |
      |   - Tailwind CSS & Marked    |                    |   - /posts (CRUD & search)   |
      |   - Cookie Session Auth      |                    |   - /comments & /likes       |
      +--------------+---------------+                    +--------------+---------------+
                     |                                                   |
                     +-------------------------+-------------------------+
                                               |
                                               v
                          +------------------------------------------+
                          |    Data Access Layer (SQLAlchemy 2.0)    |
                          |      Users, Posts, Comments, Likes       |
                          +--------------------+---------------------+
                                               |
                                               v
                          +------------------------------------------+
                          |        SQLite Database (blog.db)         |
                          |         (WAL Mode Concurrency)           |
                          +------------------------------------------+
```

For complete technical design, ER diagrams, and security architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).  
For the complete API contract reference, see [docs/API_SPECIFICATION.md](docs/API_SPECIFICATION.md).

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+ (tested with Python 3.11, 3.12, 3.13, and 3.14)
- Git

### 1. Clone & Setup Workspace
```bash
git clone <your-repo-url> blog-platform
cd blog-platform
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
*(The default configuration in `.env.example` works out of the box with zero external setup).*

### 5. Seed Demo Data (Optional but Recommended)
Populate the database with realistic sample users, articles, comments, and likes:
```bash
python seed.py
```

### 6. Launch the Application
```bash
python run.py
```
Open your browser and visit:
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 👥 Demo User Accounts

If you ran `python seed.py`, the following pre-configured accounts are ready to use (also available via 1-click fill buttons on `/login`):

| User | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Alice** | `alice@example.com` | `password123` | Staff Engineer / Author |
| **Bob** | `bob@example.com` | `password123` | Frontend Dev / Community Member |
| **Charlie** | `charlie@example.com` | `password123` | Security Researcher / Writer |

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:
```bash
pytest -v
```

The test suite validates:
- Public unauthenticated browsing and draft privacy
- User registration, duplicate checks, and JWT issuance
- Author post creation, editing, and deletion
- Ownership boundary enforcement (User B cannot edit User A's post)
- Social like toggling and comment lifecycle security

---

## 📁 Repository Structure

```
blog-platform/
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependency injection (Auth, DB)
│   │   └── v1/
│   │       ├── auth.py           # Register, login, me endpoints
│   │       ├── posts.py          # Post CRUD & filtering endpoints
│   │       ├── comments.py       # Commenting endpoints
│   │       └── likes.py          # Liking endpoints
│   ├── core/
│   │   ├── config.py             # Settings (Pydantic BaseSettings)
│   │   ├── database.py           # Database connection & session
│   │   └── security.py           # Bcrypt & JWT logic
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   └── like.py
│   ├── routers/
│   │   └── web.py                # Server-rendered web routes
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   └── like.py
│   ├── templates/                # Responsive Tailwind HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── post_detail.html
│   │   ├── dashboard.html
│   │   ├── editor.html
│   │   ├── login.html
│   │   └── register.html
│   └── main.py                   # FastAPI app factory
├── docs/
│   ├── ARCHITECTURE.md           # System design & ER diagram
│   ├── API_SPECIFICATION.md      # REST API contracts
│   └── DEMO_SCRIPT.md            # 2-minute video presentation script
├── tests/
│   ├── conftest.py               # Test DB fixtures
│   ├── test_auth.py              # Auth unit tests
│   ├── test_posts.py             # Post permissions tests
│   └── test_social.py            # Like & comment tests
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore file
├── requirements.txt              # Project dependencies
├── run.py                        # Server runner
├── seed.py                       # Sample data populator
└── README.md                     # Documentation
```

---

## 🎥 2-Minute Video Walkthrough Guide

A complete script for recording a 2-minute walkthrough video demonstrating local execution, public reading, author publishing, and social interactions is located at:
👉 **[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)**

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
