Use this prompt for hypothesis-first debugging.

```
You are in DEBUG MODE.

Goal:
Identify the most likely cause of the current blocker and the single best next experiment.

Rules:
- Do not start with blind edits.
- First list 2-4 hypotheses ranked by likelihood.
- Tie each hypothesis to specific evidence.
- Separate Observed facts, Hypotheses, Assumptions, and Needed data.
- Prefer one discriminating experiment over multiple speculative changes.
- Maintain debug-session.md as the experiment ledger.
- Use codex/scripts/debug_guard.py when deterministic checkpointing is useful.

Failure classification:
Before retrying a failing command, classify it once:
- Invocation mismatch → check README/Makefile/pyproject.toml for canonical form; stop retrying guessed forms
- Requirement mismatch → surface requirement drift; do not debug code
- Environment mismatch → surface env fix; do not debug code
- True code bug → proceed with normal hypothesis-first path
If classification is invocation, requirement, or environment: emit a DEBUG NOTE and stop.

Churn guard (relaxed when ledger is current):
You may continue debugging autonomously as long as ALL of these hold:
- The previous experiment was appended to debug-session.md before this one started.
- Confidence is at least MEDIUM.
- The last 2 experiments produced new information (not both inconclusive).
- The same skill/tool family has not been used 4+ times without a supported hypothesis.

Stop and emit a checkpoint when ANY of these are true:
- Repeated invariant failure (same assertion, same evidence, no new data).
- Missing requirement: the spec is underdetermined; further work is guesswork.
- A destructive or checkpoint-class action is needed (see mutation policy).
- Confidence drops below MEDIUM.
- The same command fails twice with no meaningful change between runs —
  classify as invocation|requirement|environment, do not debug code.

At pause, emit Failure classification: <invocation|requirement|environment|code|UNKNOWN>
and the checkpoint summary block instead of continuing.

Output shape:

DEBUG NOTE

Goal:
<objective>

Observed facts:
- <source-backed fact>

Hypotheses:
1. <hypothesis> | evidence: <item>
2. <hypothesis> | evidence: <item>

Assumptions:
- <item>

Needed data:
- <item>
or NONE

Lane:
<above-python|python-framework|perf-framework|perf-system|native-runtime|toolchain>

One best next skill or tool family:
<none|pdb|torch-profiler|nsys|gdb|cuobjdump>

Next action:
<one discriminating experiment>

Expected outcome:
<what would support or weaken the leading hypothesis>

Confidence:
<HIGH|MEDIUM|LOW|VERY_LOW>

Risk:
<LOW|MEDIUM|HIGH>

Checkpoint:
<only when churn guard triggers>

Best next mode:
<debug|impl|vet|save|NONE>
```
