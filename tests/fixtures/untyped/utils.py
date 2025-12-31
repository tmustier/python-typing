# Fixture: Untyped utility functions

def format_name(first, last):
    """Missing annotations."""
    return f"{first} {last}"


def parse_config(path):
    """Missing annotations, file operations."""
    with open(path) as f:
        return f.read()


def merge_dicts(a, b):
    """Missing annotations, dict operations."""
    result = {}
    result.update(a)
    result.update(b)
    return result


DEFAULT_CONFIG = {"timeout": 30, "retries": 3}
