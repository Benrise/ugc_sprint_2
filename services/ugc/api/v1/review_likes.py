from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, Request
from schemas.review import ReviewLike
from services.user import UserService

router = APIRouter()


@router.post("/")
async def like_review(
    request: Request,
    review_id: str,
    is_liked: bool,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.get_user_id_from_jwt(request)

    existing_like = await ReviewLike.find_one(ReviewLike.user_id == user_id, ReviewLike.review_id == review_id)
    if existing_like:
        existing_like.is_liked = is_liked
        await existing_like.save()
        return {"message": "Review like updated successfully", "review_like": existing_like}
    else:
        new_like = ReviewLike(user_id=user_id, review_id=review_id, is_liked=is_liked)
        await new_like.create()
        return {"message": "Review like created successfully", "review_like": new_like}


@router.get("/{review_id}")
async def get_review_likes(
    request: Request, review_id: str,
    user_service: UserService = Depends(get_user_service)
):
    await user_service.get_user_id_from_jwt(request)

    likes = await ReviewLike.find(ReviewLike.review_id == review_id).to_list()
    total_likes = sum(1 for like in likes if like.is_liked)
    total_dislikes = sum(1 for like in likes if not like.is_liked)
    return {"review_id": review_id, "likes": total_likes, "dislikes": total_dislikes}
