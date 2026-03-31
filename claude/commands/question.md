---
description: Answer a specific codebase question using repo evidence
---

You are in QUESTION MODE.

Goal:
Answer a specific codebase question using evidence from this repo.

Core rules:
- Answer the question directly first.
- Ground the answer in codebase evidence, not generic intuition.
- Point to relevant files, functions, symbols, or call paths.
- Be concise but specific.
- Do not implement anything unless explicitly asked.
- If the repo does not contain enough evidence, say exactly what is unclear or missing.
- If you are stopping, do not merely describe the problem. Produce a high-signal handoff that lets the next mode or the user act immediately.

Don't-ask-me zone:
Do not interrupt the user for:
- straightforward repo exploration
- locating obvious symbols or files
- tracing ordinary call paths
- summarizing code structure

Only ask the user if one of these is true:
- the question depends on missing functional-doc or hardware-context knowledge
- multiple interpretations are plausible and materially different
- the repo evidence is insufficient

Output format:

QUESTION ANSWER

Answer:
<direct answer>

Relevant files / symbols:
- <file / symbol>
- <file / symbol>

Why I think this:
- <reason 1>
- <reason 2>

Unclear / missing context:
- <item>
or NONE

Best next mode:
<Navigator|Debugger|Implementer|Reviewer|NONE>

Question:
$ARGUMENTS
