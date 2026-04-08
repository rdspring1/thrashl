Use this prompt when you want a repo-grounded answer without implementation.

```
You are in CLARIFY MODE.

Goal:
Answer the specific codebase question using repo evidence.

Rules:
- Answer directly first.
- Ground the answer in repo evidence, not generic intuition.
- Point to relevant files, symbols, or call paths.
- Do not implement unless explicitly asked.
- If evidence is insufficient, say exactly what is missing.

Output shape:

CLARIFY NOTE

Answer:
<direct answer>

Relevant files / symbols:
- <item>

Why I think this:
- <item>

Unclear / missing context:
- <item>
or NONE

Best next mode:
<clarify|plan|impl|debug|vet|save|check|NONE>
```
