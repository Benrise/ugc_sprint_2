from datetime import datetime

from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.review import Review
from services.user import UserService

router = APIRouter()


@router.post("/")
async def create_review(
    request: Request,
    movie_id: str,
    content: str,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.get_user_id_from_jwt(request)

    review = Review(
        author_id=user_id,
        movie_id=movie_id,
        text=content,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    await review.create()
    return {"message": "Review created successfully", "review": review}


@router.get("/{movie_id}")
async def get_movie_reviews(
    request: Request,
    movie_id: str,
    user_service: UserService = Depends(get_user_service),
):
    token = request.cookies.get("access_token_cookie")
    await user_service.get_user_id(token)

    reviews = await Review.find(Review.movie_id == movie_id).to_list()
    return {"movie_id": movie_id, "reviews": reviews}


@router.delete("/{review_id}")
async def delete_review(
    request: Request,
    review_id: str,
    user_service: UserService = Depends(get_user_service),
):
    token = request.cookies.get("access_token_cookie")
    await user_service.get_user_id(token)

    review = await Review.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await review.delete()
    return {"message": "Review deleted successfully"}
