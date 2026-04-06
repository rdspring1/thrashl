#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(msg: str, checks: list[dict]) -> None:
    print(json.dumps({"passed": False, "checks": checks, "reason": msg}, indent=2))
    raise SystemExit(1)


def check_routing(
    save_file: Path,
    correct_skill: str,
    wrong_skills: list[str],
    case_name: str,
    checks: list[dict],
) -> None:
    label = save_file.name

    # exists
    if not save_file.exists():
        checks.append({"name": f"{label} exists", "passed": False})
        fail(f"{case_name}: {label} not found", checks)
    checks.append({"name": f"{label} exists", "passed": True})

    text = save_file.read_text()

    # correct skill selected
    if correct_skill not in text:
        checks.append({"name": f"{label}: correct skill ({correct_skill})", "passed": False})
        fail(f"{case_name}: {correct_skill} not selected in {label}", checks)
    checks.append({"name": f"{label}: correct skill ({correct_skill})", "passed": True})

    # wrong skills absent — one check per wrong skill
    for wrong_skill in wrong_skills:
        if wrong_skill in text:
            checks.append({"name": f"{label}: wrong skill absent ({wrong_skill})", "passed": False})
            fail(f"{case_name}: {wrong_skill} present in {label} — wrong lane or tool spray", checks)
        checks.append({"name": f"{label}: wrong skill absent ({wrong_skill})", "passed": True})

    # no tool spraying (correct skill + any wrong skill in same document)
    wrong_in_doc = [s for s in wrong_skills if s in text]
    if correct_skill in text and wrong_in_doc:
        checks.append({"name": f"{label}: no tool spray", "passed": False})
        fail(f"{case_name}: {wrong_in_doc} also present in {label} — tool spray detected", checks)
    checks.append({"name": f"{label}: no tool spray", "passed": True})


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    checks: list[dict] = []

    check_routing(
        save_file=repo_dir / "framework-save.md",
        correct_skill="pytorch-profiler-trace",
        wrong_skills=["nsys-trace-profiler"],
        case_name="framework-profiler-case",
        checks=checks,
    )

    check_routing(
        save_file=repo_dir / "system-save.md",
        correct_skill="nsys-trace-profiler",
        wrong_skills=["pytorch-profiler-trace"],
        case_name="system-profiler-case",
        checks=checks,
    )

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "reason": "both profiler cases routed to correct skill with no tool spray"
    }, indent=2))


if __name__ == "__main__":
    main()
