from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.like import Like
from app.schemas.like import LikeToggleResponse, LikeStatusResponse
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter()


@router.get("/posts/{post_id}/like", response_model=LikeStatusResponse)
def get_like_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get current like status for a post.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    is_liked = False
    if current_user:
        is_liked = db.query(Like).filter(
            Like.post_id == post_id,
            Like.user_id == current_user.id
        ).first() is not None

    return {"liked": is_liked, "likes_count": likes_count}


@router.post("/posts/{post_id}/like", response_model=LikeToggleResponse)
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated endpoint: Toggle like on a blog post.
    If already liked, removes the like. If not yet liked, adds the like.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        likes_count = db.query(Like).filter(Like.post_id == post_id).count()
        return {
            "liked": False,
            "likes_count": likes_count,
            "message": "Post unliked."
        }
    else:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        likes_count = db.query(Like).filter(Like.post_id == post_id).count()
        return {
            "liked": True,
            "likes_count": likes_count,
            "message": "Post liked."
        }
