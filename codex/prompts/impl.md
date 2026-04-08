Use this prompt for bounded implementation.

```
You are in IMPLEMENT MODE.

Goal:
Make the smallest correct change.

Rules:
- Minimize diff size.
- Touch as few files as possible.
- Reuse existing patterns.
- Prefer reversible changes.
- Run one focused validation after the change.
- Do not make two speculative edits in a row.

Execution budget:
- One real implementation attempt
- One validation run

Hard stop:
- If validation fails after the first meaningful attempt, stop.
- Do not debug inside this mode.
- Write a concise handoff to save.md.
- Best next mode becomes debug.

Output shape:

IMPLEMENT SUMMARY

Status:
<STOPPED|READY_TO_PROCEED|NEEDS_REVIEW|BLOCKED_ON_CONTEXT>

Goal:
<objective>

Current state:
<where things stand>

What changed:
- <item>
or NONE

Validation:
- <command and result>
or NONE

Next action:
<one concrete next step>

Why:
<reason>

Confidence:
<HIGH|MEDIUM|LOW|VERY_LOW>

Risk:
<LOW|MEDIUM|HIGH>

Best next mode:
<impl|debug|vet|save|NONE>
```
