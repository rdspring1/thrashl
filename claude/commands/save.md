---
description: Save the current state as a concise markdown handoff
---

Produce a SAVE NOTE and write it to `save.md` in the current working directory.

`save.md` is the canonical state file. `/check`, `/debug`, and the next session read from it.

Default behavior:
- If no explicit context is provided, summarize the current conversation/task state.
- Infer the most recent goal, blocker, evidence, and best next step from:
  - the recent conversation
  - the current repo state
  - the latest visible summaries, failures, diffs, or conclusions
- If `debug-session.md` exists in the current directory, incorporate a summary of its experiment ledger into the Evidence section.
- Write the note to `save.md` in the current working directory using the Write tool.

Rules:
- If you are stopping, do not merely describe the problem.
- Produce a high-signal handoff that lets the next mode or the user act immediately.
- Prefer one concrete next action over a vague menu of possibilities.
- Omit trivial or empty sections.
- Be concise and decision-oriented.
- Be explicit about uncertainty and missing context.
- After producing the note, write it to `save.md` in the current working directory using the Write tool.

Output format:

# Save Note

## Goal
<current objective>

## Current State
<where things stand now>

## Next Action
<one concrete next action>

## Why
<why this is the best next step>

## Expected Outcome
<what should happen if correct>

## Confidence
<HIGH|MEDIUM|LOW|VERY_LOW>

## Risk
<LOW|MEDIUM|HIGH>

## Evidence
- <item>
- <item>

Optional sections: include only if meaningful
### What Changed
- <item>

### Blocker
- <item>

### Missing Context
- <item>

### Needs From User
- <item>

### Best Next Mode
<Implementer|Debugger|Reviewer|Navigator|NONE>

### Preflight  (required before autonomous runs; omit for interactive saves)
- Bounded scope: <files/modules in scope; what is explicitly out of scope>
- Canonical command: <exact run/test/build command>
- Stop condition: <what done looks like, or what triggers escalation>
- Risk level: <LOW|MEDIUM|HIGH>
- Expected artifact: <test result, file, or output when complete>

Context:
$ARGUMENTS
