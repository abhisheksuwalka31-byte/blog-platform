import sys
from datetime import datetime, timezone
from app.core.database import SessionLocal, init_db, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.post import Post, slugify
from app.models.comment import Comment
from app.models.like import Like


def seed_database():
    print("🌱 Initializing database schema...")
    init_db()

    db = SessionLocal()

    # Clear existing data to ensure clean idempotency
    print("🧹 Cleaning existing records...")
    db.query(Like).delete()
    db.query(Comment).delete()
    db.query(Post).delete()
    db.query(User).delete()
    db.commit()

    print("👤 Creating demo users...")
    alice = User(
        username="alice",
        email="alice@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Alice Chen",
        bio="Staff Software Engineer specializing in distributed architectures, async Python, and database internals.",
        avatar_url="https://api.dicebear.com/7.x/initials/svg?seed=Alice+Chen"
    )
    bob = User(
        username="bob",
        email="bob@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Bob Martinez",
        bio="Full-Stack Developer, open source advocate, and UI/UX design enthusiast.",
        avatar_url="https://api.dicebear.com/7.x/initials/svg?seed=Bob+Martinez"
    )
    charlie = User(
        username="charlie",
        email="charlie@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Charlie Vance",
        bio="Security researcher & author exploring zero-trust systems, authentication, and cloud infrastructure.",
        avatar_url="https://api.dicebear.com/7.x/initials/svg?seed=Charlie+Vance"
    )

    db.add_all([alice, bob, charlie])
    db.commit()
    db.refresh(alice)
    db.refresh(bob)
    db.refresh(charlie)

    print("📝 Creating demo blog posts...")

    post_1 = Post(
        title="Building High-Performance APIs with FastAPI and SQLAlchemy 2.0",
        slug="building-high-performance-apis-fastapi-sqlalchemy",
        summary="Learn how combining FastAPI with modern SQLAlchemy 2.0 delivers asynchronous throughput, automatic Swagger OpenAPI docs, and strict type safety.",
        content="""## Introduction

Building reliable, high-performance web APIs has never been more straightforward in Python. With **FastAPI** and **SQLAlchemy 2.0**, developers can enjoy type safety with Pydantic v2 and modern asynchronous ORM query syntax.

### Why Choose FastAPI?

Here are three primary reasons FastAPI has become an industry standard:

1. **Automatic OpenAPI/Swagger Documentation**: Interactive API testing at `/docs` without third-party plugins.
2. **Strict Request Validation**: Powered by Pydantic models with type hints.
3. **Async Native Performance**: First-class async/await support matching Node.js and Go in many real-world benchmarks.

### Example: Dependency Injection

Here is how cleanly you can manage database sessions with dependency injection:

```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### Wrapping Up

By structuring your project into modular domain layers (schemas, models, core, routers), you create codebases that scale cleanly as engineering teams expand.
""",
        tags="python,fastapi,backend,architecture",
        is_published=True,
        author_id=alice.id
    )

    post_2 = Post(
        title="Modern Web Authentication: Cookies vs Bearer JWTs Explained",
        slug="modern-web-authentication-cookies-vs-bearer-jwts",
        summary="An in-depth security comparison between HTTP-only secure cookies and Bearer tokens for mobile, SPAs, and server-rendered web applications.",
        content="""## Understanding Authentication in 2026

When designing modern web authentication, engineers frequently debate between **HTTP-only Cookies** and **Authorization Bearer Tokens (JWTs)**.

### The Problem with LocalStorage

Storing JSON Web Tokens in browser `localStorage` leaves applications susceptible to **Cross-Site Scripting (XSS)**. Any third-party script injected via compromised npm dependencies can read `localStorage.getItem("token")` and exfiltrate user credentials.

### The Hybrid Solution

In production architectures, a **hybrid pattern** offers the best of both worlds:

- **Browser Web Clients**: Set an `HttpOnly`, `SameSite=Lax`, `Secure` cookie. JavaScript running in the browser cannot read the raw token, defending against XSS token harvesting.
- **External API Clients & Mobile**: Accept `Authorization: Bearer <token>` headers for automated curl scripts and native apps.

```python
def get_token_from_request(request: Request) -> Optional[str]:
    # Check Bearer header first, then fallback to HttpOnly cookie
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:]
    return request.cookies.get("access_token")
```

This dual-support ensures developer convenience without sacrificing client defense!
""",
        tags="security,auth,jwt,web",
        is_published=True,
        author_id=charlie.id
    )

    post_3 = Post(
        title="Why Markdown Remains the Gold Standard for Technical Writing",
        slug="why-markdown-remains-the-gold-standard-for-technical-writing",
        summary="A look at how Markdown keeps developer documentation portable, git-trackable, and distraction-free.",
        content="""## Simplicity Over Rich WYSIWYG Bloat

For technical content, few innovations have had as lasting an impact as John Gruber's **Markdown**.

### Key Advantages

- **Portable**: Markdown is plain text. It renders identically on GitHub, static site generators, and custom web apps.
- **Code-First**: Code blocks with language syntax highlighting (`python`, `javascript`, `sql`) are first-class citizens.
- **Diff-Friendly**: Content changes produce clean, readable Git diffs during pull requests.

> "Simplicity is prerequisite for reliability." — Edsger W. Dijkstra

Give it a try in the BlogVerse editor and see how seamless composing technical articles can be!
""",
        tags="markdown,writing,productivity",
        is_published=True,
        author_id=bob.id
    )

    post_draft = Post(
        title="Draft: Exploring Distributed SQLite with LiteFS and WAL Mode",
        slug="draft-exploring-distributed-sqlite-litefs",
        summary="Unfinished notes on scaling SQLite across edge nodes using Write-Ahead Logging replication.",
        content="""## Work in Progress

This is a private draft only visible to the author (Alice).

Key ideas to explore:
- SQLite Write-Ahead Logging (WAL) concurrency characteristics.
- Zero-latency reads on edge servers.
- Automatic failover for primary write nodes.
""",
        tags="sqlite,databases,draft",
        is_published=False,  # DRAFT!
        author_id=alice.id
    )

    db.add_all([post_1, post_2, post_3, post_draft])
    db.commit()
    db.refresh(post_1)
    db.refresh(post_2)
    db.refresh(post_3)
    db.refresh(post_draft)

    print("💬 Adding comments and discussions...")
    comment_1 = Comment(
        content="Fantastic breakdown, Alice! The code snippet makes dependency injection super clear. Are you planning a follow-up on background task workers with Celery or RQ?",
        post_id=post_1.id,
        author_id=bob.id
    )
    comment_2 = Comment(
        content="Great writeup! We recently migrated our API from Django REST Framework to FastAPI and cut our p99 response latencies in half.",
        post_id=post_1.id,
        author_id=charlie.id
    )
    comment_3 = Comment(
        content="Thanks @bob and @charlie! Yes, a post on background tasks and Redis queues is coming next week.",
        post_id=post_1.id,
        author_id=alice.id
    )
    comment_4 = Comment(
        content="Strongly agree on HttpOnly cookies. Too many tutorials recommend storing JWTs directly in localStorage without explaining the XSS vectors.",
        post_id=post_2.id,
        author_id=alice.id
    )

    db.add_all([comment_1, comment_2, comment_3, comment_4])
    db.commit()

    print("❤️ Adding sample likes...")
    like_1 = Like(post_id=post_1.id, user_id=bob.id)
    like_2 = Like(post_id=post_1.id, user_id=charlie.id)
    like_3 = Like(post_id=post_2.id, user_id=alice.id)
    like_4 = Like(post_id=post_3.id, user_id=alice.id)
    like_5 = Like(post_id=post_3.id, user_id=charlie.id)

    db.add_all([like_1, like_2, like_3, like_4, like_5])
    db.commit()

    db.close()
    print("✅ Seed completed successfully!")
    print("\n--- Pre-configured Test Accounts ---")
    print("1. Alice (Author):    alice@example.com    / password123")
    print("2. Bob (Reader/Dev):  bob@example.com      / password123")
    print("3. Charlie (Security):charlie@example.com  / password123")
    print("------------------------------------\n")


if __name__ == "__main__":
    seed_database()
