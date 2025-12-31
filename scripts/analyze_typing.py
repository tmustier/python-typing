#!/usr/bin/env python3
"""
Analyze pyright error distribution to guide fix strategy.

Outputs:
- Total error count
- Breakdown by error type
- Breakdown by file
- Suggested starting point
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Optional


def run_pyright() -> Optional[dict]:
    """Run pyright and return JSON output."""
    try:
        result = subprocess.run(
            ["npx", "pyright", "--outputjson"],
            capture_output=True,
            text=True,
            timeout=120
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running pyright: {e}", file=sys.stderr)
        return None


def analyze_errors(data: dict) -> None:
    """Analyze and display error distribution."""
    diagnostics = data.get("generalDiagnostics", [])
    summary = data.get("summary", {})
    
    error_count = summary.get("errorCount", 0)
    warning_count = summary.get("warningCount", 0)
    
    print(f"\n{'='*60}")
    print(f"Pyright Analysis")
    print(f"{'='*60}\n")
    
    print(f"Total: {error_count} errors, {warning_count} warnings\n")
    
    if error_count == 0:
        print("🎉 No errors! You're done.")
        return
    
    # Analyze by rule
    rules: Counter[str] = Counter()
    files: Counter[str] = Counter()
    
    for diag in diagnostics:
        if diag.get("severity") == "error":  # Error
            rule = diag.get("rule", "unknown")
            rules[rule] += 1
            
            file_path = diag.get("file", "unknown")
            # Shorten path for display
            try:
                file_path = str(Path(file_path).relative_to(Path.cwd()))
            except ValueError:
                pass
            files[file_path] += 1
    
    # Display by rule
    print("By Error Type:")
    print("-" * 40)
    for rule, count in rules.most_common(10):
        pct = count / error_count * 100
        hint = _get_rule_hint(rule)
        print(f"  {rule:35} {count:4} ({pct:4.1f}%)")
        if hint:
            print(f"    └─ {hint}")
    
    if len(rules) > 10:
        print(f"  ... and {len(rules) - 10} more types")
    
    print()
    
    # Display by file
    print("By File (top 10):")
    print("-" * 40)
    for file_path, count in files.most_common(10):
        print(f"  {file_path:40} {count:4} errors")
    
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")
    
    print()
    
    # Suggest starting point
    _suggest_starting_point(rules, files, diagnostics)


def _get_rule_hint(rule: str) -> str:
    """Get a short hint for fixing this rule type."""
    hints = {
        "reportUnknownMemberType": "Usually third-party libs → install stubs",
        "reportMissingParameterType": "Add parameter annotations",
        "reportMissingTypeStubs": "pip install types-{package}",
        "reportUnknownArgumentType": "Check function call types",
        "reportGeneralTypeIssues": "Type mismatch → fix logic or annotations",
        "reportOptionalMemberAccess": "Add None check before access",
        "reportUnknownVariableType": "Add variable annotation",
        "reportPrivateUsage": "Rename or make public",
        "reportAttributeAccessIssue": "Check attribute exists on type",
        "reportReturnType": "Add return type annotation",
    }
    return hints.get(rule, "")


def _suggest_starting_point(rules: Counter, files: Counter, diagnostics: list) -> None:
    """Suggest where to start fixing."""
    print("Suggested Strategy:")
    print("-" * 40)
    
    # Check for quick wins
    quick_win_rules = [
        "reportMissingParameterType",
        "reportMissingTypeStubs", 
        "reportUnusedImport",
        "reportUnusedVariable",
        "reportReturnType",
    ]
    
    quick_wins = sum(rules.get(r, 0) for r in quick_win_rules)
    if quick_wins > 0:
        print(f"  1. Quick wins: {quick_wins} errors from missing annotations/imports")
        print(f"     Start with: reportMissingParameterType, reportReturnType")
    
    # Check for stub issues
    stub_count = rules.get("reportMissingTypeStubs", 0) + rules.get("reportUnknownMemberType", 0)
    if stub_count > 20:
        print(f"  2. Third-party stubs: {stub_count} errors may need stub packages")
        print(f"     Check: pip install types-requests types-pyyaml etc.")
    
    # Suggest smallest file with moderate errors
    if files:
        # Find files with 5-20 errors (manageable chunks)
        moderate_files = [(f, c) for f, c in files.items() if 5 <= c <= 20]
        if moderate_files:
            suggested = min(moderate_files, key=lambda x: x[1])
            print(f"  3. Good starting file: {suggested[0]}")
            print(f"     ({suggested[1]} errors - manageable chunk)")
        else:
            # Fall back to file with fewest errors
            smallest = files.most_common()[-1]
            print(f"  3. Start small: {smallest[0]} ({smallest[1]} errors)")
    
    print()


def main():
    print("Running pyright analysis...")
    data = run_pyright()
    
    if data is None:
        print("Failed to run pyright. Is it installed? (npm install -g pyright)")
        sys.exit(1)
    
    analyze_errors(data)


if __name__ == "__main__":
    main()
