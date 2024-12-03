from datetime import datetime
from typing import Optional

from beanie import Document


class Review(Document):
    author_id: str
    movie_id: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Settings:
        collection = "reviews"


class ReviewLike(Document):
    user_id: str
    review_id: str
    is_liked: Optional[bool] = None
    is_disliked: Optional[bool] = None

    def validate(self):
        if self.is_liked and self.is_disliked:
            raise ValueError("A review cannot be both liked and disliked at the same time.")
        if not self.is_liked and not self.is_disliked:
            raise ValueError("Either 'is_liked' or 'is_disliked' must be set.")

    class Settings:
        collection = "review_likes"
