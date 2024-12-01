from enum import Enum


class EventType(str, Enum):
    MOVIE_PROGRESS = "movie_progress"
    MOVIE_DETAILS = "movie_details"
    MOVIE_FILTERS = "movie_filters"

    def __str__(self):
        return self.value
