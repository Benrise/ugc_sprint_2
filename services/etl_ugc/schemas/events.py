from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel


class MovieProgressEvent(BaseModel):
    user_id: str
    movie_id: str
    progress: float
    status: Literal["in_progress", "completed"]
    last_watched: datetime

    def as_tuple(self):
        return (
            self.user_id,
            self.movie_id,
            self.progress,
            self.status,
            self.last_watched,
        )


class MovieFiltersEvent(BaseModel):
    user_id: str
    query: str
    page: int
    size: int
    date_event: datetime

    def as_tuple(self):
        return (
            self.user_id,
            self.query,
            self.page,
            self.size,
            self.date_event,
        )


class MovieDetailsEvent(BaseModel):
    user_id: str
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genres: List[dict]
    actors: List[dict]
    writers: List[dict]
    directors: List[dict]
    date_event: datetime

    def as_tuple(self):
        genres = [(genre['uuid'], genre['name']) for genre in self.genres]
        actors = [(actor['uuid'], actor['full_name']) for actor in self.actors]
        writers = [(writer['uuid'], writer['full_name']) for writer in self.writers]
        directors = [(director['uuid'], director['full_name']) for director in self.directors]

        return (
            self.user_id,
            self.uuid,
            self.title,
            self.imdb_rating,
            self.description,
            genres,
            actors,
            writers,
            directors,
            self.date_event,
        )
