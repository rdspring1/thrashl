#!/usr/bin/env python3
"""Check high-value Codex doctrine parity against Claude-side source files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Rule:
    name: str
    claude_files: tuple[str, ...]
    claude_patterns: tuple[str, ...]
    codex_files: tuple[str, ...]
    codex_patterns: tuple[str, ...]


RULES = (
    Rule(
        name="bounded implementation rule",
        claude_files=("claude/commands/impl.md",),
        claude_patterns=(
            "one real implementation attempt. one validation run.",
            "if validation fails after a real attempt, stop immediately.",
        ),
        codex_files=("codex/AGENTS.md", "codex/prompts/impl.md"),
        codex_patterns=(
            "run one focused validation after the implementation attempt.",
            "one validation run",
            "if the first meaningful validation fails, stop implementation.",
        ),
    ),
    Rule(
        name="first failed validation routes to debug",
        claude_files=("claude/commands/impl.md",),
        claude_patterns=(
            "emit summary, set best next mode: debugger, and stop.",
            "write it to `save.md`",
        ),
        codex_files=("codex/AGENTS.md", "codex/prompts/impl.md"),
        codex_patterns=(
            "best next mode becomes `debug`.",
            "write a concise handoff to save.md.",
        ),
    ),
    Rule(
        name="evidence discipline split",
        claude_files=("claude/commands/debug.md",),
        claude_patterns=(
            "observed facts | hypotheses | assumptions | needed data",
            "if you cannot cite a source, label the claim as an assumption",
        ),
        codex_files=("codex/AGENTS.md", "codex/prompts/debug.md"),
        codex_patterns=(
            "observed facts",
            "hypotheses",
            "assumptions",
            "needed data",
            "if you cannot cite a source, label it as an assumption.",
        ),
    ),
    Rule(
        name="save.md as canonical replay artifact",
        claude_files=("claude/commands/save.md",),
        claude_patterns=(
            "`save.md` is the canonical state file.",
        ),
        codex_files=("codex/AGENTS.md", "codex/README.md", "codex/prompts/save.md"),
        codex_patterns=(
            "canonical cross-session replay and resume artifact",
        ),
    ),
    Rule(
        name="debug churn checkpoint behavior",
        claude_files=("claude/commands/debug.md",),
        claude_patterns=(
            "trigger a mandatory checkpoint when:",
            "2-3 consecutive ledger entries yield low-information results",
            "the last experiment family has been retried with only small variations",
        ),
        codex_files=("codex/AGENTS.md", "codex/prompts/debug.md"),
        codex_patterns=(
            "checkpoint triggers:",
            "2-3 consecutive low-information results",
            "repeated variations on the same experiment family",
            "at a checkpoint, pause",
        ),
    ),
)


def read_lower(path_str: str) -> str:
    path = ROOT / path_str
    return path.read_text(encoding="utf-8").lower()


def missing_patterns(files: tuple[str, ...], patterns: tuple[str, ...]) -> list[str]:
    corpus = "\n".join(read_lower(path_str) for path_str in files)
    return [pattern for pattern in patterns if pattern not in corpus]


def main() -> int:
    failures: list[str] = []

    for rule in RULES:
        claude_missing = missing_patterns(rule.claude_files, rule.claude_patterns)
        codex_missing = missing_patterns(rule.codex_files, rule.codex_patterns)

        if claude_missing or codex_missing:
            failures.append(rule.name)
            print(f"FAIL {rule.name}")
            if claude_missing:
                print(f"  missing in Claude sources: {claude_missing}")
            if codex_missing:
                print(f"  missing in Codex sources: {codex_missing}")
            continue

        print(f"PASS {rule.name}")

    if failures:
        print()
        print(f"Parity check failed for {len(failures)} rule(s).")
        return 1

    print()
    print("Parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
