from beanie import Document


class Bookmark(Document):
    user_id: str
    movie_id: str

    class Settings:
        collection = "bookmarks"
