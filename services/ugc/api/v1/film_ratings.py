from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.film import FilmRating
from services.user import UserService

router = APIRouter()


@router.post("/")
async def rate_film(
    request: Request,
    movie_id: str,
    stars: int,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.get_user_id_from_jwt(request)

    if not (0 <= stars <= 10):
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 10")
    film_rating = await FilmRating.find_one(FilmRating.user_id == user_id, FilmRating.movie_id == movie_id)
    if film_rating:
        film_rating.stars = stars
        await film_rating.save()
        return {"message": "Rating updated successfully", "film_rating": film_rating}
    else:
        new_rating = FilmRating(user_id=user_id, movie_id=movie_id, stars=stars)
        await new_rating.create()
        return {"message": "Rating created successfully", "film_rating": new_rating}


@router.get("/{movie_id}")
async def get_movie_ratings(
    request: Request,
    movie_id: str,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.get_user_id_from_jwt(request)

    stars = await FilmRating.find(FilmRating.movie_id == movie_id).to_list()
    average_rating = sum(r.stars for r in stars) / len(stars) if stars else 0
    return {"movie_id": movie_id, "average_rating": average_rating, "ratings_count": len(stars)}
