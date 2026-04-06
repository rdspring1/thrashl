#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
RUNS = ROOT / "runs"
RESULTS = ROOT / "results"


def prepare_case(case_name: str) -> None:
    fixture = FIXTURES / case_name
    if not fixture.exists():
        raise SystemExit(f"unknown case: {case_name}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{case_name}"
    run_dir = RUNS / run_id
    repo_src = fixture / "repo"
    repo_dst = run_dir / "repo"

    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copytree(repo_src, repo_dst)

    spec_src = fixture / "SPEC.md"
    spec_dst = run_dir / "SPEC.md"
    shutil.copy2(spec_src, spec_dst)

    print(f"Prepared run: {run_dir}")
    print()
    print("Next steps:")
    print(f"  1. cd {repo_dst}")
    print("  2. Open Claude in that repo")
    print("  3. Follow the task in ../SPEC.md using /impl")
    print(f"  4. Score with: python3 evals/runner.py score {run_dir}")


def score_case(run_dir_str: str) -> None:
    run_dir = Path(run_dir_str).resolve()
    spec_name = run_dir.name.split("-", 2)[-1]
    fixture = FIXTURES / spec_name
    oracle = fixture / "oracle.py"

    if not oracle.exists():
        raise SystemExit(f"missing oracle for fixture: {fixture}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS / f"{run_dir.name}.json"

    proc = subprocess.run(
        [sys.executable, str(oracle), str(run_dir)],
        capture_output=True,
        text=True,
    )

    output = proc.stdout if proc.stdout else proc.stderr
    result_path.write_text(output)

    print(output.strip())
    print()
    print(f"Saved result to {result_path}")

    raise SystemExit(proc.returncode)


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: runner.py prepare <case> | score <run_dir>")

    cmd = sys.argv[1]

    if cmd == "prepare":
        prepare_case(sys.argv[2])
    elif cmd == "score":
        score_case(sys.argv[2])
    else:
        raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
