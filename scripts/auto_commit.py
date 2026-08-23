"""Auto-commit engine.

Picks a realistic-looking change (add a helper, refactor one, update the
changelog, bump the version), applies it, and commits with a natural,
human-style message. Designed to run on a schedule via GitHub Actions.

Env vars:
  AUTO_FORCE=1   always commit at least once (skips the "day off" dice roll)
  AUTO_MAX_SLEEP seconds of random start delay (default 600, set 0 for local runs)
"""

from __future__ import annotations

import os
import random
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "pykit"
TESTS = ROOT / "tests" / "test_pykit.py"
CHANGELOG = ROOT / "CHANGELOG.md"
INIT = SRC / "__init__.py"

# ---------------------------------------------------------------------------
# Snippet bank: real, working helpers that get added over time.
# Each entry: module, name, imports, code, test, messages.
# "alt" is an equivalent implementation used for refactor commits.
# ---------------------------------------------------------------------------

SNIPPETS = [
    {
        "module": "strings",
        "name": "slugify",
        "imports": ["import re"],
        "code": '''def slugify(text: str) -> str:
    """Convert text to a url-friendly slug."""
    text = re.sub(r"[^\\w\\s-]", "", text.lower())
    return re.sub(r"[-\\s]+", "-", text).strip("-")
''',
        "test": '''def test_slugify():
    from pykit.strings import slugify
    assert slugify("Hello, World!") == "hello-world"
''',
        "messages": [
            "add slugify helper",
            "strings: add slugify",
            "add slugify util for url slugs",
        ],
    },
    {
        "module": "strings",
        "name": "camel_to_snake",
        "imports": ["import re"],
        "code": '''def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s1).lower()
''',
        "test": '''def test_camel_to_snake():
    from pykit.strings import camel_to_snake
    assert camel_to_snake("someVarName") == "some_var_name"
''',
        "messages": [
            "add camel_to_snake converter",
            "strings: camelCase to snake_case helper",
        ],
    },
    {
        "module": "strings",
        "name": "mask",
        "imports": [],
        "code": '''def mask(text: str, visible: int = 4, char: str = "*") -> str:
    """Mask all but the last `visible` characters."""
    if len(text) <= visible:
        return text
    return char * (len(text) - visible) + text[-visible:]
''',
        "test": '''def test_mask():
    from pykit.strings import mask
    assert mask("1234567890") == "******7890"
''',
        "messages": [
            "add mask helper for sensitive strings",
            "add string masking util",
        ],
    },
    {
        "module": "strings",
        "name": "initials",
        "imports": [],
        "code": '''def initials(name: str, limit: int = 2) -> str:
    """Get uppercase initials from a full name."""
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:limit])
''',
        "alt": '''def initials(name: str, limit: int = 2) -> str:
    """Get uppercase initials from a full name."""
    parts = name.split()
    letters = [p[0].upper() for p in parts if p]
    return "".join(letters[:limit])
''',
        "test": '''def test_initials():
    from pykit.strings import initials
    assert initials("john doe") == "JD"
''',
        "messages": ["add initials helper", "strings: initials()"],
        "refactor_messages": ["simplify initials()", "clean up initials helper"],
    },
    {
        "module": "strings",
        "name": "pluralize",
        "imports": [],
        "code": '''def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return '1 item' / '2 items' style strings."""
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"
''',
        "test": '''def test_pluralize():
    from pykit.strings import pluralize
    assert pluralize(1, "item") == "1 item"
    assert pluralize(3, "item") == "3 items"
''',
        "messages": ["add pluralize helper", "add simple pluralize()"],
    },
    {
        "module": "dates",
        "name": "humanize_delta",
        "imports": [],
        "code": '''def humanize_delta(seconds: int) -> str:
    """Turn a duration in seconds into a rough human string."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"
''',
        "test": '''def test_humanize_delta():
    from pykit.dates import humanize_delta
    assert humanize_delta(30) == "30s"
    assert humanize_delta(7200) == "2h"
''',
        "messages": [
            "add humanize_delta for durations",
            "dates: human readable durations",
        ],
    },
    {
        "module": "dates",
        "name": "start_of_day",
        "imports": [],
        "code": '''def start_of_day(dt: datetime) -> datetime:
    """Return the datetime at 00:00:00 of the same day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)
''',
        "test": '''def test_start_of_day():
    from datetime import datetime
    from pykit.dates import start_of_day
    d = start_of_day(datetime(2024, 3, 5, 14, 30))
    assert (d.hour, d.minute) == (0, 0)
''',
        "messages": ["add start_of_day helper", "dates: start_of_day()"],
    },
    {
        "module": "dates",
        "name": "days_between",
        "imports": [],
        "code": '''def days_between(a: date, b: date) -> int:
    """Absolute number of days between two dates."""
    return abs((b - a).days)
''',
        "test": '''def test_days_between():
    from datetime import date
    from pykit.dates import days_between
    assert days_between(date(2024, 1, 1), date(2024, 1, 11)) == 10
''',
        "messages": ["add days_between", "dates: add days_between helper"],
    },
    {
        "module": "collections",
        "name": "chunk",
        "imports": [],
        "code": '''def chunk(items: list, size: int) -> list[list]:
    """Split a list into chunks of at most `size` items."""
    return [items[i : i + size] for i in range(0, len(items), size)]
''',
        "test": '''def test_chunk():
    from pykit.collections import chunk
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
''',
        "messages": ["add chunk helper", "collections: chunk()"],
    },
    {
        "module": "collections",
        "name": "unique",
        "imports": [],
        "code": '''def unique(items: Iterable[Any]) -> list:
    """Deduplicate while preserving order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
''',
        "alt": '''def unique(items: Iterable[Any]) -> list:
    """Deduplicate while preserving order."""
    return list(dict.fromkeys(items))
''',
        "test": '''def test_unique():
    from pykit.collections import unique
    assert unique([1, 2, 1, 3, 2]) == [1, 2, 3]
''',
        "messages": ["add ordered unique()", "collections: add unique helper"],
        "refactor_messages": [
            "simplify unique() using dict.fromkeys",
            "refactor unique implementation",
        ],
    },
    {
        "module": "collections",
        "name": "flatten",
        "imports": [],
        "code": '''def flatten(nested: Iterable[Iterable[Any]]) -> list:
    """Flatten one level of nesting."""
    return [x for sub in nested for x in sub]
''',
        "test": '''def test_flatten():
    from pykit.collections import flatten
    assert flatten([[1, 2], [3]]) == [1, 2, 3]
''',
        "messages": ["add flatten helper", "collections: flatten one level"],
    },
    {
        "module": "collections",
        "name": "group_by",
        "imports": [],
        "code": '''def group_by(items: Iterable[Any], key) -> dict:
    """Group items into a dict by key function."""
    out: dict = {}
    for item in items:
        out.setdefault(key(item), []).append(item)
    return out
''',
        "test": '''def test_group_by():
    from pykit.collections import group_by
    got = group_by(["ant", "bee", "asp"], key=lambda w: w[0])
    assert got == {"a": ["ant", "asp"], "b": ["bee"]}
''',
        "messages": ["add group_by helper", "collections: group_by()"],
    },
    {
        "module": "collections",
        "name": "pick",
        "imports": [],
        "code": '''def pick(d: dict, keys: Iterable[Any]) -> dict:
    """Return a dict with only the given keys (if present)."""
    return {k: d[k] for k in keys if k in d}
''',
        "test": '''def test_pick():
    from pykit.collections import pick
    assert pick({"a": 1, "b": 2}, ["a", "c"]) == {"a": 1}
''',
        "messages": ["add pick() for dicts", "collections: add pick helper"],
    },
    {
        "module": "numbers",
        "name": "human_size",
        "imports": [],
        "code": '''def human_size(num_bytes: float) -> str:
    """Format bytes as a human readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"
''',
        "test": '''def test_human_size():
    from pykit.numbers import human_size
    assert human_size(2048) == "2.0 KB"
''',
        "messages": ["add human_size formatter", "numbers: human readable sizes"],
    },
    {
        "module": "numbers",
        "name": "percent",
        "imports": [],
        "code": '''def percent(part: float, whole: float, digits: int = 1) -> float:
    """Percentage of part in whole, safe against division by zero."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, digits)
''',
        "test": '''def test_percent():
    from pykit.numbers import percent
    assert percent(1, 4) == 25.0
    assert percent(1, 0) == 0.0
''',
        "messages": ["add percent helper", "numbers: safe percent()"],
    },
    {
        "module": "numbers",
        "name": "ordinal",
        "imports": [],
        "code": '''def ordinal(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 11 -> 11th, etc."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
''',
        "test": '''def test_ordinal():
    from pykit.numbers import ordinal
    assert ordinal(1) == "1st"
    assert ordinal(11) == "11th"
    assert ordinal(23) == "23rd"
''',
        "messages": ["add ordinal formatter", "numbers: add ordinal()"],
    },
    {
        "module": "numbers",
        "name": "lerp",
        "imports": [],
        "code": '''def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t
''',
        "test": '''def test_lerp():
    from pykit.numbers import lerp
    assert lerp(0, 10, 0.5) == 5
''',
        "messages": ["add lerp", "numbers: linear interpolation helper"],
    },
]

