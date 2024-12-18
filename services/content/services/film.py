from functools import lru_cache
from typing import List, Optional

import orjson
from db.elastic import get_search_service
from db.redis import get_cache
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.film import FilmModel, FilmRating
from utils.abstract import AsyncCacheStorage, AsyncSearchService
from utils.enums import Sort

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, cache: AsyncCacheStorage, search_service: AsyncSearchService):
        self.cache = cache
        self.search_service = search_service

    async def get_by_id(self, film_id: str) -> FilmModel | None:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_search_service(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_search_service(self, film_id: str) -> FilmModel | None:
        doc = await self.search_service.get(index='movies', id=film_id)
        if doc is None:
            return None
        return FilmModel(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> FilmModel | None:
        data = await self.cache.get(film_id)
        if not data:
            return None
        film = FilmModel.model_validate_json(data)
        return film

    async def _put_film_to_cache(self, film: FilmModel):
        await self.cache.set(film.uuid, film.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_by_query(self, query: str, page: int, size: int) -> FilmRating | None:
        word = query.lower()
        cache_key = f'film:query:{word}'
        films = await self._films_from_cache(cache_key)
        if not films:
            films = await self._get_films_by_query(query, page, size)
            if not films:
                return None
            await self._put_films_to_cache(films, cache_key)
        return films

    async def _get_films_by_query(self, query: str, page: int, size: int) -> FilmRating | None:
        page -= 1
        body = {"from": page, "size": size, "query": {"match": {"title": {"query": query}}}}
        doc = await self.search_service.search(
            index='movies',
            body=body,
            _source_includes=['uuid', 'title', 'imdb_rating']
        )
        return [FilmRating(**i['_source']) for i in doc['hits']['hits']]

    async def get_films(
            self, genre: str, sort_field: str, sort_order: Sort, page: int, size: int
    ) -> List[FilmRating]:
        cache_key = 'film:rating:all'
        if genre:
            cache_key = f'film:rating:genre:{genre}'
        films: Optional[List[FilmRating]] = await self._films_from_cache(cache_key)
        if not films:
            films = await self._get_films_from_search_service(
                genre, sort_field,
                sort_order,
                page,
                size
            )
            if not films:
                films = []
            await self._put_films_to_cache(films, cache_key)
        return films

    async def _get_films_from_search_service(
            self, genre: str, sort_field: str, sort_order: Sort, page: int, size: int
    ) -> list[FilmRating] | None:
        sort = sort_order.value
        page -= 1
        body = {"from": page, "size": size, "sort": {sort_field: {"order": sort}}}
        if genre:
            body["query"] = {
                "nested": {
                    "path": "genres", "query": {
                        "bool": {"must": [{"match": {"genres.uuid": genre}}]}
                    },
                }
            }
        response = await self.search_service.search(
            index='movies',
            body=body,
            _source_includes=['uuid', 'title', 'imdb_rating']
        )
        films = [FilmRating(**doc['_source']) for doc in response['hits']['hits']]
        return films if films else []

    async def _films_from_cache(self, cache_key: str) -> list[FilmRating] | None:
        films = await self.cache.get(cache_key)
        if not films:
            return None
        return [FilmRating(uuid=film['uuid'],
                           title=film['title'],
                           imdb_rating=film['imdb_rating']) for film in orjson.loads(films)]

    async def _put_films_to_cache(self, films: list[FilmRating], cache_key: str):
        await self.cache.set(
            cache_key,
            orjson.dumps(jsonable_encoder(films)),
            FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        cache: AsyncCacheStorage = Depends(get_cache),
        search_service: AsyncSearchService = Depends(get_search_service),
) -> FilmService:
    return FilmService(cache, search_service)
