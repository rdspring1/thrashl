#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = (
    "### Review scope",
    "### Checklist",
    "### Findings",
    "### Test economy",
    "### Diff economy",
    "### Verification",
    "### Summary",
    "### Best next mode",
)

BLOCKING_TAG = re.compile(r"\[BLOCKING\s*/\s*(HIGH|MEDIUM|LOW-MEDIUM)\]", re.IGNORECASE)
NON_BLOCKING_TAG = re.compile(r"\[NON-?BLOCKING\s*/\s*LOW\]", re.IGNORECASE)
BLOCKING_COUNT_LINE = re.compile(
    r"BLOCKING\s+issues\s+found:\s*(\d+)", re.IGNORECASE
)
NON_BLOCKING_COUNT_LINE = re.compile(
    r"NON-?BLOCKING\s+issues\s+found:\s*(\d+)", re.IGNORECASE
)


def fail(msg: str, checks: list[dict]) -> None:
    print(json.dumps({"passed": False, "checks": checks, "reason": msg}, indent=2))
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: oracle.py <run_dir>")

    run_dir = Path(sys.argv[1]).resolve()
    repo_dir = run_dir / "repo"
    baseline_dir = repo_dir / ".baseline"
    vet_output = repo_dir / "vet-output.md"

    checks: list[dict] = []

    if not vet_output.exists():
        checks.append({"name": "vet-output.md present", "passed": False})
        fail("vet-output.md not found — /vet output artifact missing", checks)
    checks.append({"name": "vet-output.md present", "passed": True})

    text = vet_output.read_text()
    lower = text.lower()

    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in lower]
    if missing:
        checks.append({
            "name": "all required template sections present",
            "passed": False,
            "missing": missing,
        })
        fail(f"vet-output.md missing required sections: {missing}", checks)
    checks.append({"name": "all required template sections present", "passed": True})

    bcount_match = BLOCKING_COUNT_LINE.search(text)
    if not bcount_match:
        checks.append({"name": "BLOCKING true count in header", "passed": False})
        fail(
            "vet-output.md missing 'BLOCKING issues found: <n>' header line — "
            "true count must always be reported even when shown list is capped",
            checks,
        )
    blocking_true = int(bcount_match.group(1))
    checks.append({
        "name": "BLOCKING true count in header",
        "passed": True,
        "value": blocking_true,
    })

    nbcount_match = NON_BLOCKING_COUNT_LINE.search(text)
    if not nbcount_match:
        checks.append({"name": "NON-BLOCKING true count in header", "passed": False})
        fail(
            "vet-output.md missing 'NON-BLOCKING issues found: <n>' header line",
            checks,
        )
    non_blocking_true = int(nbcount_match.group(1))
    checks.append({
        "name": "NON-BLOCKING true count in header",
        "passed": True,
        "value": non_blocking_true,
    })

    blocking_tags = BLOCKING_TAG.findall(text)
    non_blocking_tags = NON_BLOCKING_TAG.findall(text)
    blocking_shown = len(blocking_tags)
    non_blocking_shown = len(non_blocking_tags)

    if blocking_shown > 10:
        checks.append({
            "name": "BLOCKING shown cap (<= 10)",
            "passed": False,
            "shown": blocking_shown,
        })
        fail(
            f"too many BLOCKING findings shown: {blocking_shown} > 10",
            checks,
        )
    checks.append({
        "name": "BLOCKING shown cap (<= 10)",
        "passed": True,
        "shown": blocking_shown,
    })

    if non_blocking_shown > 3:
        checks.append({
            "name": "NON-BLOCKING shown cap (<= 3)",
            "passed": False,
            "shown": non_blocking_shown,
        })
        fail(
            f"too many NON-BLOCKING findings shown: {non_blocking_shown} > 3",
            checks,
        )
    checks.append({
        "name": "NON-BLOCKING shown cap (<= 3)",
        "passed": True,
        "shown": non_blocking_shown,
    })

    high_blocking = sum(
        1 for tag in blocking_tags if tag.upper() == "HIGH"
    )
    if high_blocking < 1:
        checks.append({
            "name": "HIGH-priority blocker reported",
            "passed": False,
        })
        fail(
            "no [BLOCKING / HIGH] finding present — the seeded HIGH-priority "
            "bug (format_currency ignoring the currency parameter) was missed",
            checks,
        )
    checks.append({"name": "HIGH-priority blocker reported", "passed": True})

    seeded_bug_terms = ("format_currency", "currency parameter", "currency=", "currency argument")
    if not any(term.lower() in lower for term in seeded_bug_terms):
        checks.append({
            "name": "HIGH blocker references the seeded bug",
            "passed": False,
        })
        fail(
            "vet-output.md does not reference format_currency or the ignored "
            "currency parameter — the HIGH-priority bug was not located",
            checks,
        )
    checks.append({"name": "HIGH blocker references the seeded bug", "passed": True})

    test_economy_hit_terms = (
        "monkeypatch",
        "test_currency_extra",
        "duplicate test",
        "fold",
    )
    if not any(term in lower for term in test_economy_hit_terms):
        checks.append({
            "name": "test bloat flagged (monkeypatch or duplicate test file)",
            "passed": False,
        })
        fail(
            "vet-output.md does not flag the unnecessary monkeypatch or the "
            "duplicate test file test_currency_extra.py — test economy lens "
            "was not applied",
            checks,
        )
    checks.append({
        "name": "test bloat flagged (monkeypatch or duplicate test file)",
        "passed": True,
    })

    fixture_repo = Path(__file__).resolve().parent / "repo"
    out_of_scope_edits: list[str] = []
    for py in sorted(repo_dir.rglob("*.py")):
        if baseline_dir in py.parents:
            continue
        rel = py.relative_to(repo_dir).as_posix()
        fixture_equiv = fixture_repo / rel
        if not fixture_equiv.exists():
            continue
        if py.read_bytes() != fixture_equiv.read_bytes():
            out_of_scope_edits.append(rel)
    if out_of_scope_edits:
        checks.append({
            "name": "no source edits during /vet (review-only)",
            "passed": False,
            "edited": out_of_scope_edits,
        })
        fail(
            f"source files were modified during /vet — review-only mode "
            f"violated: {out_of_scope_edits}",
            checks,
        )
    checks.append({"name": "no source edits during /vet (review-only)", "passed": True})

    informational: list[dict] = []

    excess_low = blocking_true + non_blocking_true - (blocking_shown + non_blocking_shown)
    pattern_collapse_terms = ("pattern", "collapsed", "minor", "additional low")
    collapsed = any(term in lower for term in pattern_collapse_terms)
    informational.append({
        "name": "excess LOW issues collapsed into pattern-level note",
        "passed": collapsed if excess_low > 0 else True,
        "informational": True,
        "excess_low": excess_low,
    })

    hedging_terms = ("on the other hand", "could be argued", "both sides")
    hedged = any(term in lower for term in hedging_terms)
    informational.append({
        "name": "no both-sides hedging language",
        "passed": not hedged,
        "informational": True,
    })

    print(json.dumps({
        "passed": True,
        "checks": checks + informational,
        "blocking_true": blocking_true,
        "non_blocking_true": non_blocking_true,
        "blocking_shown": blocking_shown,
        "non_blocking_shown": non_blocking_shown,
        "reason": (
            "vet-output.md respected caps, reported the HIGH blocker with true "
            "counts, flagged test bloat, and made no source edits"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
