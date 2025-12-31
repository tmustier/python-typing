"""Tests for init_typing.py script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_init_typing(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the init_typing.py script with given arguments."""
    script = Path(__file__).parent.parent / "scripts" / "init_typing.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60
    )


class TestInitTyping:
    """Test init_typing.py functionality."""

    def test_creates_pyrightconfig(self, temp_project: Path) -> None:
        """Test that pyrightconfig.json is created."""
        result = run_init_typing(temp_project)
        assert result.returncode == 0

        config_path = temp_project / "pyrightconfig.json"
        assert config_path.exists()

        content = config_path.read_text()
        assert "strict" in content

    def test_creates_pyrightconfig_standard(self, temp_project: Path) -> None:
        """Test creation with standard mode."""
        result = run_init_typing(temp_project, "--level", "standard")
        assert result.returncode == 0

        config_path = temp_project / "pyrightconfig.json"
        content = config_path.read_text()
        assert "standard" in content

    def test_creates_pyrightconfig_basic(self, temp_project: Path) -> None:
        """Test creation with basic mode."""
        result = run_init_typing(temp_project, "--level", "basic")
        assert result.returncode == 0

        config_path = temp_project / "pyrightconfig.json"
        content = config_path.read_text()
        assert "basic" in content

    def test_creates_rules(self, temp_project: Path) -> None:
        """Test that typing discipline rules are created."""
        result = run_init_typing(temp_project)
        assert result.returncode == 0

        rules_dir = temp_project / ".long-task-harness" / "rules"
        assert rules_dir.exists()

        expected_rules = [
            "block-type-ignore.md",
            "block-gratuitous-assert.md",
            "warn-any-type.md",
            "warn-cast-overuse.md"
        ]
        for rule in expected_rules:
            assert (rules_dir / rule).exists(), f"Missing rule: {rule}"

    def test_creates_typing_findings(self, temp_project: Path) -> None:
        """Test that typing-findings.md is created."""
        result = run_init_typing(temp_project)
        assert result.returncode == 0

        findings = temp_project / ".long-task-harness" / "typing-findings.md"
        assert findings.exists()
        assert "Typing Findings Log" in findings.read_text()

    def test_creates_precommit_hook(self, temp_project: Path) -> None:
        """Test that pre-commit hook is created."""
        result = run_init_typing(temp_project)
        assert result.returncode == 0

        hook = temp_project / ".git" / "hooks" / "pre-commit"
        assert hook.exists()
        assert "pyright" in hook.read_text()

    def test_skips_rules_with_flag(self, temp_project: Path) -> None:
        """Test --no-rules flag."""
        result = run_init_typing(temp_project, "--no-rules")
        assert result.returncode == 0

        rules_dir = temp_project / ".long-task-harness" / "rules"
        assert not rules_dir.exists()

    def test_skips_hook_with_flag(self, temp_project: Path) -> None:
        """Test --no-hook flag."""
        result = run_init_typing(temp_project, "--no-hook")
        assert result.returncode == 0

        hook = temp_project / ".git" / "hooks" / "pre-commit"
        assert not hook.exists()

    def test_backup_existing_config(self, temp_project: Path) -> None:
        """Test that existing config is backed up."""
        existing = temp_project / "pyrightconfig.json"
        existing.write_text('{"old": true}')

        result = run_init_typing(temp_project)
        assert result.returncode == 0

        backup = temp_project / "pyrightconfig.json.bak"
        assert backup.exists()
        assert '{"old": true}' in backup.read_text()

    def test_output_shows_baseline(self, temp_project_with_errors: Path) -> None:
        """Test that output shows baseline error count."""
        result = run_init_typing(temp_project_with_errors)
        assert result.returncode == 0

        stdout: str = result.stdout.lower()
        assert "baseline" in stdout or "error" in stdout
