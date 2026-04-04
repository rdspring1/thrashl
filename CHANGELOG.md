# Changelog

## [0.4.0] - 2026-04-04

### Added

**Commands** (`commands/`)

- `check.md` — State-snapshot mode. Reports current debug session state from externally grounded sources only (`debug-session.md` or explicit conversation ledger entries). Does not reconstruct state from inferred reasoning. Use during long silent debug sessions.

**Agents** (`agents/`)

- `explain.md` — Externally-grounded introspection specialist. Implements the same source contract and output structure as `/check`. Available as a persistent named agent alongside the debugger.

### Changed

**Commands** (`commands/`)

- `debug.md` — Added four sections: experiment ledger (appends to `debug-session.md`), churn guard (mandatory CHECKPOINT after 2-3 low-information entries or repeated test-family churn; may resume only when confidence >= MEDIUM and no decision-relevant source is missing), evidence discipline (Observed facts / Hypotheses / Assumptions / Needed data; cite sources; never invent evidence), data-source policy (ask for external source only when missing semantics would change which branch to debug next). Added optional `Checkpoint` section to output format.

**Agents** (`agents/`)

- `debugger.md` — Added compact rules mirroring `debug.md`: experiment ledger, churn guard, evidence discipline, data-source policy.

## [0.3.0] - 2026-03-31

### Added

- `sync-claude.sh` — Sync script. Rsyncs `claude/commands/` and `claude/agents/` into `~/.claude/`. Replaces the manual `cp` install steps in README.

## [0.2.0] - 2026-03-31

### Added

**Commands** (`commands/`)

- `question.md` — Question mode. Answers a specific codebase question using repo evidence; answers directly first, no implementation drift.
- `save.md` — Save mode. Produces a concise markdown handoff from current conversation/task state; infers goal, blocker, and next step without explicit input.

### Changed

**Commands** (`commands/`)

- `debug.md` — Default behavior now infers the current blocker from conversation, repo state, and visible failures when no explicit context is provided. Output renamed from `SUMMARY` to `DEBUG NOTE`. Format tightened: optional sections only appear when meaningful, `What I want to do next` → `Next action`.
- `vet.md` — Default behavior now targets uncommitted diff (or last commit if clean). Added don't-ask-me zone. Output renamed from `REVIEW SUMMARY` to `VET NOTE`. Format tightened to match debug.md style.
- `summary.md` — Removed. Replaced by `save.md`.

**Agents** (`agents/`)

- `debugger.md` — Added: prefer 1 best experiment over multiple equivalent options; if one hypothesis is clearly dominant, do not pad with weaker alternatives.
- `navigator.md` — Added explicit default behavior: answer the specific repo question first, provide supporting references, do not implement unless asked.
- `reviewer.md` — Replaced generic test guidance with explicit no-coverage-theater rule: only propose tests that catch realistic failure modes or protect important invariants.

**CLAUDE.md**

- Added sections: command vs agent preference, default command behavior, save behavior, exploration/debugging/review preference, output shaping.

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
