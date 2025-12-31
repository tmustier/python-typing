# Frequently Asked Questions

## During Setup

### What is this going to do to my repo?

It adds configuration files only:
- `pyrightconfig.json` - Type checker config
- `.long-task-harness/` directory - Progress tracking (gitignored state files)
- `.git/hooks/pre-commit` - Warning hook (optional)

Your source code is not modified. You can delete these files to undo.

### How long will this take?

Depends on codebase size and error count:

| Errors | Estimated Time |
|--------|----------------|
| <100 | 1-2 hours |
| 100-500 | 1-2 days |
| 500-1000 | 3-5 days |
| 1000+ | 1-2 weeks |

With ralph-wiggum loops, you can run unattended overnight.

### Can I undo this?

Yes. Delete:
- `pyrightconfig.json`
- `.long-task-harness/` directory (or just the typing-related files)
- `.git/hooks/pre-commit` (if added)

Your code is unchanged.

---

## During Fixing

### I'm stuck on this error, what do I do?

1. Check `references/patterns.md` for similar patterns
2. Check `.long-task-harness/typing-findings.md` for documented workarounds
3. Search pyright issues: https://github.com/microsoft/pyright/issues
4. For third-party libs: check if stubs exist (`pip install types-{lib}`)
5. Ask for help rather than using `# type: ignore`

### Third-party library has no types, now what?

Options in order of preference:

1. **Install stub package**: `pip install types-{library}`
2. **Check for inline types**: Look for `py.typed` marker in the package
3. **Create minimal local stubs**: Add `.pyi` file in `stubs/` directory
4. **Last resort**: Use `# type: ignore[import]` with documentation in typing-findings.md

### The error count isn't going down, why?

Common causes:

1. **Cascading errors**: Fixing one error reveals others that were masked
2. **Pyright update**: New version added checks - see changelog
3. **Gnarly file**: Some files have deeply interconnected issues

Don't worry - progress isn't always linear. Focus on one file at a time.

### Can I skip this file/module for now?

Yes. Add to `exclude` in pyrightconfig.json:

```json
{
  "exclude": ["src/legacy/**", "src/problematic_module.py"]
}
```

Come back to it later or document why it's excluded.

### How do I handle conditional imports?

See `references/patterns.md` Layer 4 for detailed patterns. Quick summary:

```python
# Option 1: TYPE_CHECKING guard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from optional_lib import Thing

# Option 2: Consistent callable signature
process: Callable[[str], int]
try:
    from fast_lib import process
except ImportError:
    from slow_lib import process
```

### What's the difference between `object` and `Any`?

- `Any`: Disables type checking - anything goes in and out
- `object`: Type-safe "any value" - you can store anything but must narrow before use

```python
def store(x: Any) -> None:
    x.whatever()  # OK - no checking

def store(x: object) -> None:
    x.whatever()  # Error - object has no 'whatever'
    if isinstance(x, str):
        x.upper()  # OK - narrowed to str
```

Prefer `object` when you genuinely don't know the type but want safety.

---

## Philosophical

### Why can't I just use `# type: ignore`?

Because it defeats the purpose. Type checking catches bugs - silencing it hides bugs. Every `type: ignore` is:

- A bug you might ship
- Technical debt for the next person
- A signal the code design may be wrong

Fix the type, fix the code, or document why it's truly unfixable.

### This is taking forever, is it worth it?

Yes. Benefits compound:

- **Catches bugs before runtime** - No more "AttributeError: NoneType has no..."
- **Better IDE support** - Autocomplete, refactoring, go-to-definition
- **Documents contracts** - Function signatures are self-documenting
- **Safer refactoring** - Change a type, see all affected code
- **Reduced debugging** - Types catch errors that tests might miss

The upfront cost pays off within months.

### My code works fine, why does pyright complain?

"Works fine" means "works for the inputs I've tested." Pyright checks *all possible* inputs. Common cases:

| Your assumption | Reality |
|-----------------|---------|
| "This is never None" | Function signature says `Optional[str]` |
| "This is always a string" | Union type could be `int` too |
| "This attribute exists" | Type doesn't guarantee it |

These are potential runtime errors waiting to happen.

### Should I aim for 100% type coverage?

Start with getting pyright to pass (0 errors). Then consider:

- **Critical paths**: Payment, auth, data processing - type thoroughly
- **Internal utilities**: Less critical, can be looser
- **Generated code**: May not be worth typing manually

Focus on value, not vanity metrics.

---

## Completion

### How do I know when I'm done?

When `npx pyright` reports 0 errors. Then:

1. Review typing-findings.md for any documented issues
2. Consider adding pyright to CI (fail on errors)
3. Update pyrightconfig to remove any temporary excludes

### What do I do with typing-findings.md after?

Keep it! It documents:

- Known limitations in third-party libraries
- Design decisions about type tradeoffs
- Historical context for any remaining `type: ignore` comments

Future maintainers will thank you.

### Should I enforce this in CI?

Yes, once you hit 0 errors:

```yaml
# .github/workflows/typecheck.yml
name: Type Check
on: [push, pull_request]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g pyright
      - run: pyright
```

This prevents regressions.

---

## Gotchas

### Pyright updated and now I have new errors!

Pyright releases frequently. Options:

1. **Fix the new errors** (recommended)
2. **Pin pyright version**: `pip install pyright==1.1.x` or in package.json
3. **Check changelog**: See what changed at https://github.com/microsoft/pyright/releases

### My IDE shows different errors than CLI

IDEs often bundle their own pyright version. Ensure consistency:

- VS Code: Check Pylance version in extensions
- Use `npx pyright` as source of truth
- Consider pinning version in both places

### Some errors only appear in strict mode

That's expected. Strict mode enables additional checks:

- `reportUnknownMemberType`
- `reportUnknownArgumentType`
- `reportUnknownVariableType`
- etc.

You can disable specific checks in pyrightconfig.json if needed, but try to fix them first.
