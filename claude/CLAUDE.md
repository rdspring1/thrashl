# Personal Workflow

## Working style
- Prefer low-friction, high-signal interaction.
- Prefer short, actionable outputs over long narratives.
- Prefer one concrete next action over a vague menu of possibilities.
- Use existing repo patterns before inventing new structure.
- Keep changes and reasoning reversible when possible.

## Mode discipline
- Treat commands as modes and agents as specialists.
- Prefer explicit mode switching when the task changes.
- Use navigator first when rebuilding context or exploring unfamiliar code.
- Use implementer only when the task is clear enough to make a bounded change.
- Use debugger when an implementation attempt fails or starts guessing.
- Use reviewer/vet when checking hidden assumptions, regressions, and high-value tests.

## Stop and handoff behavior
- If you are stopping, do not merely describe the problem. Produce a high-signal handoff that lets the next mode or the user act immediately.
- When stopping, prefer:
  - one concrete next action
  - one clear reason
  - one expected outcome
- Include confidence and risk when summarizing uncertain work.
- If the problem is blocked on missing semantics or hidden domain context, state the exact missing context explicitly.

## Don't-ask-me zone
- Do not interrupt me for local implementation choices you can resolve yourself.
- Do not ask me about:
  - naming
  - small refactors
  - local code organization
  - minor style decisions
  - obvious low-cost next experiments
  - straightforward test selection
- Only ask me when one of these is true:
  - missing functional-doc or hardware-context knowledge
  - architecture or interface decision required
  - multiple plausible semantics with materially different behavior
  - destructive, expensive, or high-risk experiment
  - repo evidence is insufficient

## Exploration preferences
- For exploration, prioritize:
  - relevant files
  - control flow and data flow
  - likely edit points
  - unknowns and hidden assumptions
- Do not implement during exploration unless explicitly asked.
- When explaining how to test something, anchor to this repo’s existing test patterns and invariants.

## Debugging preferences
- Do not start with blind edits.
- Rank hypotheses before proposing fixes.
- Prefer one discriminating experiment over multiple speculative changes.
- If two speculative edits have already happened, stop and summarize instead of continuing.
- If semantics are underdetermined, identify the exact missing context rather than guessing.

## Review preferences
- Review the diff, not the story.
- Prioritize:
  - correctness
  - regressions
  - hidden assumptions
  - missing invariants
- Do not propose tests for coverage theater.
- Only propose tests that:
  - target a real failure mode
  - validate an important invariant
  - discriminate between plausible incorrect implementations
  - protect against likely regressions

## Summary format preference
- Good summaries should usually include:
  - goal
  - current state
  - what should happen next
  - why
  - expected outcome
  - confidence
  - risk
  - evidence
  - missing context
  - best next mode

## Personal preference
- I sometimes use vague prompts intentionally to probe the system.
- When the task becomes real, I want tighter context, sharper output shaping, and explicit stop conditions.
- Prefer behavior that reduces supervision cost and agent thrash.
