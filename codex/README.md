# Codex CLI Port for thrashl

This is a Codex-native adaptation of the `thrashl` workflow.

The design goal is not to imitate Claude Code's surface area. The goal is to preserve the control model:

- bounded implementation
- hypothesis-first debugging
- explicit handoffs
- evidence discipline
- replayable state in `save.md`
- active debug history in `debug-session.md`

Claude remains the source of truth. If this folder drifts from [`claude/CLAUDE.md`](/home/me/thrashl/claude/CLAUDE.md), update this port to match the Claude-side doctrine instead of inventing a Codex-only variant.

## Proposed Layout

```text
codex/
  AGENTS.md
  README.md
  prompts/
    clarify.md
    plan.md
    impl.md
    debug.md
    vet.md
    save.md
    check.md
  scripts/
    check_state.py
    debug_guard.py
```

## Surface Mapping

| Claude thrashl surface | Codex CLI equivalent | Notes |
|---|---|---|
| `/question` or `/clarify` | `codex/prompts/clarify.md` | Use as a prompt template for repo-grounded answers. |
| `/plan` | `codex/prompts/plan.md` | Codex already has planning behavior; this template sharpens output and stop conditions. |
| `/impl` | `codex/prompts/impl.md` | Keep one-attempt, one-validation budget in the prompt. |
| `/debug` | `codex/prompts/debug.md` + `codex/scripts/debug_guard.py` | Prompt handles reasoning; script enforces ledger append and churn checks. |
| `/vet` | `codex/prompts/vet.md` | Codex already reviews well; this template narrows it to high-signal findings. |
| `/save` | `codex/prompts/save.md` | Codex writes [`save.md`](/home/me/thrashl/save.md) directly. |
| `/check` | `codex/prompts/check.md` + `codex/scripts/check_state.py` | Script provides explicit `active` vs `replay` state views. |
| `navigator` | Clarify or Plan prompt | Separate agent not required. Use Codex itself in exploration mode. |
| `implementer` | Impl prompt | Native Codex behavior maps cleanly here. |
| `debugger` | Debug prompt | Keep hypothesis-first, evidence-first, one-best-next-experiment. |
| `reviewer` | Vet prompt | Codex review mode already fits. |
| `explain` | Check prompt / script | Read-only state reporting. |

## Recommended AGENTS.md Structure

1. Source-of-truth rule
2. Core operating principles
3. Mode discipline
4. Stop and handoff behavior
5. Debug churn guard
6. Evidence discipline
7. State files contract
8. One-best-next-skill routing
9. Don't-ask-me rules
10. Output shaping rules

## What Lives Where

`AGENTS.md`

- durable doctrine
- source-of-truth precedence
- stop rules
- evidence policy
- churn guard policy
- state-file contract
- routing heuristics
- user interaction preferences

`prompts/`

- mode switching
- task-local output formats
- session-local constraints
- reminders about budgets and stop conditions
- reusable "start from here" text for Codex sessions

`scripts/`

- deterministic ledger checks
- source-ordered state snapshotting
- rules that are easier to enforce mechanically than by prompting
- doctrine parity checks against Claude-side sources

## What Does Not Port 1:1

- Claude slash commands do not exist as a first-class Codex CLI surface. Use prompt templates instead.
- Specialist subagents are not the default Codex interaction model. Do not force roleplay when a single Codex pass is cleaner.
- Automatic command wiring from markdown files is Claude-specific. In Codex, templates are explicit operator tools, not built-in commands.
- Any Claude-specific "agent picker" behavior should become routing guidance inside `AGENTS.md`, not fake subagent infrastructure.

## Minimal V1 Port

This folder preserves the core doctrine with the smallest useful surface:

- `AGENTS.md` carries the doctrine.
- `prompts/*.md` replace custom commands.
- `scripts/debug_guard.py` appends experiments to [`debug-session.md`](/home/me/thrashl/debug-session.md) and flags churn checkpoints.
- `scripts/check_state.py --view active` prefers the active debug ledger, while `--view replay` treats [`save.md`](/home/me/thrashl/save.md) as the source of truth.
- `save.md` remains the canonical replayable handoff file.
- `debug-session.md` remains the authoritative active debug ledger, not the long-term replay source.

That is enough to preserve:

- bounded implementation
- debug churn guard
- evidence discipline
- save replayability
- one-best-next-skill routing

## Suggested Migration Order

1. Keep editing the Claude-side doctrine first in [`claude/CLAUDE.md`](/home/me/thrashl/claude/CLAUDE.md).
2. Port only the stable doctrine into [`codex/AGENTS.md`](/home/me/thrashl/codex/AGENTS.md).
3. Add Codex prompt templates for `clarify`, `impl`, `debug`, `vet`, `save`, and `check`.
4. Add helper scripts only where prompt-only behavior keeps drifting.
5. Use Codex as the secondary operator path and compare its outputs against Claude on real tasks.
6. Promote only the parts that hold up across repeated sessions; keep everything else Claude-primary.

## Usage Pattern

Start a Codex session by pointing it at [`codex/AGENTS.md`](/home/me/thrashl/codex/AGENTS.md), then paste the relevant template from `codex/prompts/`.

For debug sessions:

1. Use [`codex/prompts/debug.md`](/home/me/thrashl/codex/prompts/debug.md)
2. Append the experiment with `python3 codex/scripts/debug_guard.py append ...`
3. Run `python3 codex/scripts/debug_guard.py checkpoint` when you need a deterministic churn check

For state snapshots:

1. Use [`codex/prompts/check.md`](/home/me/thrashl/codex/prompts/check.md)
2. Run `python3 codex/scripts/check_state.py --view active` for active-session introspection
3. Run `python3 codex/scripts/check_state.py --view replay` for replay/resume state

For doctrine maintenance:

1. Run `python3 codex/scripts/check_parity.py` to check high-value Codex doctrine parity against the Claude-side source files

For Codex evals:

1. Prepare a run with `python3 codex/evals/runner.py prepare codex-impl-first-failure`
2. Open Codex in the prepared repo and follow `../SPEC.md` using [`codex/prompts/impl.md`](/home/me/thrashl/codex/prompts/impl.md)
3. Score with `python3 codex/evals/runner.py score <run_dir>`
