from typing import Any, Dict, Optional
from urllib.parse import parse_qs

from fastapi import Request


def extract_query_params(request: Request, raw_params: Optional[str] = None) -> Dict[str, Any]:
    """
    Универсальный парсер query-параметров.

    Args:
        request (Request): FastAPI запрос.
        raw_params (Optional[str]): Необязательная строка параметров (например, из другого источника).

    Returns:
        Dict[str, Any]: Словарь параметров, где ключи — названия параметров, значения — их значения.
    """
    query_string = raw_params if raw_params else request.url.query
    q_params = parse_qs(query_string, keep_blank_values=True)

    parsed_params = {k: v if len(v) > 1 else v[0] for k, v in q_params.items()}
    return parsed_params
