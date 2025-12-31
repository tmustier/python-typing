# Python Typing Skill - Specification

## Overview

A skill for migrating Python codebases to strict type checking using pyright. Provides setup automation, fix patterns, discipline enforcement, and optional iteration loop support.

**Target users:** Developers who want to add or improve type safety in existing Python codebases.

**License:** MIT

---

## Core Value Proposition

1. **Setup automation** - Initialize pyright strict config, rules, and tracking in any project
2. **Fix patterns** - Teach proper ways to resolve type errors (not silence them)
3. **Discipline enforcement** - Rules that block `# type: ignore`, warn on `Any`/`cast`/assert hacks
4. **Progress tracking** - Integration with long-task-harness for session continuity
5. **Iteration loops** - Optional ralph-wiggum integration for unattended fixing (Claude Code only)

---

## Onboarding Flow

### Entry Point

User says something like:
- "Set up strict type checking for this project"
- "Help me add types to this codebase"
- "Run a typing migration"

### Flow

```
Agent: I'll set up pyright type checking with discipline enforcement.

## Strictness Level

What level of type checking?
  A) strict - Maximum type safety, catches most issues
  B) standard - Balanced, good for existing codebases
  C) basic - Minimal, just obvious bugs

[Agent runs pyright at each level and shows baseline counts]

Current baseline:
  strict:   734 errors
  standard: 89 errors
  basic:    12 errors

> User picks (or agent infers from "strict typing" in request)

## Setup Options

Would you like:
  A) **Recommended setup** - Full setup with tracking and rules
  B) **Minimal setup** - Just pyright config and rules
  C) **Custom** - Choose each component

> User picks A (most common)
```

### Recommended Setup (Option A)

Agent installs:
1. `pyrightconfig-strict.json` (or standard/basic based on choice)
2. `.long-task-harness/` directory with:
   - `rules/block-type-ignore.md`
   - `rules/block-gratuitous-assert.md`
   - `rules/warn-any-type.md`
   - `rules/warn-cast-overuse.md`
   - `typing-findings.md`
3. Pre-commit hook (warn but allow)
4. ralph-wiggum plugin (if Claude Code detected)

Agent then explains what was installed:

```
Done! Here's what I set up:

## pyright Configuration
Created pyrightconfig-strict.json with strict type checking.
Baseline: 734 errors

## Typing Discipline Rules
Added to .long-task-harness/rules/:
- block-type-ignore: Prevents # type: ignore (must fix properly)
- block-gratuitous-assert: Warns on assert x is not None
- warn-any-type: Warns on explicit Any usage
- warn-cast-overuse: Warns on cast() usage

## Progress Tracking (long-task-harness)
Installed long-task-harness for tracking progress across sessions.
This creates .long-task-harness/ with:
- Session logs (what was fixed, decisions made)
- Feature tracking
- typing-findings.md for documenting unfixable issues

Learn more: [link to long-task-harness repo]

## Pre-commit Hook
Added hook that warns (but doesn't block) if pyright has errors.
Shows error count on each commit to track progress.

## Iteration Loop (ralph-wiggum) [Claude Code only]
Installed ralph-wiggum plugin for running unattended fix loops.

Ready to start? Here's the recommended approach:
[shows fix strategy]
```

### Minimal Setup (Option B)

Agent installs only:
1. `pyrightconfig-{level}.json`
2. Rules in `.long-task-harness/rules/` (creates dir if needed)
3. `typing-findings.md` template

Skips: long-task-harness full setup, ralph-wiggum, pre-commit hook

Agent notes:
```
Minimal setup complete. Note: I highly recommend installing 
long-task-harness and ralph-wiggum for the best experience.
Run "set up full typing tracking" if you change your mind.
```

### Custom Setup (Option C)

