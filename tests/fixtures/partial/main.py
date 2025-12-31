# Fixture: Partially typed Python code
# Some annotations present, some missing

from typing import Optional


def get_user(user_id: int) -> dict:
    """Has annotations but dict is too vague."""
    return {"id": user_id, "name": "Alice"}


def process_items(items: list) -> list:
    """Has annotations but list is too vague."""
    result = []
    for item in items:
        result.append(item.upper())  # Error: item is Unknown
    return result


class Config:
    timeout: int
    retries: int
    
    def __init__(self, timeout: int, retries: int) -> None:
        self.timeout = timeout
        self.retries = retries


def get_config(path: str) -> Optional[Config]:
    """Returns Optional but caller might not handle None."""
    if not path:
        return None
    return Config(30, 3)


def use_config(path: str) -> int:
    """Doesn't handle Optional correctly."""
    config = get_config(path)
    return config.timeout  # Error: config might be None
