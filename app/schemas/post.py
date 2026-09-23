from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user import UserResponse
from app.schemas.comment import CommentResponse


class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=10)
    tags: Optional[str] = Field("", max_length=255)
    is_published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[str] = Field(None, max_length=255)
    is_published: Optional[bool] = None


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    tags: Optional[str] = ""
    is_published: bool
    author_id: int
    created_at: datetime
    updated_at: datetime
    reading_time_minutes: int
    likes_count: int = 0
    comments_count: int = 0
    author: UserResponse

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostResponse):
    content: str
    content_html: Optional[str] = None
    comments: List[CommentResponse] = []
    is_liked_by_viewer: bool = False
