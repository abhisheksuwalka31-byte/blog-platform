from typing import List, Optional
import uuid
import markdown
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post, slugify
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostDetailResponse
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter()


def render_markdown(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "nl2br",
            "sane_lists"
        ]
    )


def build_post_response(post: Post, db: Session, current_user: Optional[User] = None) -> dict:
    likes_count = db.query(Like).filter(Like.post_id == post.id).count()
    comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    
    is_liked = False
    if current_user:
        is_liked = db.query(Like).filter(
            Like.post_id == post.id,
            Like.user_id == current_user.id
        ).first() is not None

    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "tags": post.tags or "",
        "is_published": post.is_published,
        "author_id": post.author_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "reading_time_minutes": post.reading_time_minutes,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "author": post.author,
        "is_liked_by_viewer": is_liked
    }


@router.get("", response_model=List[PostResponse])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search keyword in title, summary, or content"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    author: Optional[str] = Query(None, description="Filter by author username"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Public endpoint: Anyone can browse and list published blog posts.
    """
    query = db.query(Post).filter(Post.is_published == True)

    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_pattern),
                Post.summary.ilike(search_pattern),
                Post.content.ilike(search_pattern)
            )
        )

    if tag:
        query = query.filter(Post.tags.ilike(f"%{tag}%"))

    if author:
        author_user = db.query(User).filter(User.username == author).first()
        if author_user:
            query = query.filter(Post.author_id == author_user.id)
        else:
            return []

    posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return [build_post_response(p, db, current_user) for p in posts]


@router.get("/user/me", response_model=List[PostResponse])
def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated author endpoint: View own posts (both published and drafts).
    """
    posts = db.query(Post).filter(
        Post.author_id == current_user.id
    ).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()

    return [build_post_response(p, db, current_user) for p in posts]


@router.get("/{id_or_slug}", response_model=PostDetailResponse)
def get_post_detail(
    id_or_slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Public endpoint: Anyone can read a published blog post with its comments and likes.
    Drafts can only be read by their author.
    """
    if id_or_slug.isdigit():
        post = db.query(Post).filter(Post.id == int(id_or_slug)).first()
    else:
        post = db.query(Post).filter(Post.slug == id_or_slug).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    if not post.is_published:
        # Only the author can view drafts
        if not current_user or current_user.id != post.author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This post is a draft and can only be viewed by its author."
            )

    post_data = build_post_response(post, db, current_user)
    post_data["content_html"] = render_markdown(post.content)
    post_data["comments"] = post.comments

    return post_data


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated author endpoint: Create a new blog post.
    """
    base_slug = slugify(post_in.title)
    if not base_slug:
        base_slug = "post"

    # Ensure unique slug
    unique_slug = base_slug
    counter = 1
    while db.query(Post).filter(Post.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1

    post = Post(
        title=post_in.title,
        slug=unique_slug,
        summary=post_in.summary or (post_in.content[:150] + "..." if len(post_in.content) > 150 else post_in.content),
        content=post_in.content,
        tags=post_in.tags or "",
        is_published=post_in.is_published,
        author_id=current_user.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return build_post_response(post, db, current_user)


@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated author endpoint: Update own blog post.
    Enforces user-specific ownership isolation.
    """
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    # Ownership check
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this post. Only the author can modify it."
        )

    if post_in.title is not None:
        post.title = post_in.title
        # Re-generate slug if title changed
        base_slug = slugify(post_in.title)
        unique_slug = base_slug
        counter = 1
        while True:
            existing = db.query(Post).filter(Post.slug == unique_slug, Post.id != post.id).first()
            if not existing:
                break
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        post.slug = unique_slug

    if post_in.summary is not None:
        post.summary = post_in.summary
    if post_in.content is not None:
        post.content = post_in.content
    if post_in.tags is not None:
        post.tags = post_in.tags
    if post_in.is_published is not None:
        post.is_published = post_in.is_published

    db.commit()
    db.refresh(post)

    return build_post_response(post, db, current_user)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated author endpoint: Delete own blog post.
    Enforces user-specific ownership isolation.
    """
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    # Ownership check
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post. Only the author can delete it."
        )

    db.delete(post)
    db.commit()

    return {"message": "Blog post deleted successfully.", "id": id}
