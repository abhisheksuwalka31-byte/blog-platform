# 2-Minute Video Demo Script & Presentation Guide

This guide provides a time-coded, step-by-step walkthrough for recording a concise 2-minute Loom or screen demonstration of the **BlogVerse Platform**.

---

## Quick Reference Summary
- **App URL**: `http://127.0.0.1:8000`
- **Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Demo Accounts**:
  - `alice@example.com` / `password123` (Author / Engineer)
  - `bob@example.com` / `password123` (Reader / Collaborator)

---

## 2-Minute Storyboard & Narration

| Timestamp | Visual / Screen Action | Voiceover Narration |
| :--- | :--- | :--- |
| **0:00 - 0:20**<br>*(20s)* | **Terminal**: Launch the app with `python run.py`.<br>Open browser to `http://127.0.0.1:8000`. | *"Hi everyone! Today I'm showcasing BlogVerse, a modular, production-grade blog platform with secure authentication, user-specific ownership, and social interactions. The app boots in seconds with a single command, running FastAPI, SQLAlchemy, and a modern responsive interface."* |
| **0:20 - 0:45**<br>*(25s)* | **Browser (Incognito / Logged Out)**:<br>1. Show home feed with cards, search bar, and tags.<br>2. Filter by tag `#fastapi` or search `architecture`.<br>3. Click on Alice's post to read the rendered Markdown.<br>4. Attempt to click **Like** or submit a comment. | *"Notice that as an unauthenticated guest, I can freely discover, search, and read any published article along with community comments. However, when I try to like or comment, the platform cleanly protects write access and prompts me to log in."* |
| **0:45 - 1:15**<br>*(30s)* | **Browser (Login as Alice)**:<br>1. Click **Sign In** and use the 1-click demo button for **Alice**.<br>2. Navigate to **Write Post** (`/posts/new`).<br>3. Enter title: *"Zero-Downtime SQLite Migrations"*.<br>4. Type some Markdown and switch to the **Preview** tab.<br>5. Click **Publish Article** and show redirect to live post. | *"Let's sign in as Alice. Now authenticated, Alice can create rich articles. The editor features a live Markdown preview tab for headings, code snippets, and lists. Once published, the article is immediately live with its unique SEO slug and calculated read time."* |
| **1:15 - 1:40**<br>*(25s)* | **Browser & Switch User to Bob**:<br>1. Open Alice's post as Bob.<br>2. Click **Like** (watch count increment instantly from 2 to 3 without page refresh).<br>3. Post comment: *"Super helpful article, Alice!"*<br>4. Show that Bob CANNOT edit or delete Alice's article.<br>5. Go to Alice's dashboard (`/dashboard`) to show draft management & post analytics. | *"Now logging in as Bob, Bob can instantly like Alice's post and leave a comment. Ownership security is strictly enforced: Bob has no permissions to edit or delete Alice's content. Meanwhile, in Alice's dashboard, she can manage her drafts, see total likes received, and update her articles."* |
| **1:40 - 2:00**<br>*(20s)* | **Browser**: Navigate to `http://127.0.0.1:8000/docs`.<br>Highlight the OpenAPI interactive schema.<br>**Terminal**: Run `pytest -v` (all tests passing). | *"Behind the scenes, BlogVerse automatically provides interactive Swagger API documentation at `/docs` covering all authentication, post CRUD, and social contracts. Plus, the repository is verified with automated tests covering isolation and permissions. Thank you!"* |

---

## Pre-Recording Checklist
1. Ensure virtual environment is active: `source venv/bin/activate`
2. Seed fresh demo data: `python seed.py`
3. Launch server: `python run.py`
4. Have two browser tabs or an incognito window ready for user switching.