```
Select components (enter numbers, e.g., 1,2,3,5):

Core:
  [1] pyright config - Strict/standard/basic type checking
  [2] typing-findings.md - Document unfixable issues

Rules:
  [3] All typing discipline rules (recommended)
  [4] Choose rules individually

Tracking & Automation:
  [5] long-task-harness - Progress tracking across sessions
  [6] Pre-commit hook - Warn on commit if errors remain
  [7] ralph-wiggum - Iteration loop automation (Claude Code only)
```

If user picks [4]:
```
Select rules:
  [a] block-type-ignore - Block # type: ignore comments
  [b] block-gratuitous-assert - Warn on assert x is not None
  [c] warn-any-type - Warn on explicit Any
  [d] warn-cast-overuse - Warn on cast() usage
```

---

## Fix Strategy

### Approach: Analyze Strict, Fix in Layers

1. Run strict mode to see full scope
2. Analyze error distribution
3. Fix in layers (quick wins → structural → edge cases)

### Layers

```
Layer 1: Low-hanging fruit (mechanical fixes)
- Unused imports/variables
- Missing return type annotations on obvious functions
- Generic type arguments (List → List[str])

Layer 2: Annotation completeness
- Function parameter types
- Class attribute types
- Module-level variable types

Layer 3: Type safety fixes
- None checks (Optional handling)
- Type narrowing (isinstance, TypeGuard)
- Union type handling

Layer 4: Structural patterns
- Conditional imports (try/except)
- TypedDict for dict shapes
- Protocol for duck typing

Layer 5: External dependencies
- Missing stubs (stub packages or inline)
- Third-party library workarounds
- Document in typing-findings.md

Layer 6: Edge cases
- Complex generics
- Metaprogramming
- Genuinely unfixable → document and consider type: ignore (with justification)
```

### Analysis Script

Provide `scripts/analyze_typing.py`:

```
$ python scripts/analyze_typing.py

Baseline: 734 errors (strict mode)

Top error types:
  reportUnknownMemberType     312 (42%) → Usually third-party libs
  reportMissingParameterType   64 (9%)  → Add annotations
  reportUnknownArgumentType    78 (11%) → Check function calls
  ...

Worst files:
  src/api/client.py          45 errors
  src/utils/helpers.py       38 errors
  ...

Suggested starting point: src/utils/helpers.py
  - Isolated module (few imports)
  - Many quick wins (missing return types)
  - Fixing here won't cascade elsewhere
```

---

## Rules

### block-type-ignore (action: block)

```yaml
pattern: "#\\s*type:\\s*ignore"
```

**Message:**
```
Type ignore comment blocked.

Do NOT use # type: ignore to suppress errors. Instead:
- Fix the actual type issue
- Add proper type annotations  
- Refactor if the type system reveals a design problem

If genuinely unfixable, document in typing-findings.md first, then add
the ignore with a comment referencing the finding.
```

### block-gratuitous-assert (action: warn)

```yaml
pattern: "assert\\s+\\w+\\s+is\\s+not\\s+None"
```

**Message:**
```
Gratuitous assert detected.

assert x is not None just to satisfy types is a code smell.

Better approaches:
- Early return: if x is None: return
- Conditional: if x is not None: x.method()
- Fix upstream to not return Optional
- Raise proper exception with context
```

### warn-any-type (action: warn)

```yaml
pattern: ":\\s*Any\\b|->\\s*Any\\b|\\[Any\\]"
```

**Message:**
```
Explicit Any type detected.

Using Any defeats the purpose of type checking. Prefer:
- Specific types when known
- TypeVar for generic functions
- Union types for multiple possibilities
- object for "any object" (still type-safe)
- Protocol for structural typing
```

### warn-cast-overuse (action: warn)

```yaml
pattern: "from typing import.*cast|cast\\("
```

**Message:**
```
Cast usage detected.

cast() tells the type checker "trust me" without runtime verification.

Prefer:
- Type narrowing with isinstance()
- TypeGuard functions for complex narrowing
- Fixing upstream type annotations
```

