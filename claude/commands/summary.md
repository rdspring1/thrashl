---
description: Produce a high-signal summary for handoff or stopping
---

Produce a structured SUMMARY using this exact format.

SUMMARY
Mode:
<Implementer|Debugger|Reviewer|Navigator>

Status:
<STOPPED|READY_TO_PROCEED|BLOCKED_ON_CONTEXT|NEEDS_REVIEW>

Goal:
<current objective>

Current state:
<where things stand now>

What I want to do next:
<one concrete next action>

Why:
<why this is the best next step>

Expected outcome:
<what should happen if correct>

Confidence:
<HIGH|MEDIUM|LOW|VERY_LOW>

Risk:
<LOW|MEDIUM|HIGH>

Evidence:
- <item>
- <item>

What changed:
- <item or NONE>

What failed or blocked progress:
- <item or NONE>

Missing context:
- <item or NONE>

Needs from user:
- <only if truly required, otherwise NONE>

Best next mode:
<Implementer|Debugger|Reviewer|Navigator|NONE>

Rules:
- If you are stopping, do not merely describe the problem.
- Produce a high-signal handoff that lets the next mode or the user act immediately.
- Prefer one concrete next action over a vague menu of options.

Context:
$ARGUMENTS
