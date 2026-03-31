# Changelog

## [0.1.0] - 2026-03-30

### Added

**Commands** (`commands/`)

- `impl.md` — Implementer mode. Makes minimal, bounded changes with strong stop-to-summary behavior.
- `debug.md` — Debugger mode. Hypothesis-first reasoning; ranks hypotheses before proposing fixes; prefers one discriminating experiment over speculative changes.
- `vet.md` — Reviewer mode. Skeptical diff review focused on correctness, regressions, hidden assumptions, and high-signal test proposals.
- `summary.md` — Structured handoff output: goal, state, next action, confidence, risk, missing context.

**Agents** (`agents/`)

- `implementer.md` — Minimal change specialist. Emits decision packets instead of thrashing.
- `debugger.md` — Failure diagnosis specialist. Evidence-ranked hypotheses, discriminating experiments.
- `navigator.md` — Codebase mapping specialist. Maps files, data flow, and edit points without prematurely solving.
- `reviewer.md` — Skeptical diff reviewer. Identifies highest-signal concerns.