---

## typing-findings.md

Template:

```markdown
# Typing Findings Log

Document issues discovered during type migration that require investigation
or cannot be fixed with simple annotations.

## Format

### [YYYY-MM-DD] Finding Title
**File**: path/to/file.py:123
**Category**: [design-issue | api-mismatch | missing-stubs | unfixable]
**Severity**: [low | medium | high]

Description of the issue and why it couldn't be fixed.

---

## Findings

(Add entries as issues are discovered)
```

---

## Pre-commit Hook

**Behavior:** Warn but allow commits

```bash
#!/bin/bash
# .git/hooks/pre-commit (or via pre-commit framework)

echo "Running pyright type check..."
OUTPUT=$(npx pyright 2>&1)
EXIT_CODE=$?
ERROR_COUNT=$(echo "$OUTPUT" | grep -oE '[0-9]+ errors?' | head -1)

if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️  Pyright: $ERROR_COUNT remaining"
    echo "   (commit allowed, but please continue fixing)"
else
    echo "✅ Pyright: No errors"
fi

# Always allow commit
exit 0
```

---

## Ralph-Wiggum Integration

### Prerequisites

- Claude Code only (other agents: future enhancement)
- Plugin installed from `tmustier/claude-plugins-official`

### Installation

Agent runs:
```bash
# Clone plugin to Claude Code plugins directory
git clone https://github.com/tmustier/claude-plugins-official ~/.claude/plugins/marketplaces/claude-plugins-official

# Or if already exists, just reference it
```

### Prompt Template

```
/ralph-loop "Fix pyright strict mode errors.

## Setup
Run: npx pyright
Baseline: {ERROR_COUNT} errors

## Rules (CRITICAL)
1. Do NOT use # type: ignore - fix the actual issue
2. Do NOT use assert x is not None - use proper conditionals
3. Avoid Any - use specific types
4. Avoid cast() - use isinstance() narrowing

## Workflow
1. Run pyright, note error count
2. Pick 5-10 related errors (same file or same type)
3. Fix them properly
4. Run pyright to verify
5. Commit with descriptive message
6. Repeat

## Every 50 Errors
- Review for consistency
- Document unfixable issues in typing-findings.md
- Note patterns

## If Stuck
- Check typing-findings.md for similar issues
- For third-party libs: document and use minimal workaround
- Ask for help rather than using type: ignore

## Completion
When pyright reports 0 errors: <promise>TYPING_COMPLETE</promise>" --completion-promise "TYPING_COMPLETE" --max-iterations 300
```

Agent shows this prompt to user and confirms before they run it.

---

## FAQ

### During Setup

**Q: What is this going to do to my repo?**

A: It adds configuration files only:
- `pyrightconfig-{level}.json` - Type checker config
- `.long-task-harness/` directory - Progress tracking (gitignored state files)
- `.git/hooks/pre-commit` - Warning hook (optional)

Your source code is not modified. You can delete these files to undo.

**Q: How long will this take?**

A: Depends on codebase size and error count:
- <100 errors: 1-2 hours
- 100-500 errors: 1-2 days
- 500-1000 errors: 3-5 days
- 1000+ errors: 1-2 weeks

With ralph-wiggum loops, you can run unattended overnight.

**Q: Can I undo this?**

A: Yes. Delete:
- `pyrightconfig-*.json`
- `.long-task-harness/` directory
- `.git/hooks/pre-commit` (if added)

Your code is unchanged.

### During Fixing

**Q: I'm stuck on this error, what do I do?**

A: Check the patterns reference (references/patterns.md) for common fixes:
- Missing stubs → install stub package or create inline stubs
- Conditional imports → restructure or use TYPE_CHECKING
- Complex generics → simplify or use Protocol
- Truly unfixable → document in typing-findings.md

**Q: Third-party library has no types, now what?**