CHANGELOG_NOTES = [
    "- improve type hints in {module}",
    "- add `{name}` to {module}",
    "- minor docstring cleanups",
    "- small internal cleanups",
    "- expand test coverage",
]

CHANGELOG_MESSAGES = [
    "update changelog",
    "changelog",
    "docs: update changelog",
    "note recent changes in changelog",
]

BUMP_MESSAGES = [
    "bump version to {v}",
    "release {v}",
    "v{v}",
]


def run(*args: str) -> str:
    res = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def commit(message: str) -> None:
    run("git", "add", "-A")
    run("git", "commit", "-m", message)
    print(f"committed: {message}")


def module_path(module: str) -> Path:
    return SRC / f"{module}.py"


def ensure_imports(text: str, imports: list[str]) -> str:
    lines = text.split("\n")
    for imp in imports:
        if imp not in text:
            lines.insert(1, imp)
    return "\n".join(lines)


def add_function(snippet: dict) -> None:
    path = module_path(snippet["module"])
    text = ensure_imports(path.read_text(), snippet.get("imports", []))
    text = text.rstrip("\n") + "\n\n\n" + snippet["code"]
    path.write_text(text)
    commit(random.choice(snippet["messages"]))

    # usually the test lands in the same session, sometimes as its own commit
    if snippet.get("test"):
        tests = TESTS.read_text().rstrip("\n")
        TESTS.write_text(tests + "\n\n\n" + snippet["test"])
        if random.random() < 0.5:
            run("git", "add", "-A")
            run("git", "commit", "--amend", "--no-edit")
        else:
            commit(
                random.choice(
                    [
                        f"add test for {snippet['name']}",
                        f"tests: cover {snippet['name']}",
                        "add missing test",
                    ]
                )
            )


