Use this prompt when you want a replayable session handoff in `save.md`.

```
Write a concise save note to save.md in the current working directory.

Rules:
- save.md is the canonical cross-session replay and resume artifact.
- Prefer one concrete next action over a vague menu.
- Omit trivial or empty sections.
- Be explicit about uncertainty and missing context.
- If debug-session.md exists, summarize the useful evidence from it without treating it as the replay source of truth.

Output shape:

# Save Note

## Goal
<current objective>

## Current State
<where things stand>

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

Optional sections:
### What Changed
### Blocker
### Missing Context
### Needs From User
### Best Next Mode
```
