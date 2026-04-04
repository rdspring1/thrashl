# outcomes-guide.md — interpreting common pdb outcomes

## 1. Wrong process or worker

**Symptom:** pdb fires in the main process but the crash or wrong value originated in a dataloader worker or a non-zero torchrun rank. The frame looks unrelated to the bug.

**Action:**
- For dataloader: set `num_workers=0` and rerun — the worker code now runs in the main process and is fully debuggable with pdb.
- For torchrun: add `torch.distributed.breakpoint(rank=N)` at the suspect location in the rank you want to inspect.
- Confirm which process has the bad state: add a temporary `if rank == N: breakpoint()` guard.

---

## 2. Exception before breakpoint

**Symptom:** Python throws an exception before pdb reaches the breakpoint. The program exits (or raises) before the breakpoint location is hit.

**Action:**
- Use `python -m pdb script.py` and run `c` (continue) — pdb catches all unhandled exceptions automatically and drops into the frame at the exception site.
- Do not set a breakpoint first; let the exception bring pdb to the exact failure frame.
- At the exception frame: `bt` to see the full stack, `p locals()` to inspect state.

---

## 3. Hang with no useful Python frame

**Symptom:** `bt` inside pdb shows all threads blocked in `<built-in>`, `_wait`, or a C extension call (e.g., `nccl`, `cuda`, `pthread`). No Python-level frame shows the hang point.

**Action:**
1. Quit pdb if attached. Relaunch with `python -X faulthandler script.py args &` and capture `$PID`.
2. When hang suspected: `kill -SIGUSR1 $PID` — dumps all thread stacks to stderr without stopping the process.
3. Look for threads blocked on `futex_wait`, `sem_timedwait`, `pthread_cond_wait`, or NCCL collective calls.
4. If the blocking call is a C extension: hand off to `gdb-debugger` — attach with `gdb -p <pid>` and run `thread apply all bt`.

---

## 4. Incorrect tensor state

**Symptom:** A tensor has the wrong values, shape, dtype, or contains NaN/Inf. The computation produces wrong results.

**Action:**
1. Break at the point where the tensor is first created or last known-good.
2. At the breakpoint:
   ```
   (Pdb) p tensor.shape
   (Pdb) p tensor.dtype
   (Pdb) p tensor.min().item()
   (Pdb) p tensor.max().item()
   (Pdb) p tensor.isnan().any().item()
   (Pdb) p tensor.isinf().any().item()
   ```
3. Step forward through transformations, checking the tensor after each operation.
4. When the value first becomes wrong: that is the culprit operation. Walk up the stack with `u` to find the call site.
5. For NaN: use a conditional breakpoint — `b model.py:88, output.isnan().any().item()` — to catch the exact forward pass where NaN first appears.

---

## 5. Bug likely below Python level

**Symptom:** Repeated SIGSEGV, SIGABRT, or SIGILL; a C extension call with no Python traceback; or a hang that faulthandler cannot explain (all threads show `<built-in>` with no Python frames above them).

**Action:**
- pdb cannot help here. Hand off to `gdb-debugger`.
- For a crash: `gdb -ex "catch signal SIGSEGV" -ex run --args python script.py args`
- For a hang: `gdb -p <pid>`, then `thread apply all bt` to find the blocked C thread.
- Note the last Python frame visible before the crash (from faulthandler output or a partial traceback) — this is the starting point for GDB inspection.
