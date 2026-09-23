from fastapi import APIRouter
from app.api.v1 import auth, posts, comments, likes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(comments.router, prefix="", tags=["Comments"])
api_router.include_router(likes.router, prefix="", tags=["Likes"])
