# Codex thrashl Doctrine

This file is the Codex CLI doctrine for `thrashl`.

Claude Code remains the source of truth. If this file conflicts with [`claude/CLAUDE.md`](/home/me/thrashl/claude/CLAUDE.md), follow the Claude-side doctrine and update this file to match.

## Core Principles

- Prefer low-friction, high-signal interaction.
- Prefer one concrete next action over a vague menu.
- Prefer reversible reasoning and reversible edits.
- Use existing repo patterns before inventing new structure.
- Reduce supervision cost and agent thrash.

## Mode Discipline

Treat prompt templates as modes.

- `clarify` for repo-grounded questions and context rebuilds
- `plan` for narrowing work before execution
- `impl` for bounded implementation
- `debug` for hypothesis-first diagnosis
- `vet` for skeptical review
- `save` for replayable handoffs
- `check` for read-only state snapshots

Use the lightest mode that fits the task.

- Rebuilding context: start with `clarify`
- Making a bounded change: use `impl`
- First failed implementation attempt: stop and switch to `debug`
- Reviewing correctness and regressions: use `vet`

## Stop And Handoff

If stopping, produce a handoff that another mode can use immediately.

Include when relevant:

- goal
- current state
- one concrete next action
- why that is the best next move
- expected outcome
- confidence
- risk
- evidence
- missing context
- best next mode

Do not stop with vague narration.

## Bounded Implementation

Implementation should be narrow by default.

- Make the smallest correct change.
- Touch as few files as possible.
- Reuse repo patterns.
- Run one focused validation after the implementation attempt.
- Do not make two speculative edits in a row.

Hard stop:

- If the first meaningful validation fails, stop implementation.
- Do not debug while still in implementation mode.
- Write a concise summary to [`save.md`](/home/me/thrashl/save.md).
- Best next mode becomes `debug`.

## Debug Churn Guard

Debugging is hypothesis-first, not edit-first.

- Rank hypotheses before proposing fixes.
- Tie each hypothesis to specific evidence.
- Prefer one discriminating experiment over multiple speculative changes.
- Maintain [`debug-session.md`](/home/me/thrashl/debug-session.md) as the experiment ledger.
- Do not repeat a ledgered experiment unless the rerun purpose is explicit.

Checkpoint triggers:

- 2-3 consecutive low-information results
- repeated variations on the same experiment family
- back-and-forth lane switching without new evidence
- 4 total skill/tool invocations without a supported hypothesis

At a checkpoint, pause and emit:

- top hypothesis
- strongest competing hypothesis
- untested assumption
- best next experiment
- whether missing source data blocks progress

Resume only when confidence is at least `MEDIUM` and no decision-relevant external source is missing.

## Evidence Discipline

Separate:

- Observed facts
- Hypotheses
- Assumptions
- Needed data

Observed facts must be tied to a source:

- file and line
- log output
- test result
- diff
- tool output

If you cannot cite a source, label it as an assumption.

Never invent evidence to support a hypothesis.

## State Files

`save.md`

- canonical cross-session replay and resume artifact
- concise, decision-oriented handoff
- should be useful tomorrow without rereading the whole session
- source of truth when reporting replay or resume state

`debug-session.md`

- authoritative ledger for the active debug session
- append-only by default
- records hypothesis, exact action, result, and interpretation
- not the long-term replay source

`check` has two intentional views:

1. active-session introspection:
2. explicit current-session ledger entries
3. [`debug-session.md`](/home/me/thrashl/debug-session.md)
4. [`save.md`](/home/me/thrashl/save.md)

1. replay or resume state:
2. [`save.md`](/home/me/thrashl/save.md)
3. [`debug-session.md`](/home/me/thrashl/debug-session.md) only as an explicit fallback when `save.md` is missing

Do not merge contradictory sources.

## One-Best-Next-Skill Routing

Codex should not fake Claude subagents. Instead, route to one best next working style.

| Lane | Signals | Best Codex move |
|---|---|---|
| `clarify` | unfamiliar code, repo question, call-path uncertainty | inspect files and answer directly |
| `impl` | semantics are clear and change is bounded | implement once, validate once |
| `debug` | failed test, crash, wrong output, uncertain fix direction | rank hypotheses and pick one experiment |
| `vet` | diff exists and correctness needs scrutiny | review actual diff or last commit |
| `check` | need grounded session state only | snapshot ledger or save file |

For technical debugging layers, route to one tool family at a time:

| Layer | Signals | Tool family |
|---|---|---|
| `above-python` | env, import, launch, config | code/log inspection |
| `python-framework` | exception, wrong output, tensor state | pdb-style investigation |
| `perf-framework` | step overhead, dataloader bottleneck | torch profiler |
| `perf-system` | CUDA timeline, overlap, graph replay | nsys |
| `native-runtime` | hang, deadlock, segfault, C extension crash | gdb |
| `toolchain` | PTX, SASS, compiler lowering | cuobjdump or nvdisasm |

Pick one best next skill or tool family. Do not hedge across multiple families in the same turn.

## Don't-Ask-Me Rules

Do not interrupt for:

- naming
- small refactors
- local code organization
- minor style choices
- straightforward test selection
- obvious low-cost experiments

Only ask when one of these is true:

- semantics are underdetermined by available evidence
- architecture or interface direction is required
- multiple plausible meanings would materially change behavior
- the experiment is destructive, expensive, or high-risk
- repo evidence is insufficient

## Output Shaping

- Answer the actual question first.
- Keep summaries concise and decision-oriented.
- Omit empty sections.
- Prefer one concrete next action over a list of equivalent options.
- If confidence is low, say so explicitly and stop cleanly.
