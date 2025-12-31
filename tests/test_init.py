"""Tests for init_typing.py script."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def run_init_typing(project_dir: Path, *args) -> subprocess.CompletedProcess:
    """Run init_typing.py in the given project directory."""
    script = Path(__file__).parent.parent / "scripts" / "init_typing.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )


class TestInitTyping:
    """Test init_typing.py functionality."""

    def test_creates_pyrightconfig(self, temp_project: Path):
        """Test that pyrightconfig.json is created."""
        result = run_init_typing(temp_project, "--level", "strict")
        
        assert result.returncode == 0
        assert (temp_project / "pyrightconfig.json").exists()
        
        config = json.loads((temp_project / "pyrightconfig.json").read_text())
        assert config["typeCheckingMode"] == "strict"

    def test_creates_pyrightconfig_standard(self, temp_project: Path):
        """Test standard mode config."""
        result = run_init_typing(temp_project, "--level", "standard")
        
        assert result.returncode == 0
        config = json.loads((temp_project / "pyrightconfig.json").read_text())
        assert config["typeCheckingMode"] == "standard"

    def test_creates_pyrightconfig_basic(self, temp_project: Path):
        """Test basic mode config."""
        result = run_init_typing(temp_project, "--level", "basic")
        
        assert result.returncode == 0
        config = json.loads((temp_project / "pyrightconfig.json").read_text())
        assert config["typeCheckingMode"] == "basic"

    def test_creates_rules(self, temp_project: Path):
        """Test that typing discipline rules are created."""
        result = run_init_typing(temp_project)
        
        assert result.returncode == 0
        rules_dir = temp_project / ".long-task-harness" / "rules"
        assert rules_dir.exists()
        
        expected_rules = [
            "block-type-ignore.md",
            "block-gratuitous-assert.md",
            "warn-any-type.md",
            "warn-cast-overuse.md",
        ]
        for rule in expected_rules:
            assert (rules_dir / rule).exists(), f"Missing rule: {rule}"

    def test_creates_typing_findings(self, temp_project: Path):
        """Test that typing-findings.md is created."""
        result = run_init_typing(temp_project)
        
        assert result.returncode == 0
        findings = temp_project / ".long-task-harness" / "typing-findings.md"
        assert findings.exists()
        assert "Typing Findings" in findings.read_text()

    def test_creates_precommit_hook(self, temp_project: Path):
        """Test that pre-commit hook is created."""
        result = run_init_typing(temp_project)
        
        assert result.returncode == 0
        hook = temp_project / ".git" / "hooks" / "pre-commit"
        assert hook.exists()
        assert "pyright" in hook.read_text().lower()

    def test_skips_rules_with_flag(self, temp_project: Path):
        """Test --no-rules flag."""
        result = run_init_typing(temp_project, "--no-rules")
        
        assert result.returncode == 0
        rules_dir = temp_project / ".long-task-harness" / "rules"
        assert not rules_dir.exists() or len(list(rules_dir.iterdir())) == 0

    def test_skips_hook_with_flag(self, temp_project: Path):
        """Test --no-hook flag."""
        result = run_init_typing(temp_project, "--no-hook")
        
        assert result.returncode == 0
        hook = temp_project / ".git" / "hooks" / "pre-commit"
        assert not hook.exists()

    def test_backup_existing_config(self, temp_project: Path):
        """Test that existing pyrightconfig.json is backed up."""
        existing = temp_project / "pyrightconfig.json"
        existing.write_text('{"existing": true}')
        
        result = run_init_typing(temp_project)
        
        assert result.returncode == 0
        backup = temp_project / "pyrightconfig.json.bak"
        assert backup.exists()
        assert json.loads(backup.read_text()) == {"existing": True}

    def test_output_shows_baseline(self, temp_project_with_errors: Path):
        """Test that output shows baseline error count."""
        result = run_init_typing(temp_project_with_errors)
        
        assert result.returncode == 0
        # Should mention baseline or error count
        assert "baseline" in result.stdout.lower() or "error" in result.stdout.lower()
