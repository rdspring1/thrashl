Use this prompt for a read-only state snapshot.

```
You are in CHECK MODE.

Goal:
Report the current session state from grounded sources only.

Views:
- Active introspection:
  1. explicit current-session ledger entries
  2. debug-session.md
  3. save.md
- Replay or resume:
  1. save.md
  2. debug-session.md only as separately labeled active debug state

Rules:
- Be explicit about whether you are reporting active-session state or replay/resume state.
- For replay or resume state, treat save.md as the source of truth.
- If save.md is absent for replay or resume state, report:
  `No durable save snapshot found.`
- Do not treat absent save.md as failure.
- If debug-session.md exists while save.md is absent, report it only as active
  debug state, not as the durable replay snapshot.
- Stop at the first legible source for the chosen view.
- Do not merge contradictory sources.
- Do not reconstruct state from vibes.
- If debug-session.md includes lane, skill, Canonical, or Failure-class, report them.
- If no legible source exists, say so and stop.

Output shape:

CURRENT STATE

Goal:
<goal>

Leading hypothesis:
<top sourced hypothesis>

Current lane:
<lane or UNKNOWN>

Active skill:
<skill or NONE>
Last command: <exact command from most recent ledger entry, or UNKNOWN>
Repo invocation match: <YES | NO | UNKNOWN>
Repeat failure count: <N — identical error with no meaningful change between runs | 0>

Experiment ledger:
1. <entry>

Current direction:
<what the latest experiment is testing and why>

Would change course if:
<pivot condition>

Confidence:
<HIGH|MEDIUM|LOW|VERY_LOW>

Blocker:
<exact missing context>

Blocker classification: <code | invocation | environment | requirement | UNKNOWN>
```
