# mypy: ignore-errors
from typing import Any, Dict, Optional


def build_body(
    query: Optional[str] = None,
    page: int = 0,
    size: int = 10,
    sort_order: Optional[str] = None,
    sort_field: Optional[str] = None,
    genre_id: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    bool_clause = {"must": [{"multi_match": {"query": query}}]} if query else {}
    sort_clause = {sort_field: {"order": sort_order}} if sort_order and sort_field else {}

    if genre_id:
        bool_clause.setdefault("filter", []).append({"nested": {
            "path": "genres",
            "query": {
                "bool": {
                    "must": [{"match": {"genres.uuid": genre_id}}]
                }
            }
        }})

    return {
        "query": {"bool": bool_clause},
        "sort": sort_clause,
        "from": page,
        "size": size
    }
