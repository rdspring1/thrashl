# race-checklist.md — parent/child race debugging

## Checklist (ordered)

1. Identify which process (parent or child) is the race victim — who observes the bad state?
2. Confirm whether fork, exec, or clone is involved — determines which catchpoint to use.
3. Set `catch fork`/`exec`/`clone` to stop at the creation boundary before the race window opens.
4. Choose `follow-fork-mode` based on which side to inspect first (usually the victim).
5. Decide `detach-on-fork`: off to hold both, on to let the non-victim run free.
6. Set breakpoints in the victim process at the race-sensitive code path.
7. Freeze the non-victim side (`set scheduler-locking on` or leave it detached) while inspecting the victim.
8. Check shared state at the race point: shared memory, file descriptors, mutexes, semaphores, pipes.
9. If GDB perturbation masks the race: try `strace -f` first to locate the crash/hang with less intrusion, then return to GDB with a tighter breakpoint.

## Launch-first vs. attach-first decision table

| Situation | Preferred approach |
|---|---|
| Race is in startup / early exec | Launch under GDB — `catch fork`/`exec` before race window opens |
| Process already running, hang in progress | Attach to PID — launch would miss the live state |
| Race is nondeterministic, timing-sensitive | Try launch first; if it masks the race, attach with minimal instrumentation |
| Need both parent and child visible simultaneously | Launch with `set detach-on-fork off`; switch inferiors as needed |
| Crash happens before GDB can set breakpoints | `gdb -ex "catch signal SIGSEGV" -ex run --args ./binary args` |
| Program execs into a different binary | Use `catch exec`; GDB re-stops after exec; reset breakpoints |
| PID is known, process is suspended | `gdb -p <pid>` directly |
| Multi-rank distributed (MPI/NCCL) | One GDB per rank; use `mpirun` wrapper or explicit attach per rank PID |

## When to open a second GDB session

Open a second session (dual-session) when:
- Both sides of the race need to be frozen and inspected independently
- One process must stay stopped while you step the other
- The race requires coordinating exactly when each side proceeds

Use `scripts/dual-attach.sh <parent_pid> <child_pid>` to generate the attach commands.
Run each in a separate terminal or tmux pane.
