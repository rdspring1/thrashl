---
name: nsys-trace-profiler
description: >
  Use when the user wants to profile a CUDA program with Nsight Systems (nsys),
  capture a CUDA timeline, inspect kernel launches, measure CPU/GPU overlap,
  understand CUDA Graph behavior, or when they mention "nsys", "Nsight Systems",
  "nsys profile", "CUDA trace", "launch latency", "CUDA Graph trace", "graph replay",
  "CPU/GPU overlap", "timeline", "synchronization stall", or "idle gap".
---

## Purpose

Capture and interpret Nsight Systems traces for CUDA programs running in an interactive Docker or GPU-node session. The primary goal is to get a practical, minimal trace quickly — not a comprehensive Nsight tutorial. Public docs are sparse for many behaviors; the trace is the source of truth.

## Input routing

| Input | Action |
|---|---|
| Command to profile | Use `scripts/capture-trace.sh` or inline nsys pipeline |
| Goal: basic CUDA trace | Minimal `-t cuda,nvtx` trace |
| Goal: launch latency | Add `-t osrt` to expose CPU API overhead |
| Goal: CUDA Graph behavior | Add `--cuda-graph-trace=node` |
| Goal: CPU/GPU overlap | `-t cuda,nvtx,osrt`; inspect timeline gaps |
| Goal: graph replay / launch path | `--cuda-graph-trace=node`; inspect node execution vs. capture |
| Goal: idle gaps / sync stalls | `-t cuda,nvtx,osrt`; search for `cudaStreamSynchronize` patterns |
| Duration hint or scope hint | Use `--duration` or `--capture-range=cudaProfilerApi` |
| NCCL / distributed hint | Add `nccl` to `-t` trace categories |

## Default output format

```
TRACE INSIGHT

What to collect first:
<which trace and why it is the right starting point>

Exact command:
<copy-pasteable nsys command>

What to look for in the report:
<2-4 specific things to inspect in the timeline or nsys stats output>

Best next command:
<if the first trace is insufficient or needs deeper inspection>

Caveats:
<if behavior is graph-specific, version-specific, or underdocumented>
```

## Behavior rules

1. **Insight-first.** Explain what trace to run and why before showing the command. Never lead with a flag dump.
2. **Commands must be explicit and copy-pasteable.** No placeholder pseudocode. Every command shown must run as written given the user's binary or command.
3. **Choose the minimal trace first.** Use a narrow `-t` scope. Do not default to a full multi-category trace unless the goal requires it.
4. **Explicitly address CUDA Graphs when mentioned or suspected.** Use `--cuda-graph-trace=node` and explain capture vs. replay semantics.
5. **Always specify the output file.** Use `-o` explicitly with a descriptive name. Never rely on nsys default naming.
6. **Follow the fallback policy.** Do not emit multiple variant commands. Choose one best command, then have 1–2 ready fallbacks.
7. **Do not escalate prematurely.** After 2 fallbacks, stop and summarize what was captured and what is still missing.
8. **Separate what the trace shows from what is inferred.** Distinguish raw timeline data from interpretation.

## Fallback policy

Three-tier fallback for when the first trace is insufficient:

- **Direct path:** minimal `-t cuda,nvtx` trace scoped to the whole run.
- **Fallback 1:** add `osrt` for CPU-side visibility, or add `--cuda-graph-trace=node` for graph cases, or shorten with `--duration`.
- **Fallback 2:** scope trace via `--capture-range=cudaProfilerApi` (requires code instrumentation), or switch to `nsys stats` text summary from an existing report.
- **Stop:** after 2 fallbacks, summarize what was captured, what the trace shows, and what is still missing.

See `references/fallback-table.md` for the full decision table with 8 specific scenarios.

## Version / environment notes

- All commands assume `nsys` is in the container's PATH. Run `nsys --version` to confirm.
- `--cuda-graph-trace=node` available since nsys 2022.x; if the flag is rejected, check version.
- GPU hardware metrics (`--gpu-metrics-device`) require root or specific container capabilities; omit if unavailable and not critical.
- Default output is `.nsys-rep`; use `nsys stats <file>.nsys-rep` for text summary without the Nsight GUI.
- For NCCL tracing: add `nccl` to `-t`; requires NCCL ≥ 2.12 and nsys ≥ 2022.3.
- `--force-overwrite=true` is safe to use by default; without it nsys will refuse to overwrite an existing report.

## Reference files

- `references/commands.md` — compact flag reference for nsys and nsys stats; copy-pasteable pipelines per goal
- `references/fallback-table.md` — decision table for 8 common failure scenarios
- `references/trace-guide.md` — timeline layer guide, launch latency, graph capture/replay, overlap, idle gap patterns
- `scripts/capture-trace.sh` — goal-driven nsys wrapper with automatic flag selection and stats summary
