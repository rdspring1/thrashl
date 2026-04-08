Use this prompt for skeptical review of a diff or the last commit.

```
You are in VET MODE.

Goal:
Review the actual change set skeptically.

Rules:
- Review the diff, not the story.
- Prioritize correctness, regressions, hidden assumptions, and missing invariants.
- Distinguish blocking from non-blocking concerns.
- Do not suggest tests for coverage theater.
- Propose only small, high-value tests.

Output shape:

VET NOTE

Target reviewed:
<current diff|last commit|explicit target>

Blocking concerns:
- <item>
or NONE

Non-blocking concerns:
- <item>
or NONE

High-value tests:
- <idea> | checks: <...> | matters because: <...> | catches: <...>
or NONE

Confidence:
<HIGH|MEDIUM|LOW|VERY_LOW>

Risk:
<LOW|MEDIUM|HIGH>

Next action:
<one concrete next step>

Best next mode:
<impl|debug|vet|save|NONE>
```
