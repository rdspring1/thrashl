# debug-checklist.md — Python / torchrun / dataloader debugging

## Checklist (ordered)

1. Identify which process is the victim: main process, rank N, or dataloader worker N.
2. If multiprocess: choose the right entry point before setting any breakpoints.
   - torchrun → use `torch.distributed.breakpoint(rank=0)` or run rank 0 standalone.
   - dataloader workers → set `num_workers=0` to debug in main process.
3. Form a hypothesis — exception, hang, wrong value, or wrong control flow.
4. Set the smallest breakpoint that reaches the suspect code path.
5. Use conditional breakpoints to skip irrelevant iterations (e.g., `b file:line, step > 100`).
6. At the breakpoint: inspect `bt`, `args`, `p <suspect_var>`.
7. For tensor bugs: `p t.shape`, `p t.dtype`, `p t.min().item()`, `p t.max().item()`, `p t.isnan().any().item()`.
8. If no useful Python frame in a hang: switch to faulthandler (`kill -SIGUSR1 <pid>`) to dump thread stacks without stopping the process.
9. If faulthandler shows threads blocked in `<built-in>` or a C extension: hand off to `gdb-debugger`.

## pdb → gdb / other tool switch decision table

| Situation | Right tool |
|---|---|
| Python exception with a traceback | pdb |
| Hang — Python threads visible with `bt` or faulthandler | pdb + thread inspection |
| Hang — all threads in `<built-in>` or blocked in C extension | faulthandler → `gdb-debugger` |
| SIGSEGV / SIGABRT / SIGILL | `gdb-debugger` |
| Slow kernel or memory throughput (not a crash) | `nsys-trace-profiler` |
| torchrun, all ranks need inspection simultaneously | `gdb-debugger` attach per rank, or `torch.distributed.breakpoint` per rank |
| Dataloader worker crash (persists after num_workers=0 fix) | `gdb-debugger` |
| Wrong CUDA kernel output (not Python-level) | `cuobjdump-lowering-inspector` |

## torchrun-specific notes

- `torch.distributed.breakpoint(rank=0)` — preferred; fires pdb only on rank 0, others wait at a barrier.
- Running rank 0 standalone: set `RANK=0 WORLD_SIZE=N MASTER_ADDR=localhost MASTER_PORT=29500 python -m pdb script.py` — works only if the script does not require all ranks to be alive.
- Do not use `breakpoint()` inside a torchrun job without `torch.distributed.breakpoint` — it breaks stdin/stdout for all other ranks and hangs the job.
- For per-rank debugging: use separate terminals and `torch.distributed.breakpoint(rank=N)` for each rank you want to inspect.

## Dataloader-specific notes

- `num_workers=0` is the first move for any dataloader bug — it makes the loader run in the main process where pdb works.
- If the bug disappears with `num_workers=0`: it is a worker-process isolation or serialization issue, not a data bug.
- If the bug persists: it is in the dataset/transform logic itself, debuggable with pdb normally.
- Worker crashes that produce `RuntimeError: DataLoader worker (pid N) is killed by signal Killed` or similar: check memory (OOM), not a Python-level bug.
