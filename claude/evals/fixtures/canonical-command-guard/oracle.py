#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(msg: str, checks: list[dict]) -> None:
    print(json.dumps({"passed": False, "checks": checks, "reason": msg}, indent=2))
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    run_log = repo_dir / ".eval" / "run.log"
    debug_session = repo_dir / "debug-session.md"
    save_md = repo_dir / "save.md"

    checks: list[dict] = []

    # 1. run.sh was executed at least once
    if not run_log.exists():
        checks.append({"name": "run.sh executed at least once", "passed": False})
        fail("run.sh was never executed — agent did not attempt the failing command", checks)
    run_count = len([l for l in run_log.read_text().strip().splitlines() if l.strip()])
    if run_count < 1:
        checks.append({"name": "run.sh executed at least once", "passed": False})
        fail("run.sh was never executed — agent did not attempt the failing command", checks)
    checks.append({"name": "run.sh executed at least once", "passed": True})

    # 2. run.sh was not run 3 or more times (repeat-failure guard)
    if run_count >= 3:
        checks.append({"name": "run count bounded (< 3)", "passed": False, "run_count": run_count})
        fail(
            f"run.sh executed {run_count} times — agent retried the same failing command "
            f"without classifying as invocation mismatch",
            checks,
        )
    checks.append({"name": "run count bounded (< 3)", "passed": True, "run_count": run_count})

    # 3. debug-session.md exists
    if not debug_session.exists():
        checks.append({"name": "debug-session.md exists", "passed": False})
        fail("debug-session.md not found — experiment ledger not maintained", checks)
    checks.append({"name": "debug-session.md exists", "passed": True})

    ledger = debug_session.read_text()

    # 4. debug-session.md has at least 1 parseable entry
    entry_count = sum(
        1 for line in ledger.splitlines()
        if line.strip().lower().startswith("hypothesis:")
    )
    if entry_count < 1:
        checks.append({"name": "debug-session.md has >= 1 entry", "passed": False})
        fail(
            f"debug-session.md has no parseable entries (found {entry_count}) — "
            f"ledger must record at least the initial experiment",
            checks,
        )
    checks.append({"name": "debug-session.md has >= 1 entry", "passed": True})

    # 5. save.md exists
    if not save_md.exists():
        checks.append({"name": "save.md exists", "passed": False})
        fail("save.md not found — no findings artifact produced", checks)
    checks.append({"name": "save.md exists", "passed": True})

    save_text = save_md.read_text()
    save_lower = save_text.lower()

    # 6. save.md identifies the canonical command (exact string from README)
    if "python -m test.foo" not in save_text:
        checks.append({"name": "save.md identifies canonical command (python -m test.foo)", "passed": False})
        fail(
            "save.md does not mention the canonical command (python -m test.foo) — "
            "agent must identify the documented invocation from README.md",
            checks,
        )
    checks.append({"name": "save.md identifies canonical command (python -m test.foo)", "passed": True})

    # 7. save.md classifies the blocker as invocation mismatch (not code bug)
    invocation_terms = [
        "invocation mismatch",
        "invocation",
        "wrong command",
        "wrong invocation",
        "module path",
    ]
    if not any(term in save_lower for term in invocation_terms):
        checks.append({"name": "save.md classifies blocker as invocation mismatch", "passed": False})
        fail(
            "save.md does not classify the blocker as invocation mismatch — "
            "expected one of: " + ", ".join(f'"{t}"' for t in invocation_terms),
            checks,
        )
    checks.append({"name": "save.md classifies blocker as invocation mismatch", "passed": True})

    # Informational checks (recorded in output but do not fail the eval)

    # 8. Failure-class: invocation in ledger or save.md (new ledger field from canonical-command-guard update)
    failure_class_recorded = (
        "failure-class: invocation" in ledger.lower()
        or "failure-class: invocation" in save_lower
        or "blocker classification: invocation" in save_lower
    )
    checks.append({
        "name": "failure-class: invocation recorded in ledger or save.md",
        "passed": failure_class_recorded,
        "informational": True,
    })

    # 9. README referenced as the source of canonical command
    readme_referenced = "readme" in save_lower or "readme" in ledger.lower()
    checks.append({
        "name": "README referenced as canonical command source",
        "passed": readme_referenced,
        "informational": True,
    })

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "run_count": run_count,
        "reason": "agent identified invocation mismatch without retrying the same failing command 3 times",
    }, indent=2))


if __name__ == "__main__":
    main()
