# Fixture: Code using third-party libraries without stubs
# This will generate reportMissingTypeStubs errors

# Note: These imports will fail if packages not installed,
# but pyright will still report the missing stubs error
try:
    import requests  # type: ignore  # Intentional - testing stub detection
except ImportError:
    requests = None  # type: ignore

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


def fetch_json(url: str) -> dict:
    """Uses requests - may lack type stubs."""
    if requests is None:
        return {}
    response = requests.get(url)
    return response.json()


def load_yaml(path: str) -> dict:
    """Uses pyyaml - may lack type stubs."""
    if yaml is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f)


def process_config(url: str, local_path: str) -> dict:
    """Combines both."""
    remote = fetch_json(url)
    local = load_yaml(local_path)
    return {**local, **remote}
