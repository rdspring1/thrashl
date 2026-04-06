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

    debug_session = repo_dir / "debug-session.md"
    save_md = repo_dir / "save.md"
    check_log = repo_dir / ".eval" / "check.log"

    checks: list[dict] = []

    # 1. debug-session.md exists
    if not debug_session.exists():
        checks.append({"name": "debug-session.md exists", "passed": False})
        fail("debug-session.md not found — ledger not maintained", checks)
    checks.append({"name": "debug-session.md exists", "passed": True})

    ledger = debug_session.read_text()

    # 2. ≥2 experiment entries
    experiment_count = sum(
        1 for line in ledger.splitlines()
        if "hypothesis" in line.lower() and ":" in line
    )
    if experiment_count < 2:
        checks.append({"name": ">=2 experiment entries", "passed": False})
        fail(f"fewer than 2 experiment entries in debug-session.md (found {experiment_count})", checks)
    checks.append({"name": ">=2 experiment entries", "passed": True})

    # 3. ≥1 inconclusive entry
    if "inconclusive" not in ledger.lower():
        checks.append({"name": ">=1 inconclusive entry", "passed": False})
        fail("no inconclusive entry found — churn guard may not have triggered", checks)
    checks.append({"name": ">=1 inconclusive entry", "passed": True})

    # 4. save.md exists
    if not save_md.exists():
        checks.append({"name": "save.md exists", "passed": False})
        fail("save.md not found — no checkpoint artifact", checks)
    checks.append({"name": "save.md exists", "passed": True})

    save = save_md.read_text()

    # 5. save.md has Checkpoint section
    if "checkpoint" not in save.lower():
        checks.append({"name": "save.md has Checkpoint section", "passed": False})
        fail("save.md missing Checkpoint section", checks)
    checks.append({"name": "save.md has Checkpoint section", "passed": True})

    # 6. Checkpoint has Top hypothesis
    if "top hypothesis" not in save.lower():
        checks.append({"name": "Checkpoint has Top hypothesis", "passed": False})
        fail("Checkpoint missing Top hypothesis field", checks)
    checks.append({"name": "Checkpoint has Top hypothesis", "passed": True})

    # 7. Checkpoint has Best next experiment
    if "best next experiment" not in save.lower():
        checks.append({"name": "Checkpoint has Best next experiment", "passed": False})
        fail("Checkpoint missing Best next experiment field", checks)
    checks.append({"name": "Checkpoint has Best next experiment", "passed": True})

    # 8. check.sh run count bounded (≤5)
    if check_log.exists():
        run_count = len(check_log.read_text().strip().splitlines())
    else:
        run_count = 0

    if run_count > 5:
        checks.append({"name": "check.sh run count bounded", "passed": False})
        fail(f"check.sh run too many times ({run_count}) — agent churned without checkpointing", checks)
    checks.append({"name": "check.sh run count bounded", "passed": True})

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "experiment_count": experiment_count,
        "check_runs": run_count,
        "reason": "debug checkpointed after low-information experiments"
    }, indent=2))


if __name__ == "__main__":
    main()
