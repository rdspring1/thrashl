#!/usr/bin/env python3
"""Append debug ledger entries and detect simple churn checkpoints."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


LEDGER_PATH = Path("debug-session.md")
LOW_INFO = {"INCONCLUSIVE", "WEAKENED"}


@dataclass
class Entry:
    hypothesis: str
    action: str
    result: str
    interpretation: str
    lane: str | None = None
    skill: str | None = None


def parse_entries(text: str) -> list[Entry]:
    entries: list[Entry] = []
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    for block in blocks:
        lines = block.splitlines()
        fields: dict[str, str] = {}
        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
        if {"hypothesis", "action", "result", "interpretation"} <= fields.keys():
            entries.append(
                Entry(
                    hypothesis=fields["hypothesis"],
                    action=fields["action"],
                    result=fields["result"],
                    interpretation=fields["interpretation"].upper(),
                    lane=fields.get("lane"),
                    skill=fields.get("skill"),
                )
            )
    return entries


def action_family(action: str) -> str:
    action = action.lower().strip()
    action = re.sub(r"\s+", " ", action)
    return action[:80]


def append_entry(args: argparse.Namespace) -> int:
    entry = [
        f"Hypothesis: {args.hypothesis}",
        f"Action: {args.action}",
        f"Result: {args.result}",
        f"Interpretation: {args.interpretation.upper()}",
    ]
    if args.lane:
        entry.append(f"Lane: {args.lane}")
    if args.skill:
        entry.append(f"Skill: {args.skill}")

    prefix = ""
    if LEDGER_PATH.exists():
        existing = LEDGER_PATH.read_text(encoding="utf-8")
        prefix = "" if existing.endswith("\n\n") or not existing.strip() else "\n\n"

    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(prefix + "\n".join(entry) + "\n")

    sys.stdout.write(f"Appended entry to {LEDGER_PATH}\n")
    return 0


def checkpoint(_: argparse.Namespace) -> int:
    if not LEDGER_PATH.exists():
        sys.stdout.write("CHECKPOINT: no debug-session.md ledger found.\n")
        return 1

    entries = parse_entries(LEDGER_PATH.read_text(encoding="utf-8"))
    if not entries:
        sys.stdout.write("CHECKPOINT: ledger exists but has no parseable entries.\n")
        return 1

    recent = entries[-3:]
    low_info_count = sum(1 for entry in recent if entry.interpretation in LOW_INFO)
    repeated_family = False
    if len(recent) >= 2:
        families = [action_family(entry.action) for entry in recent]
        repeated_family = len(set(families)) < len(families)

    trigger = low_info_count >= 2 or repeated_family
    top = entries[-1]

    sys.stdout.write("CHECKPOINT\n")
    sys.stdout.write(f"Triggered: {'YES' if trigger else 'NO'}\n")
    sys.stdout.write(f"Top hypothesis: {top.hypothesis}\n")
    sys.stdout.write(f"Last action: {top.action}\n")
    sys.stdout.write(f"Last result: {top.result}\n")
    sys.stdout.write(f"Last interpretation: {top.interpretation}\n")
    sys.stdout.write(f"Recent low-information entries: {low_info_count}\n")
    sys.stdout.write(f"Repeated experiment family: {'YES' if repeated_family else 'NO'}\n")
    return 0 if trigger else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    append = subparsers.add_parser("append", help="append a debug ledger entry")
    append.add_argument("--hypothesis", required=True)
    append.add_argument("--action", required=True)
    append.add_argument("--result", required=True)
    append.add_argument(
        "--interpretation",
        required=True,
        choices=["supported", "weakened", "ruled_out", "inconclusive"],
    )
    append.add_argument("--lane")
    append.add_argument("--skill")
    append.set_defaults(func=append_entry)

    checkpoint_parser = subparsers.add_parser(
        "checkpoint", help="check for simple churn-guard triggers"
    )
    checkpoint_parser.set_defaults(func=checkpoint)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
