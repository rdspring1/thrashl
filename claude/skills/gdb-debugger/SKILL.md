---
name: gdb-debugger
description: >
  Use when the user wants to run a GDB session on a multiprocess program, debug
  a race condition, hang, deadlock, or crash, or when they mention "gdb",
  "debugger", "attach", "fork", "exec", "clone", "follow-fork", "parent/child",
  "race condition", "hang", "deadlock", "segfault", "crash", "catchpoint",
  "watchpoint", "scheduler-locking", or "dual-session".
---

## Purpose

Drive interactive GDB sessions for multiprocess programs with races, hangs, deadlocks, and crashes inside Docker containers on GPU nodes. The goal is to test or falsify a specific hypothesis as quickly as possible — not to provide a GDB tutorial.

## Input routing

| Input | Action |
|---|---|
| Binary or launch command | Launch under GDB with appropriate fork/exec settings |
| Bug description: race | Set `catch fork`/`exec`, decide `follow-fork-mode`, prepare dual-session |
| Bug description: hang / deadlock | `thread apply all bt`, inspect mutexes, find blocking syscall |
| Bug description: crash | `catch signal SIGSEGV`, run to crash, inspect backtrace and registers |
| Hint: forks / execs / clones | Set `catch fork`/`exec`/`clone`, configure `detach-on-fork` |
| Hint: parent/child race | Start with follow-parent, attach child separately if needed |
| Hint: attach needed | Use `attach <pid>`; acquire PID list first with `pgrep` or `ps` |
| Hint: existing PIDs | Attach directly; no launch needed |
| Hint: NCCL / distributed | Multi-rank: one GDB per rank via `mpirun` wrapper or explicit attach |

## Default output format

```
DEBUG MOVE

Hypothesis:
<what we are testing or trying to expose>

Command:
<exact GDB command or shell command>

Why:
<1-2 sentences>

Confirms if:
<what output or behavior would confirm the hypothesis>

Weakens if:
<what would falsify or redirect the hypothesis>

Next move:
<the single best next GDB command after this one>
```

## Behavior rules

1. **Hypothesis-first.** Start from the user's hypothesis or infer one from the bug description. Drive toward testing or falsifying it — not toward a generic GDB walkthrough.
2. **Commands must be exact and copy-pasteable.** No pseudocode. Every command shown must run as written in GDB or the shell.
3. **Prefer the shortest path to the race.** Default to `launch-under-gdb`. Escalate to attach or dual-session only when launch is insufficient.
4. **Tell the user explicitly when a second GDB session is the right move.** Do not hint — say it directly and provide the attach command.
5. **One best next command, not a menu.** When evidence is weak, pick the single most discriminating command instead of listing options.
6. **Manage fork/exec behavior explicitly.** Always state `follow-fork-mode` and `detach-on-fork` choices and why they were made.
7. **Follow the fallback policy.** Attempt launch-under-gdb first. If the race or timing makes it insufficient, escalate to attach-based or dual-session. After 2 fallbacks, stop and summarize.
8. **Separate what GDB shows from what is inferred.** Distinguish raw output from interpretation.

## Fallback policy

Three-tier fallback for when the first approach is insufficient:

- **Direct path:** launch binary under GDB with `catch fork`/`exec` and appropriate `follow-fork-mode`.
- **Fallback 1:** attach a second GDB session to the child (or parent) while keeping the first session frozen. Use `scripts/dual-attach.sh` as a template.
- **Fallback 2:** switch to a minimal reproducer — reduce env, args, or process count; or use `strace -f` to locate crash/hang point before returning to GDB.
- **Stop:** after 2 fallbacks, summarize what was observed, what is still unclear, and what context is missing.

See `references/race-checklist.md` for the launch-first vs. attach-first decision table.

## GDB multiprocess notes

- `set follow-fork-mode child` — GDB follows child after fork; parent runs free.
- `set follow-fork-mode parent` — GDB stays with parent; child runs free (default).
- `set detach-on-fork off` — GDB holds both; switch with `inferior N`.
- `catch fork` / `catch exec` / `catch clone` — stop at process creation events.
- `set scheduler-locking on` — freeze all threads except current (useful to isolate one side of a race).
- `set breakpoint pending on` — allow breakpoints in not-yet-loaded shared libraries.
- `handle SIGCHLD nostop noprint pass` — suppress SIGCHLD noise in parent sessions.
- Dual-session: open two terminals; attach GDB to parent PID in one, child PID in the other.

## Relationship to /debug

`/debug` handles hypothesis ranking from code and logs (`DEBUG NOTE`). This skill drives the live GDB session (`DEBUG MOVE`). Transition from `/debug` to this skill when the next discriminating experiment requires interactive GDB — not a code or log inspection.

## Reference files

- `references/commands.md` — compact GDB multiprocess command reference with common pipelines per scenario
- `references/race-checklist.md` — parent/child race checklist and launch-first vs. attach-first decision table
- `references/outcomes-guide.md` — interpreting common outcomes: wrong process, missed race, deadlock, crash before breakpoint, one-sided breakpoint
- `scripts/dual-attach.sh` — template for coordinating dual GDB sessions
