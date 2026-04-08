#!/usr/bin/env python3
"""Report grounded state from save.md and debug-session.md with explicit views."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def emit(view: str, source_path: Path, role: str, text: str) -> int:
    sys.stdout.write(
        f"VIEW: {view}\n"
        f"SOURCE: {source_path.name}\n"
        f"ROLE: {role}\n\n"
        f"{text}\n"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report grounded state. "
            "'active' prefers the active debug ledger. "
            "'replay' treats save.md as the replay/resume source of truth."
        )
    )
    parser.add_argument(
        "--view",
        choices=("active", "replay"),
        default="active",
        help="choose whether to inspect active-session state or replay/resume state",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    debug_path = cwd / "debug-session.md"
    save_path = cwd / "save.md"

    save_text = read_text(save_path)
    debug_text = read_text(debug_path)

    if args.view == "active":
        if debug_text:
            return emit(
                "active",
                debug_path,
                "authoritative active debug ledger",
                debug_text,
            )
        if save_text:
            return emit(
                "active",
                save_path,
                "canonical replay artifact used as fallback active context",
                save_text,
            )
        sys.stdout.write(
            "No legible active state found in debug-session.md or save.md.\n"
        )
        return 1

    if save_text:
        return emit(
            "replay",
            save_path,
            "canonical replay and resume artifact",
            save_text,
        )
    if debug_text:
        return emit(
            "replay",
            debug_path,
            "active debug ledger fallback because save.md is missing",
            debug_text,
        )

    sys.stdout.write("No legible replay state found in save.md or debug-session.md.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
