import jwt
from jwt import PyJWTError
from typing import Optional

from core.config import settings


class UserService:
    async def get_user_id(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("user_id")
            if user_id is None:
                raise ValueError("user_id отсутствует в токене")
            return user_id
        except PyJWTError as e:
            print(f"Ошибка декодирования токена: {e}")
            return None
