---
name: pdb-debugger
description: >
  Use when the user wants to debug a Python program interactively with pdb or
  breakpoint(), or when they mention "pdb", "Python debugger", "breakpoint",
  "set_trace", "torchrun debug", "dataloader hang", "Python hang", "Python crash",
  "tensor state", "wrong output", "bad gradient", or want to inspect Python-side
  control flow, exceptions, or process state interactively.
---

## Purpose

Drive interactive pdb sessions for Python programs in Docker/GPU-node sessions. The goal is to test or falsify a specific hypothesis as quickly as possible — not to provide a pdb tutorial. Covers single-process Python, torchrun multiprocess, and dataloader worker scenarios.

## Input routing

| Input | Action |
|---|---|
| Python script or launch command | Launch under `python -m pdb` or inject `breakpoint()` |
| Bug description: exception / crash | Use `python -m pdb` with `c` to run to exception; inspect frame |
| Bug description: hang | Use `faulthandler` + SIGUSR1 or `-X faulthandler`; check for C extension deadlock |
| Bug description: wrong output / bad tensor | Break at suspect location; inspect `.shape`, `.dtype`, `.min()`, `.max()` |
| Bug description: control flow | Conditional breakpoint at decision point; step through branch |
| Hint: torchrun / multiprocess | Use `torch.distributed.breakpoint(rank=0)` or run rank 0 standalone under pdb |
| Hint: dataloader workers | Set `num_workers=0` to debug in main process; workers can't use pdb directly |
| Hint: hang with no Python frame | Switch to faulthandler or `gdb-debugger` — likely a C extension deadlock |
| Hint: crash (SIGSEGV / SIGABRT) | Switch to `gdb-debugger` — below Python level |

## Default output format

```
DEBUG MOVE

Hypothesis:
<what we are testing or trying to expose>

Command:
<exact pdb command or shell command>

Why:
<1-2 sentences>

Confirms if:
<what output or behavior would confirm the hypothesis>

Weakens if:
<what would falsify or redirect the hypothesis>

Next move:
<the single best next pdb command after this one>
```

## Behavior rules

1. **Hypothesis-first.** Start from the user's hypothesis or infer one from the bug description. Drive toward testing or falsifying it — not toward a generic pdb walkthrough.
2. **Commands must be exact and copy-pasteable.** No pseudocode. Every command must run as written in pdb or the shell.
3. **Prefer the shortest path to the bug.** Default to `launch-under-pdb`. Escalate to `breakpoint()`-injection or faulthandler only when launch-under-pdb is insufficient.
4. **Explicitly say when pdb is no longer the right tool.** If the hang has no Python frame, or the crash is a SIGSEGV, say so directly and name the right tool (`gdb-debugger`, faulthandler, profiler).
5. **Address multiprocess explicitly when present.** torchrun and dataloader workers have well-known pdb limitations; give the working pattern, not a generic pdb command.
6. **One best next command, not a menu.** When evidence is weak, pick the single most discriminating command.
7. **Follow the fallback policy.** Try launch-under-pdb first. If insufficient, escalate to faulthandler or worker-specific strategy. After 2 fallbacks, stop and summarize.
8. **Separate what pdb shows from what is inferred.** Distinguish raw output from interpretation.

## Fallback policy

Three-tier fallback for when the first approach is insufficient:

- **Direct path:** `python -m pdb script.py args` — run to exception or breakpoint.
- **Fallback 1:** inject `breakpoint()` at the suspect location and rerun; or use `torch.distributed.breakpoint(rank=0)` for torchrun; or set `num_workers=0` for dataloader issues.
- **Fallback 2:** use `python -X faulthandler script.py` + `kill -SIGUSR1 <pid>` for hangs; if the stack shows a C extension deadlock, hand off to `gdb-debugger`.
- **Stop:** after 2 fallbacks, summarize what was observed and what tool or context is needed next.

See `references/debug-checklist.md` for the pdb → gdb / other tool switch decision table.

## Python debugging notes

- `python -m pdb script.py` — launch under pdb; stops at first line.
- `breakpoint()` — drops into pdb at that line; works without relaunching.
- `PYTHONBREAKPOINT=0` — disable all `breakpoint()` calls (useful to silence workers).
- `python -X faulthandler script.py` — enables faulthandler; dumps threads on SIGUSR1 or segfault.
- `torch.distributed.breakpoint(rank=0)` — PyTorch 2.0+; pdb fires on rank 0 only; other ranks continue.
- Dataloader workers: `num_workers=0` forces single-process data loading; pdb works normally.
- torchrun with pdb: do not use pdb inside torchrun directly — it conflicts with process management. Run rank 0 standalone or use `torch.distributed.breakpoint`.
- If Python stack shows all threads in `<built-in>` or no frame: the hang is in a C extension; switch to `gdb-debugger`.

## Relationship to /debug and gdb-debugger

`/debug` handles hypothesis ranking from code and logs (`DEBUG NOTE`). This skill drives the live pdb session (`DEBUG MOVE`). If the bug is below Python level (C extension deadlock, segfault), hand off to `gdb-debugger`.

## Reference files

- `references/commands.md` — compact pdb command reference + common launch pipelines per scenario
- `references/debug-checklist.md` — Python/torchrun/dataloader checklist + pdb→gdb switch decision table
- `references/outcomes-guide.md` — 5 common outcomes: wrong process/worker, exception before breakpoint, hang with no Python frame, incorrect tensor state, bug below Python level
- `scripts/pdb-launcher.sh` — copy-pasteable launch templates for common scenarios
