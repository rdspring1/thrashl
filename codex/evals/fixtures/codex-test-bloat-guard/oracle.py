#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def fail(msg: str, checks: list[dict]) -> None:
    print(json.dumps({"passed": False, "checks": checks, "reason": msg}, indent=2))
    raise SystemExit(1)


BLOAT_PATTERNS = (
    re.compile(r"\bMagicMock\b"),
    re.compile(r"\bmonkeypatch\.setattr\b"),
    re.compile(r"\bmocker\."),
    re.compile(r"\bunittest\.mock\b"),
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    tests_dir = repo_dir / "tests"
    test_currency = tests_dir / "test_currency.py"
    conftest = tests_dir / "conftest.py"
    baseline_conftest = repo_dir / ".baseline" / "conftest.py"
    save_md = repo_dir / "save.md"

    checks: list[dict] = []
    warnings: list[str] = []

    # 1. No new .py file under tests/ (only the original two are allowed)
    allowed = {"test_currency.py", "conftest.py", "__init__.py"}
    extra = sorted(
        p.name for p in tests_dir.iterdir()
        if p.is_file() and p.suffix == ".py" and p.name not in allowed
    )
    if extra:
        checks.append({
            "name": "no new test files under tests/",
            "passed": False,
            "unexpected": extra,
        })
        fail(
            f"new test files created instead of extending existing test: {extra}",
            checks,
        )
    checks.append({"name": "no new test files under tests/", "passed": True})

    # 2. test_currency.py extended with the empty-string case
    if not test_currency.exists():
        checks.append({"name": "test_currency.py present", "passed": False})
        fail("test_currency.py is missing", checks)
    test_text = test_currency.read_text()
    test_lower = test_text.lower()
    mentions_empty = '""' in test_text or "''" in test_text or "empty" in test_lower
    raises_value_error = "valueerror" in test_lower or "pytest.raises" in test_lower
    if not (mentions_empty and raises_value_error):
        checks.append({
            "name": "existing test extended with empty-string ValueError case",
            "passed": False,
            "mentions_empty": mentions_empty,
            "raises_value_error": raises_value_error,
        })
        fail(
            "test_currency.py does not appear to cover empty-string ValueError",
            checks,
        )
    checks.append({
        "name": "existing test extended with empty-string ValueError case",
        "passed": True,
    })

    # 3. No mocking / monkeypatch introduced (or justified in save.md)
    bloat_hits: list[tuple[str, str]] = []
    for py in sorted(tests_dir.rglob("*.py")):
        rel = py.relative_to(repo_dir).as_posix()
        text = py.read_text()
        for pat in BLOAT_PATTERNS:
            if pat.search(text):
                bloat_hits.append((rel, pat.pattern))
    if bloat_hits:
        justified = False
        if save_md.exists():
            save_text = save_md.read_text().lower()
            justified = "test economy" in save_text
        if not justified:
            checks.append({
                "name": "no unjustified mocking / monkeypatch in tests/",
                "passed": False,
                "hits": bloat_hits,
            })
            fail(
                f"mocking introduced without Test Economy justification in save.md: {bloat_hits}",
                checks,
            )
        warnings.append(f"mocking present but justified in save.md: {bloat_hits}")
    checks.append({
        "name": "no unjustified mocking / monkeypatch in tests/",
        "passed": True,
    })

    # 4. conftest.py unchanged from baseline
    if not baseline_conftest.exists():
        checks.append({"name": "baseline conftest.py available", "passed": False})
        fail(".baseline/conftest.py missing — fixture broken", checks)
    if not conftest.exists():
        checks.append({"name": "conftest.py present", "passed": False})
        fail("tests/conftest.py was deleted", checks)
    if conftest.read_bytes() != baseline_conftest.read_bytes():
        checks.append({
            "name": "conftest.py unchanged from baseline",
            "passed": False,
        })
        fail(
            "tests/conftest.py was modified — defensive fixture scaffolding added",
            checks,
        )
    checks.append({
        "name": "conftest.py unchanged from baseline",
        "passed": True,
    })

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "warnings": warnings,
        "reason": "Codex extended existing test in place without bloat",
    }, indent=2))


if __name__ == "__main__":
    main()
