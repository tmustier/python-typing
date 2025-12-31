"""Pytest fixtures for python-typing tests."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def skill_dir() -> Path:
    """Return the skill directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir(skill_dir: Path) -> Path:
    """Return the test fixtures directory."""
    return skill_dir / "tests" / "fixtures"


@pytest.fixture
def temp_project(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary project directory."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create minimal Python file
    (project / "main.py").write_text("def hello():\n    return 'world'\n")

    # Create git repo for hook tests
    git_dir = project / ".git"
    git_dir.mkdir()
    (git_dir / "hooks").mkdir()

    original_cwd = Path.cwd()
    try:
        os.chdir(project)
        yield project
    finally:
        os.chdir(original_cwd)


@pytest.fixture
def temp_project_with_errors(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary project with type errors."""
    project = tmp_path / "test_project_errors"
    project.mkdir()

    # Create Python file with type errors
    (project / "main.py").write_text("""
def greet(name):
    return "Hello " + name

def process(data):
    return data.get("key")
""")

    # Create pyrightconfig.json
    (project / "pyrightconfig.json").write_text("""{
  "typeCheckingMode": "strict"
}""")

    # Create git repo
    git_dir = project / ".git"
    git_dir.mkdir()
    (git_dir / "hooks").mkdir()

    original_cwd = Path.cwd()
    try:
        os.chdir(project)
        yield project
    finally:
        os.chdir(original_cwd)
