"""Pytest configuration and fixtures."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def skill_dir() -> Path:
    """Return the skill root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir(skill_dir: Path) -> Path:
    """Return the fixtures directory."""
    return skill_dir / "tests" / "fixtures"


@pytest.fixture
def temp_project(tmp_path: Path):
    """Create a temporary project directory for testing init_typing.py."""
    project = tmp_path / "test_project"
    project.mkdir()
    
    # Create a minimal Python file
    (project / "main.py").write_text("def hello():\n    return 'world'\n")
    
    # Initialize git repo (needed for pre-commit hook)
    os.system(f"cd {project} && git init -q")
    
    yield project
    
    # Cleanup
    shutil.rmtree(project, ignore_errors=True)


@pytest.fixture
def temp_project_with_errors(tmp_path: Path, fixtures_dir: Path):
    """Create a temp project with known type errors."""
    project = tmp_path / "error_project"
    shutil.copytree(fixtures_dir / "untyped", project)
    
    # Initialize git
    os.system(f"cd {project} && git init -q")
    
    yield project
    
    shutil.rmtree(project, ignore_errors=True)
