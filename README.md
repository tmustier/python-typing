# Python Typing Skill

A skill for migrating Python codebases to strict type checking using pyright.

## What it does

- **Setup automation** - Initialize pyright strict config, rules, and tracking
- **Fix patterns** - Common solutions for type errors (not workarounds)
- **Discipline enforcement** - Rules that block `# type: ignore` and other shortcuts
- **Progress tracking** - Integration with long-task-harness for session continuity
- **Iteration loops** - Optional ralph-wiggum support for unattended fixing (Claude Code only)

## Installation

Clone to your skills directory:

```bash
git clone https://github.com/tmustier/python-typing ~/.claude/skills/python-typing
```

Or wherever your agent stores skills.

## Usage

Ask your AI agent to set up typing:

```
Set up strict type checking for this project
```

The skill will:
1. Ask your preferred strictness level (strict/standard/basic)
2. Show baseline error counts
3. Offer full or minimal setup
4. Install configs, rules, and tracking
5. Show fix strategy and get you started

## What gets installed

### Required
- `pyrightconfig.json` - Type checker config

### Recommended
- `.long-task-harness/rules/` - Typing discipline rules
- `.long-task-harness/typing-findings.md` - Document unfixable issues
- Pre-commit hook - Warns on errors

### Optional
- long-task-harness - Progress tracking across sessions
- ralph-wiggum plugin - Iteration loop automation (Claude Code only)

## The Rules

This skill enforces typing discipline:

| Rule | Action | Purpose |
|------|--------|---------|
| block-type-ignore | Block | No `# type: ignore` - fix the issue |
| block-gratuitous-assert | Warn | No `assert x is not None` hacks |
| warn-any-type | Warn | Avoid `Any` - use specific types |
| warn-cast-overuse | Warn | Avoid `cast()` - use isinstance() |

## Fix Strategy

The skill guides you through errors in layers:

1. **Quick wins** - Unused imports, missing return types, generic args
2. **Annotations** - Parameter types, class attributes, module variables
3. **Type safety** - None checks, narrowing, unions
4. **Structural** - Conditional imports, TypedDict, Protocol
5. **External** - Missing stubs, third-party workarounds
6. **Edge cases** - Complex generics, metaprogramming

## Dependencies

- **Required**: Node.js (for npx pyright) or `pip install pyright`
- **Optional**: [long-task-harness](https://github.com/tmustier/long-task-harness) for progress tracking
- **Optional**: [ralph-wiggum](https://github.com/tmustier/claude-plugins-official) for iteration loops (Claude Code only)

## File Structure

```
python-typing/
├── SKILL.md                 # Main skill instructions (for AI)
├── README.md                # This file (for humans)
├── scripts/
│   ├── init_typing.py       # Initialize typing setup
│   └── analyze_typing.py    # Analyze error distribution
├── references/
│   ├── patterns.md          # Common fix patterns
│   └── faq.md               # Detailed FAQ
├── assets/
│   └── rules/               # Rule templates
└── .long-task-harness/
    ├── SPEC.md              # Full specification
    ├── features.json        # Development tracking
    └── long-task-progress.md
```

## Future Enhancements

- TypeScript/tsc support
- Cross-agent ralph-wiggum (Pi, Cursor, etc.)
- CI templates (GitHub Actions, GitLab)
- VS Code recommended settings

## License

MIT

## Contributing

Issues and PRs welcome at https://github.com/tmustier/python-typing
