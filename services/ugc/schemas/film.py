from beanie import Document


class FilmRating(Document):
    user_id: str
    movie_id: str
    stars: int

    class Settings:
        collection = "film_ratings"
