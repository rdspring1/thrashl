---
description: Non-interrupting state-snapshot grounded in debug-session.md or explicit conversation entries
---

You are in CHECK MODE.

Goal:
Report the current debug session state from externally grounded sources only.

Default behavior:
- Read `debug-session.md` in the current directory if present.
- If no session file, fall back to ledger entries explicitly visible in the conversation.
- Do not reconstruct state from inferred reasoning or vibes.
- If no session file and no legible ledger in conversation, say so and stop.

Core rules:
- Source everything from `debug-session.md` if present, otherwise from explicit conversation entries only.
- Do not reconstruct state from inferred reasoning or vibes.
- Omit empty sections.
- If no session note and no legible ledger in conversation, say so and stop.
- If `debug-session.md` contains a Lane or Skill entry, report it; otherwise report UNKNOWN / NONE.

Don't-ask-me zone:
Do not interrupt the user for:
- choosing what to include
- interpreting ambiguous ledger entries
- deciding how to label confidence

Only ask the user if one of these is true:
- the session file is present but unreadable or corrupt
- the ledger entries are contradictory and interpretation would materially change the state report

Handoff conditions:
Stop after producing the state snapshot. This is a one-shot read-only command.

Output format:

CURRENT STATE

Goal:
<what this session is trying to accomplish>

Leading hypothesis:
<top hypothesis — sourced from debug-session.md or explicit conversation statement>

Current lane: <above-python | python-framework | perf-framework | perf-system | native-runtime | toolchain | UNKNOWN>
Active skill: <skill name or NONE>

Experiment ledger:
1. <hypothesis tested> | <exact change or command> | <result> | <interpretation>
2. ...

Current direction:
<what the current experiment is testing and why — grounded in ledger>

Would change course if:
<specific observable result that would pivot>

Confidence: <HIGH|MEDIUM|LOW|VERY_LOW>

Blocker:
<exact missing context — not vague>

Context:
$ARGUMENTS
