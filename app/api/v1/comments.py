from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments_for_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Public endpoint: List all comments for a post.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(desc(Comment.created_at)).all()

    return comments


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated endpoint: Add a comment to a published blog post.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found."
        )

    if not post.is_published and post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot comment on an unpublished draft."
        )

    comment = Comment(
        content=comment_in.content,
        post_id=post_id,
        author_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated endpoint: Delete own comment, or delete comment on own post.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )

    # Permission check: comment author OR post author
    if comment.author_id != current_user.id and comment.post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this comment."
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully.", "id": comment_id}
