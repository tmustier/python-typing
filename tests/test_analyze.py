"""Tests for analyze_typing.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


def run_analyze_typing(project_dir: Path) -> subprocess.CompletedProcess:
    """Run analyze_typing.py in the given project directory."""
    script = Path(__file__).parent.parent / "scripts" / "analyze_typing.py"
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )


class TestAnalyzeTyping:
    """Test analyze_typing.py functionality."""

    def test_runs_on_untyped_fixture(self, fixtures_dir: Path):
        """Test analysis on untyped fixture."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        
        assert result.returncode == 0
        output = result.stdout.lower()
        
        # Should show error count
        assert "error" in output
        # Should show breakdown
        assert "by error type" in output or "top error" in output

    def test_runs_on_partial_fixture(self, fixtures_dir: Path):
        """Test analysis on partial fixture."""
        result = run_analyze_typing(fixtures_dir / "partial")
        
        assert result.returncode == 0
        output = result.stdout.lower()
        
        assert "error" in output

    def test_runs_on_third_party_fixture(self, fixtures_dir: Path):
        """Test analysis on third_party fixture."""
        result = run_analyze_typing(fixtures_dir / "third_party")
        
        assert result.returncode == 0
        output = result.stdout.lower()
        
        assert "error" in output

    def test_shows_file_breakdown(self, fixtures_dir: Path):
        """Test that output includes file breakdown."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        
        assert result.returncode == 0
        output = result.stdout.lower()
        
        # Should mention files
        assert "file" in output or ".py" in output

    def test_shows_suggestion(self, fixtures_dir: Path):
        """Test that output includes suggestions."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        
        assert result.returncode == 0
        output = result.stdout.lower()
        
        # Should have some kind of suggestion
        assert "suggest" in output or "start" in output or "strategy" in output

    def test_handles_zero_errors(self, temp_project: Path):
        """Test analysis on project with no errors."""
        # Create a fully typed file
        (temp_project / "typed.py").write_text(
            "def hello(name: str) -> str:\n    return f'Hello {name}'\n"
        )
        (temp_project / "pyrightconfig.json").write_text(
            '{"typeCheckingMode": "strict"}'
        )
        
        result = run_analyze_typing(temp_project)
        
        assert result.returncode == 0
        output = result.stdout.lower()
        # Should indicate success or zero errors
        assert "0 error" in output or "no error" in output or "done" in output


class TestAnalyzeOutput:
    """Test specific output format expectations."""

    def test_error_count_in_output(self, fixtures_dir: Path):
        """Test that error count is clearly shown."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        
        # Should contain a number followed by 'error'
        import re
        assert re.search(r'\d+\s*error', result.stdout.lower())

    def test_percentage_in_breakdown(self, fixtures_dir: Path):
        """Test that breakdown shows percentages."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        
        # Should contain percentage
        assert "%" in result.stdout
