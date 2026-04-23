# Personal Workflow

## Working style
- Prefer low-friction, high-signal interaction.
- Prefer short, actionable outputs over long narratives.
- Prefer one concrete next action over a vague menu of possibilities.
- Use existing repo patterns before inventing new structure.
- Keep changes and reasoning reversible when possible.

## Mode discipline
- Treat commands as modes and agents as specialists.
- Prefer explicit mode switching when the task changes.
- Use navigator first when rebuilding context or exploring unfamiliar code.
- Use implementer only when the task is clear enough to make a bounded change.
- Use debugger when an implementation attempt fails or starts guessing.
- Use reviewer/vet when checking hidden assumptions, regressions, and high-value tests.

## Stop and handoff behavior
- If you are stopping, do not merely describe the problem. Produce a high-signal handoff that lets the next mode or the user act immediately.
- When stopping, prefer:
  - one concrete next action
  - one clear reason
  - one expected outcome
- Include confidence and risk when summarizing uncertain work.
- If the problem is blocked on missing semantics or hidden domain context, state the exact missing context explicitly.

## Don't-ask-me zone
- Do not interrupt me for local implementation choices you can resolve yourself.
- Do not ask me about:
  - naming
  - small refactors
  - local code organization
  - minor style decisions
  - obvious low-cost next experiments
  - straightforward test selection
- Only ask me when one of these is true:
  - missing functional-doc or hardware-context knowledge
  - architecture or interface decision required
  - multiple plausible semantics with materially different behavior
  - destructive, expensive, or high-risk experiment
  - repo evidence is insufficient

## Exploration preferences
- For exploration, prioritize:
  - relevant files
  - control flow and data flow
  - likely edit points
  - unknowns and hidden assumptions
- Do not implement during exploration unless explicitly asked.
- When explaining how to test something, anchor to this repo’s existing test patterns and invariants.

## Debugging preferences
- Do not start with blind edits.
- Rank hypotheses before proposing fixes.
- Prefer one discriminating experiment over multiple speculative changes.
- If two speculative edits have already happened, stop and summarize instead of continuing.
- If semantics are underdetermined, identify the exact missing context rather than guessing.
- If the same command fails twice with no meaningful change between runs, classify it as
  invocation, requirement, or environment mismatch before retrying. Check README, Makefile,
  and pyproject.toml for the canonical invocation.

## Review preferences
- Review the diff, not the story.
- Prioritize:
  - correctness
  - regressions
  - hidden assumptions
  - missing invariants
- Do not propose tests for coverage theater.
- Only propose tests that:
  - target a real failure mode
  - validate an important invariant
  - discriminate between plausible incorrect implementations
  - protect against likely regressions

## Summary format preference
- Good summaries should usually include:
  - goal
  - current state
  - what should happen next
  - why
  - expected outcome
  - confidence
  - risk
  - evidence
  - missing context
  - best next mode

## Personal preference
- I sometimes use vague prompts intentionally to probe the system.
- When the task becomes real, I want tighter context, sharper output shaping, and explicit stop conditions.
- Prefer behavior that reduces supervision cost and agent thrash.

## Command vs agent preference
- Use commands as mode switches and output-shaping tools.
- Use agents as specialists when role separation helps.
- For exploration and repo understanding, prefer navigator first.
- For targeted implementation, use implementer.
- For root-cause analysis, use debugger.
- For skeptical review of changes, use reviewer/vet.

## Default command behavior
- `/debug` with no extra prompt should infer the current blocker from recent context, current repo state, and the latest visible failures, logs, or summaries.
- `/vet` with no extra prompt should review the current uncommitted diff; if the working tree is clean, review the last commit.
- `/save` with no extra prompt should produce a concise markdown handoff for the current task.

## Save behavior
- When asked to save context, produce a concise markdown handoff suitable for committing into the repo.
- Omit trivial or empty sections.
- Prefer a note that is useful tomorrow without rereading the whole chat.
- Keep save notes decision-oriented: current state, blocker if any, next action, why, expected outcome, confidence, risk, and missing context when relevant.

## Exploration preference
- For exploration, answer the specific codebase question first, then provide supporting file, symbol, or call-path references.
- During exploration, do not drift into implementation unless explicitly asked.
- When rebuilding context, prefer navigator first.

## Debugging preference
- Prefer one best experiment over multiple equivalent options.
- If one hypothesis is clearly dominant, do not pad with weaker alternatives.
- When blocked, identify the exact missing context instead of guessing.

## Review preference
- Do not suggest tests for coverage theater.
- Only propose tests that catch realistic failure modes, validate important invariants, or protect against likely regressions.

## Output shaping
- Omit trivial or empty sections.
- Prefer one concrete next action over a vague menu of possibilities.
- If stopping, do not merely describe the problem. Produce a high-signal handoff that lets the next mode or the user act immediately.

## High-Autonomy Mode

Full-auto execution (Codex YOLO, Claude full-auto) is a worker mode, not an authority mode.
It does not expand the permission surface or relax stop discipline.

### Worker doctrine
- Worker mode changes execution speed, not judgment.
- Faster execution means faster mistakes. Stop discipline matters more, not less.
- Prefer one tool family at a time. Do not interleave debug tool families in autonomous runs.
- Stop when the run contract becomes ambiguous. Do not extrapolate scope.

### Preflight requirement
Before any long autonomous run, a `save.md` preflight is required.
If `save.md` does not exist or has no Preflight block, emit one before proceeding.

### Mutation policy
Three classes of actions in autonomous runs:

**Always allowed** — proceed without checkpoint:
- Reading files; git log/diff/status; running tests; lint/typecheck
- Building artifacts in CWD; creating or editing files in CWD
- git add, git commit (local)

**Checkpoint before running** — write `save.md` first, then proceed:
- Package install or remove (pip, npm, cargo, apt)
- Environment variable writes, .env changes
- Schema migrations; deleting files; renaming files across modules
- git merge, rebase, cherry-pick
- Writing outside CWD; any `--force` flag (outside git push/reset)

**Never without human approval** — stop immediately, write `save.md`, do not execute:
- git push --force; git reset --hard; git branch -D
- Drop or truncate database tables
- Production environment writes
- Secret or credential-bearing commands
- CI/CD configuration changes; bulk file deletion

### Checkpoint cadence
Trigger a checkpoint (write `save.md`, pause) when:
- 20+ tool invocations since the last checkpoint or session start
- 2+ consecutive low-information results in impl mode
- Before any checkpoint-class mutation (see mutation policy above)
- Change scope expands beyond the preflight contract
- Confidence drops below MEDIUM

At checkpoint: write `save.md` with current state, `### What Changed`, and `### Preflight` (original contract).
