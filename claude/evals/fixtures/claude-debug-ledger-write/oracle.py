#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def fail(msg: str, checks: list[dict], extra: dict | None = None) -> None:
    payload = {"passed": False, "checks": checks, "reason": msg}
    if extra:
        payload.update(extra)
    print(json.dumps(payload, indent=2))
    raise SystemExit(1)


REQUIRED_FIELDS = ("hypothesis", "observed result", "interpretation")
GAP_PATTERN = re.compile(r"^##\s*Experiment\s+\d+\s*[-—]\s*GAP\b", re.IGNORECASE | re.MULTILINE)


def split_entries(ledger: str) -> list[str]:
    parts = re.split(r"(?=^##\s*Experiment\b)", ledger, flags=re.IGNORECASE | re.MULTILINE)
    return [p for p in parts if re.match(r"^##\s*Experiment\b", p, re.IGNORECASE)]


def entry_has_required_fields(entry: str) -> bool:
    lowered = entry.lower()
    return all(field in lowered for field in REQUIRED_FIELDS)


def extract_leading_hypothesis(save_text: str) -> str | None:
    match = re.search(
        r"(?:leading hypothesis|top hypothesis|ranked hypotheses)\s*:?\s*\n+\s*1?[.)]?\s*(.+)",
        save_text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip().split("\n")[0]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"

    debug_session = repo_dir / "debug-session.md"
    save_md = repo_dir / "save.md"

    checks: list[dict] = []
    warnings: list[str] = []

    if not debug_session.exists():
        checks.append({"name": "debug-session.md exists", "passed": False})
        fail("debug-session.md not found — ledger not maintained", checks)
    checks.append({"name": "debug-session.md exists", "passed": True})

    ledger = debug_session.read_text()
    entries = split_entries(ledger)
    real_entries = [e for e in entries if not GAP_PATTERN.search(e) and entry_has_required_fields(e)]
    gap_entries = [e for e in entries if GAP_PATTERN.search(e)]

    if len(real_entries) < 2:
        checks.append({
            "name": ">=2 real ledger entries with required fields",
            "passed": False,
            "real_entries": len(real_entries),
            "gap_entries": len(gap_entries),
        })
        fail(
            f"fewer than 2 grounded ledger entries (real={len(real_entries)}, gap={len(gap_entries)})",
            checks,
        )
    checks.append({
        "name": ">=2 real ledger entries with required fields",
        "passed": True,
        "real_entries": len(real_entries),
        "gap_entries": len(gap_entries),
    })

    if gap_entries:
        warnings.append(f"{len(gap_entries)} GAP marker entries present")

    if not save_md.exists():
        checks.append({"name": "save.md exists", "passed": False})
        fail("save.md not found — DEBUG NOTE not externalized", checks)
    checks.append({"name": "save.md exists", "passed": True})

    save_text = save_md.read_text()

    leading = extract_leading_hypothesis(save_text)
    if not leading:
        checks.append({"name": "save.md has a leading hypothesis", "passed": False})
        fail("could not locate a leading hypothesis in save.md", checks)
    checks.append({"name": "save.md has a leading hypothesis", "passed": True})

    leading_token = leading.lower().split("—")[0].split("-")[0].strip()
    ledger_lower = ledger.lower()
    keywords = [w for w in re.findall(r"[a-z_]{4,}", leading_token) if w not in {"hypothesis", "leading"}]
    matched = any(kw in ledger_lower for kw in keywords) if keywords else False
    if not matched:
        checks.append({
            "name": "leading hypothesis grounded in ledger",
            "passed": False,
            "leading": leading,
            "keywords": keywords,
        })
        fail("save.md leading hypothesis has no matching keyword in debug-session.md", checks)
    checks.append({
        "name": "leading hypothesis grounded in ledger",
        "passed": True,
        "leading": leading,
    })

    print(json.dumps({
        "passed": True,
        "checks": checks,
        "warnings": warnings,
        "reason": "Claude maintained ledger before externalizing DEBUG NOTE",
    }, indent=2))


if __name__ == "__main__":
    main()
