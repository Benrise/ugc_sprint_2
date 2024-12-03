from typing import Optional

import jwt
from core.config import settings
from fastapi import Request
from jwt import PyJWTError


class UserService:
    async def get_user_id_from_jwt(self, request: Request) -> Optional[str]:
        try:
            token = request.cookies.get("access_token_cookie")
            if not token:
                raise PyJWTError("Отсутствует токен")

            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("user_id")
            if user_id is None:
                raise ValueError("user_id отсутствует в токене")
            return str(user_id)
        except PyJWTError as e:
            print(f"Ошибка декодирования токена: {e}")
            return None
