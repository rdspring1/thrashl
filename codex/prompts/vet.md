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

Surgical Simplicity review:
For each changed line, judge whether it traces to the task, a real
failure mode, or a verified invariant. List under Blocking concerns
any of:
- new helpers / functions with exactly one callsite
- new config knobs, parameters, or flags with no current consumer
- defensive try/except, null checks, or fallbacks for impossible states
- edits to adjacent code not required by the task (drive-by refactors)
- new test files when an existing test could be extended
- monkeypatch / mock / fixture scaffolding without a one-sentence
  justification
- new files when an existing file would work

For each, propose the smaller form (inline the helper, remove the
knob, delete the defensive branch, fold into existing test).

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