def refactor_function(snippet: dict) -> bool:
    path = module_path(snippet["module"])
    text = path.read_text()
    if snippet["code"] in text:
        path.write_text(text.replace(snippet["code"], snippet["alt"]))
    elif snippet["alt"] in text:
        path.write_text(text.replace(snippet["alt"], snippet["code"]))
    else:
        return False
    commit(random.choice(snippet["refactor_messages"]))
    return True


def update_changelog() -> None:
    text = CHANGELOG.read_text()
    added = [s for s in SNIPPETS if is_added(s)]
    template = random.choice(CHANGELOG_NOTES)
    if "{name}" in template and not added:
        template = "- small internal cleanups"
    pick_snip = random.choice(added) if added else {"name": "", "module": ""}
    line = template.format(name=pick_snip["name"], module=pick_snip["module"])
    if line in text:
        line = "- misc fixes"
    text = text.replace("## Unreleased\n", f"## Unreleased\n\n{line}\n", 1).replace(
        "\n\n\n", "\n\n"
    )
    CHANGELOG.write_text(text)
    commit(random.choice(CHANGELOG_MESSAGES))


def bump_version() -> None:
    text = INIT.read_text()
    version = text.split('"')[1]
    major, minor, patch = version.split(".")
    new = f"{major}.{minor}.{int(patch) + 1}"
    INIT.write_text(text.replace(version, new))
    CHANGELOG.write_text(
        CHANGELOG.read_text().replace(
            "## Unreleased\n", f"## Unreleased\n\n## {new}\n", 1
        )
    )
    commit(random.choice(BUMP_MESSAGES).format(v=new))


def is_added(snippet: dict) -> bool:
    return f"def {snippet['name']}(" in module_path(snippet["module"]).read_text()


def do_one_change() -> None:
    pending = [s for s in SNIPPETS if not is_added(s)]
    refactorable = [s for s in SNIPPETS if s.get("alt") and is_added(s)]

    choices: list[tuple[str, float]] = []
    if pending:
        choices.append(("add", 0.62))
    if refactorable:
        choices.append(("refactor", 0.12))
    choices.append(("changelog", 0.18))
    if random.random() < 0.05:
        choices.append(("bump", 0.4))

    action = random.choices([c[0] for c in choices], [c[1] for c in choices])[0]
    if action == "add":
        add_function(random.choice(pending))
    elif action == "refactor":
        if not refactor_function(random.choice(refactorable)):
            update_changelog()
    elif action == "bump":
        bump_version()
    else:
        update_changelog()


def daily_target() -> int:
    """How many commits today, 0-9. Seeded by the date so every
    scheduled run that day agrees on the same target."""
    today = date.today()
    rng = random.Random(today.isoformat())
    if today.weekday() >= 5:  # weekends are quieter, often off
        return rng.choices([0, 1, 2, 3, 4], [0.35, 0.25, 0.20, 0.12, 0.08])[0]
    return rng.choices(
        range(9),
        [0.08, 0.10, 0.16, 0.18, 0.16, 0.13, 0.09, 0.06, 0.04],
    )[0]


def commits_today() -> int:
    out = run("git", "log", "--since=midnight", "--oneline")
    return len(out.splitlines()) if out else 0


def main() -> int:
    force = os.environ.get("AUTO_FORCE") == "1"
    max_sleep = int(os.environ.get("AUTO_MAX_SLEEP", "600"))

    target = daily_target()
    done = commits_today()
    remaining = target - done
    if remaining <= 0:
        if not force:
            print(f"daily target reached ({done}/{target}), skipping")
            return 0
        remaining = 1

    if max_sleep:
        delay = random.randint(0, max_sleep)
        print(f"start delay: {delay}s")
        time.sleep(delay)

    n_commits = min(remaining, random.choices([1, 2, 3], [0.5, 0.3, 0.2])[0])
    print(f"making {n_commits} commit(s), daily {done}/{target}")
    for i in range(n_commits):
        do_one_change()
        if i < n_commits - 1 and max_sleep:
            time.sleep(random.randint(45, 240))
    return 0


if __name__ == "__main__":
    sys.exit(main())
