import os
from typing import Optional
import markdown
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from app.api.deps import get_current_user_optional

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def render_markdown(text: str) -> str:
    return markdown.markdown(
        text or "",
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "nl2br",
            "sane_lists"
        ]
    )


def get_popular_tags(db: Session, limit: int = 8) -> list:
    posts = db.query(Post).filter(Post.is_published == True).all()
    tag_counts = {}
    for p in posts:
        if p.tags:
            for t in p.tags.split(","):
                t = t.strip()
                if t:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [t[0] for t in sorted_tags[:limit]]


@router.get("/", response_class=HTMLResponse)
def index_page(
    request: Request,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Public homepage: Anyone can browse and read published blog posts.
    """
    query = db.query(Post).filter(Post.is_published == True)

    if q:
        search_pat = f"%{q}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_pat),
                Post.summary.ilike(search_pat),
                Post.content.ilike(search_pat)
            )
        )

    if tag:
        query = query.filter(Post.tags.ilike(f"%{tag}%"))

    posts = query.order_by(desc(Post.created_at)).all()

    # Enrich post data for template
    enriched_posts = []
    for post in posts:
        is_liked = False
        if current_user:
            is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first() is not None
        
        enriched_posts.append({
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "content": post.content,
            "tags": post.tags,
            "author": post.author,
            "created_at": post.created_at,
            "reading_time_minutes": post.reading_time_minutes,
            "likes_count": len(post.likes),
            "comments_count": len(post.comments),
            "is_liked_by_viewer": is_liked
        })

    popular_tags = get_popular_tags(db)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": current_user,
            "posts": enriched_posts,
            "search_query": q,
            "active_tag": tag,
            "popular_tags": popular_tags
        }
    )


@router.get("/posts/new", response_class=HTMLResponse)
def new_post_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Protected post creator page. Redirects to login if unauthenticated.
    """
    if not current_user:
        return RedirectResponse(url="/login?redirect=/posts/new", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="editor.html",
        context={
            "current_user": current_user,
            "is_edit": False,
            "post": None
        }
    )


@router.get("/posts/{id_or_slug}", response_class=HTMLResponse)
def post_detail_page(
    request: Request,
    id_or_slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Public article page: Anyone can read published posts and comments.
    """
    if id_or_slug.isdigit():
        post = db.query(Post).filter(Post.id == int(id_or_slug)).first()
    else:
        post = db.query(Post).filter(Post.slug == id_or_slug).first()

    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found.")

    if not post.is_published and (not current_user or current_user.id != post.author_id):
        raise HTTPException(status_code=403, detail="This draft is private to its author.")

    is_liked = False
    if current_user:
        is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first() is not None

    post_dict = {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content_html": render_markdown(post.content),
        "tags": post.tags,
        "is_published": post.is_published,
        "author_id": post.author_id,
        "author": post.author,
        "created_at": post.created_at,
        "reading_time_minutes": post.reading_time_minutes,
        "likes_count": len(post.likes),
        "comments": post.comments,
        "is_liked_by_viewer": is_liked
    }

    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={
            "current_user": current_user,
            "post": post_dict
        }
    )


@router.get("/posts/{id}/edit", response_class=HTMLResponse)
def edit_post_page(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Protected post editor page. Enforces user-specific ownership.
    """
    if not current_user:
        return RedirectResponse(url=f"/login?redirect=/posts/{id}/edit", status_code=status.HTTP_303_SEE_OTHER)

    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to edit another author's post.")

    return templates.TemplateResponse(
        request=request,
        name="editor.html",
        context={
            "current_user": current_user,
            "is_edit": True,
            "post": post
        }
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Protected author dashboard: View own posts, metrics, and manage articles.
    """
    if not current_user:
        return RedirectResponse(url="/login?redirect=/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    user_posts = db.query(Post).filter(Post.author_id == current_user.id).order_by(desc(Post.created_at)).all()

    total_likes = 0
    published_count = 0
    draft_count = 0
    posts_data = []

    for p in user_posts:
        l_cnt = len(p.likes)
        c_cnt = len(p.comments)
        total_likes += l_cnt
        if p.is_published:
            published_count += 1
        else:
            draft_count += 1

        posts_data.append({
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "summary": p.summary,
            "content": p.content,
            "is_published": p.is_published,
            "created_at": p.created_at,
            "likes_count": l_cnt,
            "comments_count": c_cnt
        })

    stats = {
        "total_posts": len(user_posts),
        "published_posts": published_count,
        "draft_posts": draft_count,
        "total_likes": total_likes
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": current_user,
            "posts": posts_data,
            "stats": stats
        }
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    redirect: Optional[str] = "/dashboard",
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if current_user:
        return RedirectResponse(url=redirect or "/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "current_user": None,
            "redirect_url": redirect
        }
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    redirect: Optional[str] = "/dashboard",
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if current_user:
        return RedirectResponse(url=redirect or "/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "current_user": None,
            "redirect_url": redirect
        }
    )


@router.get("/logout")
def logout_page():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
