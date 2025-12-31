"""Tests for analyze_typing.py script."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def run_analyze_typing(cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run the analyze_typing.py script in the given directory."""
    script = Path(__file__).parent.parent / "scripts" / "analyze_typing.py"
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60
    )


class TestAnalyzeTyping:
    """Test analyze_typing.py functionality."""

    def test_runs_on_untyped_fixture(self, fixtures_dir: Path) -> None:
        """Test that analysis runs on untyped fixture."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "error" in output

    def test_runs_on_partial_fixture(self, fixtures_dir: Path) -> None:
        """Test that analysis runs on partial fixture."""
        result = run_analyze_typing(fixtures_dir / "partial")
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "error" in output

    def test_runs_on_third_party_fixture(self, fixtures_dir: Path) -> None:
        """Test that analysis runs on third_party fixture."""
        result = run_analyze_typing(fixtures_dir / "third_party")
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "error" in output or "warning" in output

    def test_shows_file_breakdown(self, fixtures_dir: Path) -> None:
        """Test that output shows file breakdown."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "by file" in output

    def test_shows_suggestion(self, fixtures_dir: Path) -> None:
        """Test that output shows suggested strategy."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "suggest" in output or "strategy" in output

    def test_handles_zero_errors(self, temp_project: Path) -> None:
        """Test handling of project with no errors."""
        # Create pyrightconfig.json with basic mode
        (temp_project / "pyrightconfig.json").write_text("""{
  "typeCheckingMode": "basic"
}""")

        # Create fully typed file
        (temp_project / "main.py").write_text("""
def hello() -> str:
    return 'world'
""")

        result = run_analyze_typing(temp_project)
        assert result.returncode == 0

        output: str = result.stdout.lower()
        assert "0 error" in output or "no error" in output


class TestAnalyzeOutput:
    """Test analyze output format."""

    def test_error_count_in_output(self, fixtures_dir: Path) -> None:
        """Test that error count appears in output."""
        result = run_analyze_typing(fixtures_dir / "untyped")
        assert result.returncode == 0

        # Should match pattern like "44 errors"
        assert re.search(r"\d+ errors?", result.stdout.lower())

    def test_percentage_in_breakdown(self, fixtures_dir: Path) -> None:
        """Test that breakdown shows percentages."""
        result = run_analyze_typing(fixtures_dir / "untyped")

        # Should contain percentage
        assert "%" in result.stdout