A: Options in order of preference:
1. Install stub package: `pip install types-{library}`
2. Check if library has inline types (py.typed marker)
3. Create minimal local stubs in `stubs/` directory
4. Use `# type: ignore[import]` with documentation in typing-findings.md

**Q: The error count isn't going down, why?**

A: Common causes:
- Fixing one error reveals others (cascading)
- Pyright updated and added new checks
- You're in a particularly gnarly file

Don't worry - progress isn't always linear. Focus on one file at a time.

**Q: Can I skip this file/module for now?**

A: Yes. Add to `exclude` in pyrightconfig:
```json
{
  "exclude": ["src/legacy/**", "src/problematic_module.py"]
}
```

Come back to it later or document why it's excluded.

### Philosophical

**Q: Why can't I just use `# type: ignore`?**

A: Because it defeats the purpose. Type checking catches bugs - silencing it hides bugs. Every `type: ignore` is:
- A bug you might ship
- Technical debt for the next person
- A signal the code design may be wrong

Fix the type, fix the code, or document why it's truly unfixable.

**Q: This is taking forever, is it worth it?**

A: Yes. Benefits compound:
- Catches bugs before runtime
- Enables better IDE support (autocomplete, refactoring)
- Documents function contracts
- Makes refactoring safer
- Reduces debugging time long-term

The upfront cost pays off within months.

**Q: My code works fine, why does pyright complain?**

A: "Works fine" means "works for the inputs I've tested." Pyright checks *all possible* inputs. Common cases:
- None handling: your code assumes non-None but type says Optional
- Union types: your code assumes one type but could receive another
- Attribute access: your code assumes attribute exists but type doesn't guarantee it

These are potential runtime errors waiting to happen.

### Completion

**Q: How do I know when I'm done?**

A: When `npx pyright` reports 0 errors. Then:
1. Review typing-findings.md for any documented issues
2. Consider adding pyright to CI (fail on errors)
3. Update pyrightconfig to remove any excludes you added temporarily

**Q: What do I do with typing-findings.md after?**

A: Keep it! It documents:
- Known limitations in third-party libraries
- Design decisions about type tradeoffs
- Historical context for any remaining `type: ignore` comments

Future maintainers will thank you.

**Q: Should I enforce this in CI?**

A: Yes, once you hit 0 errors:
```yaml
# .github/workflows/typecheck.yml
- run: npx pyright
```

This prevents regressions.

### Gotchas

**Q: Pyright updated and now I have new errors!**

A: Pyright releases frequently. Options:
- Fix the new errors (recommended)
- Pin pyright version in requirements: `pyright==1.1.x`
- Check pyright changelog for what changed

---

## File Structure

```
python-typing/
├── SKILL.md                 # Main skill instructions
├── SPEC.md                  # This specification
├── README.md                # Human-facing documentation
├── scripts/
│   ├── init_typing.py       # Initialize typing setup in a project
│   └── analyze_typing.py    # Analyze error distribution
├── references/
│   ├── patterns.md          # Common fix patterns
│   └── faq.md               # Detailed FAQ (expanded from above)
└── assets/
    └── rules/               # Rule templates to copy
        ├── block-type-ignore.md
        ├── block-gratuitous-assert.md
        ├── warn-any-type.md
        └── warn-cast-overuse.md
```

---

## Future Enhancements

1. **TypeScript support** - Add `references/typescript-tsc.md` with TS-specific patterns
2. **Cross-agent ralph-wiggum** - Port iteration loops to work with Pi, Cursor, etc.
3. **CI templates** - GitHub Actions, GitLab CI, etc.
4. **VS Code integration** - Recommended settings, extensions
5. **Mypy support** - Alternative to pyright for teams that prefer it

---

## Dependencies

- **Required:** pyright (npm or pip install)
- **Optional:** long-task-harness (progress tracking)
- **Optional:** ralph-wiggum plugin (iteration loops, Claude Code only)

---

## Open Questions

(None remaining - spec is complete)
