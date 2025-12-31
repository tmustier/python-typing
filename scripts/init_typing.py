#!/usr/bin/env python3
"""
Initialize pyright typing setup in a project.

Creates:
- pyrightconfig-{level}.json
- .long-task-harness/rules/ with typing discipline rules
- .long-task-harness/typing-findings.md
- Pre-commit hook (optional)
- Installs long-task-harness (optional)
- Installs ralph-wiggum plugin (optional, Claude Code only)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_script_dir() -> Path:
    return Path(__file__).parent.resolve()


def get_skill_dir() -> Path:
    return get_script_dir().parent


def get_project_dir() -> Path:
    return Path.cwd()


def run_pyright(config: str | None = None) -> int:
    """Run pyright and return error count."""
    cmd = ["npx", "pyright", "--outputjson"]
    if config:
        cmd.extend(["-p", config])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        data = json.loads(result.stdout)
        return data.get("summary", {}).get("errorCount", -1)
    except Exception:
        return -1


def create_pyright_config(level: str, project_dir: Path) -> int:
    """Create pyrightconfig and return baseline error count."""
    
    configs = {
        "strict": {
            "typeCheckingMode": "strict",
            "pythonVersion": "3.11",
            "reportMissingTypeStubs": False,
            "reportMissingImports": False
        },
        "standard": {
            "typeCheckingMode": "standard",
            "pythonVersion": "3.11",
            "reportMissingTypeStubs": False
        },
        "basic": {
            "typeCheckingMode": "basic",
            "pythonVersion": "3.11"
        }
    }
    
    config = configs.get(level, configs["strict"])
    config_path = project_dir / f"pyrightconfig.json"
    
    # Check for existing config
    if config_path.exists():
        print(f"  ⚠️  pyrightconfig.json already exists, backing up to pyrightconfig.json.bak")
        shutil.copy(config_path, project_dir / "pyrightconfig.json.bak")
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"  ✅ Created pyrightconfig.json ({level} mode)")
    
    # Get baseline
    error_count = run_pyright()
    if error_count >= 0:
        print(f"  📊 Baseline: {error_count} errors")
    
    return error_count


def create_rules(project_dir: Path) -> None:
    """Copy typing discipline rules to project."""
    rules_src = get_skill_dir() / "assets" / "rules"
    harness_dir = project_dir / ".long-task-harness"
    rules_dst = harness_dir / "rules"
    
    harness_dir.mkdir(exist_ok=True)
    rules_dst.mkdir(exist_ok=True)
    
    rules = [
        "block-type-ignore.md",
        "block-gratuitous-assert.md",
        "warn-any-type.md",
        "warn-cast-overuse.md"
    ]
    
    for rule in rules:
        src = rules_src / rule
        dst = rules_dst / rule
        if src.exists():
            shutil.copy(src, dst)
            print(f"  ✅ Added rule: {rule}")
        else:
            print(f"  ⚠️  Rule not found: {src}")


def create_typing_findings(project_dir: Path) -> None:
    """Create typing-findings.md template."""
    harness_dir = project_dir / ".long-task-harness"
    harness_dir.mkdir(exist_ok=True)
    
    findings_path = harness_dir / "typing-findings.md"
    
    if findings_path.exists():
        print(f"  ⚠️  typing-findings.md already exists, skipping")
        return
    
    template = '''# Typing Findings Log

Document issues discovered during type migration that require investigation
or cannot be fixed with simple annotations.

## Format

```markdown
### [YYYY-MM-DD] Finding Title
**File**: path/to/file.py:123
**Category**: [design-issue | api-mismatch | missing-stubs | unfixable]
**Severity**: [low | medium | high]

Description of the issue and why it couldn't be fixed.
```

---

## Findings

(Add entries as issues are discovered)
'''
    
    with open(findings_path, "w") as f:
        f.write(template)
    
    print(f"  ✅ Created typing-findings.md")


def create_precommit_hook(project_dir: Path) -> None:
    """Create pre-commit hook that warns on pyright errors."""
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        print(f"  ⚠️  Not a git repo, skipping pre-commit hook")
        return
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / "pre-commit"
    
    # Check for existing hook
    if hook_path.exists():
        print(f"  ⚠️  pre-commit hook exists, appending pyright check")
        with open(hook_path, "a") as f:
            f.write("\n\n# Pyright type check (added by python-typing skill)\n")
            f.write(_get_hook_content())
    else:
        with open(hook_path, "w") as f:
            f.write("#!/bin/bash\n\n")
            f.write(_get_hook_content())
        hook_path.chmod(0o755)
    
    print(f"  ✅ Added pre-commit hook (warns on type errors)")


def _get_hook_content() -> str:
    return '''echo "Running pyright type check..."
OUTPUT=$(npx pyright 2>&1)
EXIT_CODE=$?
ERROR_COUNT=$(echo "$OUTPUT" | grep -oE '[0-9]+ errors?' | head -1)

if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️  Pyright: $ERROR_COUNT remaining"
    echo "   (commit allowed, but please continue fixing)"
else
    echo "✅ Pyright: No errors"
fi
'''


def install_long_task_harness(project_dir: Path) -> None:
    """Initialize long-task-harness if not present."""
    harness_dir = project_dir / ".long-task-harness"
    
    if (harness_dir / "long-task-progress.md").exists():
        print(f"  ✅ long-task-harness already initialized")
        return
    
    # Try to find and run init script
    lth_skill = Path.home() / ".claude" / "skills" / "long-task-harness"
    init_script = lth_skill / "scripts" / "init_harness.py"
    
    if init_script.exists():
        subprocess.run([sys.executable, str(init_script), str(project_dir)], 
                      capture_output=True)
        print(f"  ✅ Initialized long-task-harness")
    else:
        print(f"  ⚠️  long-task-harness skill not found at {lth_skill}")
        print(f"      Install from: https://github.com/tmustier/long-task-harness")


def install_ralph_wiggum() -> None:
    """Install ralph-wiggum plugin for Claude Code."""
    plugins_dir = Path.home() / ".claude" / "plugins" / "marketplaces"
    ralph_dir = plugins_dir / "claude-plugins-official"
    
    if ralph_dir.exists():
        print(f"  ✅ ralph-wiggum plugin already available")
        return
    
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run([
            "git", "clone", 
            "https://github.com/tmustier/claude-plugins-official",
            str(ralph_dir)
        ], capture_output=True, check=True)
        print(f"  ✅ Installed ralph-wiggum plugin")
        print(f"      Restart Claude Code to activate")
    except subprocess.CalledProcessError:
        print(f"  ⚠️  Failed to clone ralph-wiggum plugin")
        print(f"      Install manually: git clone https://github.com/tmustier/claude-plugins-official ~/.claude/plugins/marketplaces/claude-plugins-official")


def main():
    parser = argparse.ArgumentParser(description="Initialize pyright typing setup")
    parser.add_argument("--level", choices=["strict", "standard", "basic"], 
                       default="strict", help="Type checking strictness level")
    parser.add_argument("--full", action="store_true",
                       help="Full setup including long-task-harness and ralph-wiggum")
    parser.add_argument("--no-rules", action="store_true",
                       help="Skip typing discipline rules")
    parser.add_argument("--no-hook", action="store_true",
                       help="Skip pre-commit hook")
    parser.add_argument("--no-ralph", action="store_true",
                       help="Skip ralph-wiggum installation")
    parser.add_argument("--no-harness", action="store_true",
                       help="Skip long-task-harness initialization")
    
    args = parser.parse_args()
    project_dir = get_project_dir()
    
    print(f"\n🔧 Initializing pyright typing setup in: {project_dir}\n")
    
    # Core setup
    baseline = create_pyright_config(args.level, project_dir)
    
    if not args.no_rules:
        create_rules(project_dir)
    
    create_typing_findings(project_dir)
    
    if not args.no_hook:
        create_precommit_hook(project_dir)
    
    # Full setup extras
    if args.full:
        if not args.no_harness:
            install_long_task_harness(project_dir)
        if not args.no_ralph:
            install_ralph_wiggum()
    
    print(f"\n✅ Setup complete!")
    print(f"\nNext steps:")
    print(f"  1. Run: npx pyright")
    print(f"  2. Start fixing errors (see SKILL.md for strategy)")
    if baseline > 0:
        print(f"\nBaseline: {baseline} errors to fix")


if __name__ == "__main__":
    main()
