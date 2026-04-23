# Changelog

## [0.14.0] - 2026-04-23

### Changed

**Doctrine** (`claude/CLAUDE.md`, `codex/AGENTS.md`)

- Added **High-Autonomy Mode** section to both doctrine files (mirrored). Covers: worker doctrine (full-auto is a worker mode, not an authority mode; execution speed does not change judgment); preflight requirement (a `save.md` Preflight block is required before any long autonomous run); mutation policy (three classes: always-allowed, checkpoint-before-running, never-without-human-approval — with examples for each); checkpoint cadence (triggers: 20+ tool invocations since last checkpoint, 2+ consecutive low-information results in impl mode, any checkpoint-class mutation, scope drift beyond preflight contract, confidence below MEDIUM).

**Commands** (`claude/commands/`)

- `impl.md` — Added **Mutation policy** section after the canonical-command-check: three classes (always-allowed, checkpoint-before-running, never-without-human-approval) applied in autonomous runs. Added two new **Handoff conditions**: (1) same command fails twice with materially the same error and no meaningful change between runs — classify as invocation/requirement/environment/code and stop, do not retry; (2) in autonomous runs, checkpoint after 20+ tool invocations or if scope expands beyond preflight contract.

- `debug.md` — Strengthened churn guard language: in full-auto mode all three triggers are mandatory hard stops; failure classification must be emitted before any retry regardless of mode.

- `save.md` — Added `### Preflight` optional block to the output schema. Required before autonomous runs; omitted for interactive saves. Fields: bounded scope, canonical command, stop condition, risk level, expected artifact.

**Codex** (`codex/`)

- `prompts/impl.md` — Parity with `claude/commands/impl.md`: added mutation policy section and two new hard-stop conditions (repeated-invariant-failure classify-and-stop; autonomous-run checkpoint cadence).

- `prompts/save.md` — Parity with `claude/commands/save.md`: added `### Preflight` optional block to the output schema.

---

## [0.13.0] - 2026-04-11

### Changed

**Commands** (`claude/commands/`)

- `debug.md` — Added **Failure classification** section: before retrying a failing command, classify it as invocation mismatch, requirement mismatch, environment mismatch, or true code bug. If classification is invocation, requirement, or environment, emit a DEBUG NOTE with the recommended fix and stop — do not run the same failing command again. Extended **churn guard** with a third trigger: the same command fails twice with materially the same error and no meaningful change (code edit, env change, dependency install, config update) occurred between runs — treat this as invocation/requirement/environment mismatch, not a code bug. Added optional `Canonical:` and `Failure-class:` fields to the **experiment ledger** format. Added `Failure classification:` to the **checkpoint** output.

- `impl.md` — Added **Canonical-command check** section before the execution budget: before running any test, build, or run command, check for a documented invocation in README.md, Makefile, pyproject.toml, tox.ini / noxfile.py, package.json, and CI workflow files. If a canonical form exists, use it instead of a guessed variant. Record `Canonical: YES / NO / UNKNOWN` in the ledger.

- `check.md` — Added three fields to `CURRENT STATE` output: `Last command` (exact command from most recent ledger entry), `Repo invocation match` (YES / NO / UNKNOWN), and `Repeat failure count` (identical error with no meaningful change between runs). Added `Blocker classification` field (code / invocation / environment / requirement / UNKNOWN). Updated core rules to surface `Canonical` and `Failure-class` ledger entries when present.

**Doctrine** (`claude/CLAUDE.md`)

- Added one bullet to **Debugging preferences**: if the same command fails twice with no meaningful change between runs, classify it as invocation, requirement, or environment mismatch before retrying; check README, Makefile, and pyproject.toml for the canonical invocation.

**Codex** (`codex/`)

- `prompts/debug.md` — Parity with `claude/commands/debug.md`: added failure classification section, extended churn guard with same-command-same-error trigger, and added `Failure classification:` to the checkpoint output shape.

- `prompts/impl.md` — Parity with `claude/commands/impl.md`: added canonical-command check section before execution budget.

- `prompts/check.md` — Parity with `claude/commands/check.md`: added `Last command`, `Repo invocation match`, `Repeat failure count`, and `Blocker classification` to the output shape.

- `scripts/debug_guard.py` — Added `canonical` and `failure_class` fields to the `Entry` dataclass and ledger parser. Added `--canonical` and `--failure-class` CLI arguments to the `append` subcommand. Added repeat-same-command detection to the `checkpoint` subcommand: triggers when the last two entries share the same action family and both interpretations are non-SUPPORTED. Checkpoint output now emits `Failure classification:` and `Canonical invocation used:` when present.

