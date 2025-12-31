# Fixture: API module with mixed typing

from typing import Any, Dict, List


def fetch_data(url: str) -> Any:
    """Uses Any - defeats type checking."""
    return {"data": [1, 2, 3]}


def transform(data: Any) -> Dict[str, Any]:
    """Any in, Any out - no safety."""
    return {"result": data}


def validate(items: List) -> bool:
    """List without type parameter."""
    return len(items) > 0


class APIClient:
    base_url: str
    
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session = None  # No type annotation
    
    def get(self, path: str):  # Missing return type
        return fetch_data(self.base_url + path)
