from abc import ABC, abstractmethod

from fastapi.responses import RedirectResponse

from schemas.user import OAuthData


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass


class AsyncSearchService(ABC):
    @abstractmethod
    async def get(
                self,
                index: str,
                id: str,
                **kwargs
            ):
        pass

    @abstractmethod
    async def search(self, index: str, body: dict, **kwargs):
        pass


class OAuthProvider(ABC):
    def __init__(self, client, provider):
        self.client = client
        self.provider = provider

    @abstractmethod
    async def process_token(self, token) -> OAuthData:
        pass

    async def redirect(self, request) -> RedirectResponse:
        redirect_uri = request.url_for('auth_callback', provider=self.provider)
        return await self.client.authorize_redirect(request, redirect_uri)

    async def authorize_access_token(self, request):
        return await self.client.authorize_access_token(request)