## [0.12.0] - 2026-04-07

### Added

**Codex** (`codex/`)

- `AGENTS.md` — Codex CLI doctrine file. Translates the Claude-side workflow into Codex-native terms while keeping Claude as the source of truth. Preserves bounded implementation, debug churn guard, evidence discipline, `save.md` replayability, and one-best-next-skill routing.
- `prompts/` — Prompt-template equivalents for the main thrashl surfaces: `clarify.md`, `plan.md`, `impl.md`, `debug.md`, `vet.md`, `save.md`, and `check.md`. These replace Claude-style slash commands with reusable Codex session templates.
- `scripts/check_state.py` — Deterministic state snapshot helper. Reads `debug-session.md` first, then `save.md`, and stops cleanly if neither contains legible state.
- `scripts/debug_guard.py` — Deterministic debug ledger helper. Appends experiment entries to `debug-session.md` and flags simple churn-checkpoint conditions from recent low-information or repeated experiment-family runs.
- `README.md` — Codex port overview, surface mapping, doctrine split (`AGENTS.md` vs prompts vs scripts), non-portable Claude surfaces, minimal v1 scope, and migration order with Claude remaining primary.

### Changed

**Sync** (`sync-codex.sh`)

- Added `sync-codex.sh` — Codex install/sync analogue to `sync-claude.sh`. Copies `codex/AGENTS.md` plus `codex/prompts/` and `codex/scripts/` into `~/.codex/`, creating target directories as needed.

**README**

- Added a `Codex CLI` section describing the Codex-native port and install flow via `./sync-codex.sh`.

## [0.11.0] - 2026-04-05

### Changed

**Commands** (`claude/commands/`)

- `impl.md` — Added **Execution budget** block: one real implementation attempt plus one validation run is the explicit budget for this mode. Added **Hard stop rule**: if validation fails after a real attempt, stop immediately — do not investigate, rank hypotheses, or make another edit; emit SUMMARY and route to Debugger. The budget framing replaces the implicit "stop if failure" condition with a named contract.

- `debug.md` — Added **Lessons learned** block to the DEBUG NOTE output format. Emitted only when hypothesis is confirmed, fix is verified, and the takeaway is nontrivial. Three optional lines: new checklist item, new source policy, new skill routing hint. Omit any line with no specific reusable content.

- `save.md` — Declared `save.md` as the canonical state file shared by `/check`, `/debug`, and the next session. Added step: if `debug-session.md` exists, incorporate a summary of its experiment ledger into the Evidence section. Clarified that writing `save.md` is normative, not incidental.

- `check.md` — Updated source priority order to reflect immediacy: (1) explicit ledger entries in current conversation, (2) `debug-session.md`, (3) `save.md`. Stop at the first legible source. Rationale: `/check` is used mid-session to inspect a silent active debug session; the current conversation is the most authoritative source.

---

## [0.10.0] - 2026-04-04

### Changed

**Agents** (`claude/agents/`)

- `debugger.md` — Added **Skill routing** block: 6-lane classification table (above-python, python-framework, perf-framework, perf-system, native-runtime, toolchain), lane declaration rule, skill commitment rule (one skill per turn, cheaper-first tie-breaking), and wrong-skill detection with lane-switch logging to `debug-session.md`.

**Commands** (`claude/commands/`)

- `debug.md` — Replaced narrow 2-skill "Live session handoff" (gdb/pdb only) with full 5-skill routing table covering all specialized debug skills, plus transition rules for lane switching and churn guard integration.
- `check.md` — Added `Current lane` and `Active skill` fields to `CURRENT STATE` output format, sourced from `debug-session.md`; added lane/skill sourcing rule to core rules.

---

## [0.9.0] - 2026-04-04

### Added

**Skills** (`claude/skills/`)

- `pytorch-profiler-trace/` — Capture and interpret PyTorch profiler traces for training and inference programs on GPU nodes. Encodes practical `torch.profiler` setup choices for CPU/CUDA hotspot tracing, kernel/stream timing, CUDA Graph behavior, distributed/NCCL overlap, and dataloader overhead. Includes `references/commands.md` (torch.profiler API reference, schedule params, output methods, 6 copy-pasteable setups), `references/fallback-table.md` (8-scenario decision table including nsys escalation), `references/trace-guide.md` (`key_averages()` column guide, Chrome/Perfetto trace reading, 6 common pathologies, Perfetto tips), and `scripts/profile-snippet.py` (three goal-driven templates: hotspot/graph/distributed with REPLACE markers, wall-time measurement, and Chrome trace export).

---

## [0.8.0] - 2026-04-04

### Added

**Skills** (`claude/skills/`)

