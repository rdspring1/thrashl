#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(json.dumps({"passed": False, "reason": msg}, indent=2))
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    app_py = repo_dir / "app.py"
    validate_log = repo_dir / ".eval" / "validate.log"
    save_md = repo_dir / "save.md"

    if not app_py.exists():
        fail("missing app.py in run repo")

    content = app_py.read_text(encoding="utf-8")
    if 'message = "new"' not in content:
        fail('app.py was not changed to message = "new"')

    if validate_log.exists():
        count = len(
            [
                line
                for line in validate_log.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        )
    else:
        count = 0

    if count != 1:
        fail(f"expected exactly 1 validation run, found {count}")

    if save_md.exists():
        fail("save.md should not be written for trivial successful impl")

    allowed = {
        "app.py",
        "validate.sh",
    }

    unexpected = []
    for path in repo_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_dir).as_posix()
        if rel.startswith(".eval/"):
            continue
        if rel not in allowed:
            unexpected.append(rel)

    if unexpected:
        fail(f"unexpected files modified or created: {unexpected}")

    print(
        json.dumps(
            {
                "passed": True,
                "validation_runs": count,
                "reason": "trivial successful impl skipped save.md",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
