# thrashl evals

This directory contains small deterministic behavior evals for thrashl.

The first eval, `impl-first-failure`, checks that `/impl` behaves like a bounded execution mode:

- make one bounded change
- run one validation command
- stop immediately on meaningful failure
- write a replayable handoff
- route to `Debugger` instead of self-debugging

## Layout

- `fixtures/` — versioned benchmark definitions
- `runs/` — per-run workspaces (gitignored)
- `results/` — per-run score output (gitignored)

## Usage

Prepare a run workspace:

```bash
python3 evals/runner.py prepare impl-first-failure
```