- `pdb-debugger/` — Interactive pdb session partner for Python programs in Docker/GPU-node sessions. Covers single-process Python, torchrun multiprocess, and dataloader worker scenarios. Drives toward testing a specific hypothesis with exact copy-pasteable pdb commands and explicit handoff rules to `gdb-debugger` when the bug is below Python level. Includes `references/commands.md` (core pdb commands, conditional breakpoints, exception-driven debugging, 6 pipelines), `references/debug-checklist.md` (9-step debugging checklist, pdb→gdb switch decision table, torchrun/dataloader notes), `references/outcomes-guide.md` (5 common outcomes: wrong process/worker, exception before breakpoint, hang with no Python frame, bad tensor state, bug below Python), and `scripts/pdb-launcher.sh` (goal-driven launcher: basic/exception/rank0/hang).

### Changed

**Commands** (`claude/commands/`)

- `debug.md` — Extended **Live session handoff** rule to route between `gdb-debugger` (C/CUDA, segfaults, C extension deadlocks) and `pdb-debugger` (Python, torchrun, dataloader, tensor state).

---

## [0.7.0] - 2026-04-04

### Added

**Skills** (`claude/skills/`)

- `gdb-debugger/` — Interactive GDB session partner for multiprocess programs with races, hangs, deadlocks, and crashes in Docker/GPU-node sessions. Drives toward testing a specific hypothesis with exact copy-pasteable GDB commands. Includes `references/commands.md` (fork/exec/clone control, breakpoints, threads, signals, attach, 7 pipelines), `references/race-checklist.md` (9-step race checklist, launch-first vs. attach-first decision table, when to open dual session), `references/outcomes-guide.md` (5 common outcomes: wrong process, missed race, deadlock, crash before breakpoint, one-sided breakpoint), and `scripts/dual-attach.sh` (dual GDB session template with coordination pattern).

### Changed

**Commands** (`claude/commands/`)

- `debug.md` — Added **Live session handoff** rule: when the next discriminating experiment requires interactive GDB (attach, race, hang, deadlock), explicitly transition to the `gdb-debugger` skill. `/debug` → hypothesis ranking from code/logs; `gdb-debugger` → live GDB session driving.

---

## [0.6.0] - 2026-04-04

### Added

**Skills** (`claude/skills/`)

- `nsys-trace-profiler/` — Capture and interpret Nsight Systems traces for CUDA programs in Docker/GPU-node sessions. Encodes goal-driven nsys flag selection, CUDA Graph capture/replay semantics, launch latency analysis, CPU/GPU overlap inspection, and idle gap identification. Includes `references/commands.md` (nsys/nsys-stats flag reference + 9 pipelines), `references/fallback-table.md` (8-scenario decision table), `references/trace-guide.md` (timeline layer guide, graph capture/replay, overlap, sync stall patterns, nsys stats usage), and `scripts/capture-trace.sh` (goal-driven wrapper: basic/launch/graph/overlap/scoped).

### Changed

**Skills** (`claude/skills/`)

- Relocated from `.claude/skills/` to `claude/skills/` to consolidate all Claude artifacts under `claude/`.

- `cuobjdump-lowering-inspector/` — Arch notes updated: added `sm_100a` as a distinct target required for `.rs` (stochastic) rounding in `cvt.*` instructions (not supported on plain `sm_100`). Added note on `cvt.rs.satfinite.e2m1x4.f32` lowering to two sequential `F2FP.SATFINITE.E2M1.F32.PACK_AB_MERGE_C.RS` SASS instructions (confirmed CUDA 13.2 / sm_100a). All pipeline examples in `references/commands.md` and default arch in `scripts/snippet-to-dump.sh` updated from `sm_100`/`sm_90` to `sm_100a`.

**Sync** (`sync-claude.sh`)

- Updated skills source path from `.claude/skills/` to `claude/skills/` following the relocation above.

---

## [0.5.0] - 2026-04-04

### Added

**Skills** (`.claude/skills/`)

- `cuobjdump-lowering-inspector/` — Inspect PTX and SASS lowering for CUDA snippets, `.cu` files, executables, cubins, and fatbins. Encodes nvcc/cuobjdump/nvdisasm/ptxas flag knowledge, input-type routing, fallback strategy, and insight-first output format. Primary use case: inline asm inspection where functional docs are incomplete and compiler output is the main source of truth. Includes `references/commands.md` (flag reference + pipelines), `references/fallback-table.md` (8-scenario decision table), `references/correlation-guide.md` (PTX↔SASS mapping guide), and `scripts/snippet-to-dump.sh` (compile-and-dump helper with 3-tier SASS fallback).

---

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
