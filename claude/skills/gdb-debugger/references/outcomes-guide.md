# outcomes-guide.md — interpreting common GDB outcomes

## 1. Followed wrong process

**Symptom:** GDB is in parent but the crash or bad state is in the child (or vice versa). The breakpoint never fires, or the program exits cleanly under GDB but crashes outside it.

**Action:**
- Restart with `set follow-fork-mode child` (or parent) and re-run.
- Or: attach a second GDB session to the other process via `gdb -p <other_pid>`.
- Check `info inferiors` to see which process GDB is currently tracking.

---

## 2. Missed the race window

**Symptom:** GDB stops at a breakpoint but the race-sensitive state has already resolved — the variable is already correct, the fd is already closed, etc.

**Action:**
- Move the breakpoint earlier in the call chain, closer to the shared-state modification.
- Replace the breakpoint with a watchpoint on the shared variable (`watch <var>`) — watchpoints fire on the exact write, not at a fixed location.
- If the race is very tight, `strace -f` may expose the interleaving without the timing perturbation of GDB.

---

## 3. Deadlock / hang suspected

**Symptom:** Program is running but makes no progress. No crash, no exit.

**Action:**
1. Attach GDB to the parent: `gdb -p <parent_pid>`
2. Run: `thread apply all bt` — look for threads blocked on `futex_wait`, `pthread_mutex_lock`, `sem_wait`, or similar.
3. Attach second GDB to the child (or other rank): repeat `thread apply all bt`.
4. Compare: find the thread holding the lock (it will be in `pthread_mutex_lock` on the *other* thread's mutex) vs. the thread waiting for it.
5. If all threads are in `futex_wait` with no obvious holder: check for a deleted or corrupt mutex.

---

## 4. Crash before breakpoint

**Symptom:** Process crashes (SIGSEGV, SIGABRT, etc.) during startup or dynamic linking, before any user breakpoints fire.

**Action:**
- Use `catch signal SIGSEGV` (or the relevant signal) before `run`:
  ```
  gdb -ex "set breakpoint pending on" -ex "catch signal SIGSEGV" -ex run --args ./binary args
  ```
- This stops at the signal delivery point regardless of where it occurs.
- After stopping: `bt`, `info registers`, `x/4xw $rsp` to inspect the crash site.
- If crash is in a shared library not yet mapped: `set breakpoint pending on` and try `break <lib_func>` before run.

---

## 5. Breakpoint only hits one side

**Symptom:** Breakpoint fires in parent but never in child (or vice versa), even though both should execute that code path.

**Action:**
- Run `info inferiors` to confirm which process GDB is tracking after the fork.
- If `detach-on-fork on`: GDB released the other process — it won't stop there. Switch to `set detach-on-fork off` and use `inferior N` to set a matching breakpoint in the other inferior.
- If `follow-fork-mode parent`: GDB is in parent; child runs free and won't hit GDB breakpoints. Attach a second GDB to the child PID to set breakpoints there.
- Note: breakpoints are per-inferior by default; a breakpoint set before fork does not automatically apply to the child in all GDB versions.
