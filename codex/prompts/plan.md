Use this prompt when the task needs narrowing before execution.

```
You are in PLAN MODE.

Goal:
Reduce ambiguity and produce the smallest viable execution plan.

Rules:
- Keep the plan short.
- Prefer one proposed path, not a menu of equivalent options.
- Call out missing context only if it materially changes implementation or debugging.
- Do not start implementing while planning.

Output shape:

PLAN NOTE

Goal:
<objective>

Current constraints:
- <item>

Recommended path:
1. <step>
2. <step>
3. <step>

Why this path:
<reason>

Stop condition:
<what would cause a switch to debug, vet, or save>

Best next mode:
<impl|debug|vet|clarify|save|NONE>
```
