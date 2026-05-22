#!/usr/bin/env python3
from __future__ import annotations

import ast
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

EXPECTED_SCOPE = {"tests/test_currency.py"}


def collect_defs(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def count_refs(name: str, files: list[Path]) -> int:
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    refs = 0
    for f in files:
        text = f.read_text()
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(("def ", "async def ", "class ")):
                continue
            refs += len(pattern.findall(line))
    return refs


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    tests_dir = repo_dir / "tests"
    test_currency = tests_dir / "test_currency.py"
    conftest = tests_dir / "conftest.py"
    baseline_dir = repo_dir / ".baseline"
    baseline_conftest = baseline_dir / "tests" / "conftest.py"
    save_md = repo_dir / "save.md"

    checks: list[dict] = []
    warnings: list[str] = []

    save_text = save_md.read_text().lower() if save_md.exists() else ""
    surgical_justified = "surgical simplicity" in save_text

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

    bloat_hits: list[tuple[str, str]] = []
    for py in sorted(tests_dir.rglob("*.py")):
        rel = py.relative_to(repo_dir).as_posix()
        text = py.read_text()
        for pat in BLOAT_PATTERNS:
            if pat.search(text):
                bloat_hits.append((rel, pat.pattern))
    if bloat_hits:
        if not surgical_justified:
            checks.append({
                "name": "no unjustified mocking / monkeypatch in tests/",
                "passed": False,
                "hits": bloat_hits,
            })
            fail(
                f"mocking introduced without Surgical Simplicity justification in save.md: {bloat_hits}",
                checks,
            )
        warnings.append(f"mocking present but justified in save.md: {bloat_hits}")
    checks.append({
        "name": "no unjustified mocking / monkeypatch in tests/",
        "passed": True,
    })

    if not baseline_conftest.exists():
        checks.append({"name": "baseline conftest.py available", "passed": False})
        fail(".baseline/tests/conftest.py missing — fixture broken", checks)
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

    out_of_scope: list[str] = []
    for py in sorted(repo_dir.rglob("*.py")):
        if baseline_dir in py.parents:
            continue
        rel = py.relative_to(repo_dir).as_posix()
        baseline_equiv = baseline_dir / rel
        if not baseline_equiv.exists():
            if rel in EXPECTED_SCOPE:
                continue
            out_of_scope.append(rel)
            continue
        if py.read_bytes() == baseline_equiv.read_bytes():
            continue
        if rel in EXPECTED_SCOPE:
            continue
        out_of_scope.append(rel)
    if out_of_scope:
        path_justified = surgical_justified and all(
            p.lower() in save_text for p in out_of_scope
        )
        if not path_justified:
            checks.append({
                "name": "no edits outside declared scope fence",
                "passed": False,
                "out_of_scope": out_of_scope,
                "expected_scope": sorted(EXPECTED_SCOPE),
            })
            fail(
                f"edits to files outside scope fence without Surgical Simplicity justification: {out_of_scope}",
                checks,
            )
        warnings.append(
            f"out-of-scope edits present but justified in save.md: {out_of_scope}"
        )
    checks.append({
        "name": "no edits outside declared scope fence",
        "passed": True,
    })

    src_files = [
        p for p in repo_dir.rglob("*.py")
        if baseline_dir not in p.parents
        and tests_dir not in p.parents
        and p.name != "conftest.py"
    ]
    single_use: list[str] = []
    for py in src_files:
        rel = py.relative_to(repo_dir).as_posix()
        baseline_equiv = baseline_dir / rel
        current_defs = collect_defs(py.read_text())
        baseline_defs = (
            collect_defs(baseline_equiv.read_text())
            if baseline_equiv.exists() else set()
        )
        new_defs = current_defs - baseline_defs
        if not new_defs:
            continue
        ref_files = [
            p for p in repo_dir.rglob("*.py") if baseline_dir not in p.parents
        ]
        for name in sorted(new_defs):
            refs = count_refs(name, ref_files)
            if refs <= 1:
                single_use.append(f"{rel}:{name} (refs={refs})")
    if single_use:
        if not surgical_justified:
            checks.append({
                "name": "no single-use helpers in src",
                "passed": False,
                "single_use": single_use,
            })
            fail(
                f"new helpers with one or fewer callsites without Surgical Simplicity justification: {single_use}",
                checks,
            )
        warnings.append(
            f"single-use helpers present but justified in save.md: {single_use}"
        )
    checks.append({"name": "no single-use helpers in src", "passed": True})

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "warnings": warnings,
        "reason": "Claude extended existing test in place without bloat or scope drift",
    }, indent=2))


if __name__ == "__main__":
    main()
