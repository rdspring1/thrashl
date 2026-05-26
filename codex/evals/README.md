# Codex evals

This directory contains small deterministic behavior evals for the Codex port of `thrashl`.

The first eval, `codex-impl-first-failure`, checks that the Codex `impl` prompt still behaves like a bounded implementation mode:

- make one bounded change
- run one validation command
- stop immediately on meaningful failure
- write a replayable handoff to `save.md` when failure/blocker/replay value exists
- route to `debug` instead of self-debugging

`codex-impl-trivial-success-no-save` covers the opposite boundary: a tiny
successful one-file `impl` change should validate once and skip `save.md`.

## Layout

- `fixtures/` - versioned benchmark definitions
- `runs/` - per-run workspaces (gitignored)
- `results/` - per-run score output (gitignored)

## Manual usage

Prepare a run workspace:

```bash
python3 codex/evals/runner.py prepare codex-impl-first-failure
```

Then:

1. `cd <prepared-run>/repo`
2. Open Codex in that repo
3. Follow the task in `../SPEC.md` using `codex/prompts/impl.md`
4. Score with `python3 codex/evals/runner.py score <prepared-run>`
