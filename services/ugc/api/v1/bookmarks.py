from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, Request
from schemas.bookmark import Bookmark
from services.user import UserService

router = APIRouter()


@router.get("/")
async def get_user_bookmarks(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.get_user_id_from_jwt(request)

    bookmarks = await Bookmark.find(Bookmark.user_id == user_id).to_list()
    return {"user_id": user_id, "bookmarks": bookmarks}


@router.post("/toggle")
async def toggle_bookmark(
    request: Request,
    movie_id: str,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.get_user_id_from_jwt(request)

    existing_bookmark = await Bookmark.find_one(Bookmark.user_id == user_id, Bookmark.movie_id == movie_id)

    if existing_bookmark:
        await existing_bookmark.delete()
        return {"message": "Bookmark removed successfully"}
    else:
        bookmark = Bookmark(user_id=user_id, movie_id=movie_id)
        await bookmark.create()
        return {"message": "Bookmark created successfully", "bookmark": bookmark}
