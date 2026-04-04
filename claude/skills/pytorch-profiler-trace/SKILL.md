---
name: pytorch-profiler-trace
description: >
  Use when the user wants to profile a PyTorch program with torch.profiler,
  identify CPU/CUDA hotspots, inspect kernel or stream timing, understand CUDA
  Graph behavior, profile distributed or NCCL overlap, or when they mention
  "torch.profiler", "PyTorch profiler", "profiler trace", "key_averages",
  "export_chrome_trace", "hotspot", "kernel timing", "dataloader overhead",
  "profiler schedule", "TensorBoard profiler", or "profile step".
---

## Purpose

Capture and interpret PyTorch profiler traces for training and inference programs on GPU nodes. The primary goal is to identify CPU/CUDA hotspots, stream timing, and overhead patterns quickly — not to provide a torch.profiler tutorial. Public docs cover the API; this skill encodes practical setup choices.

## Input routing

| Input | Action |
|---|---|
| Training loop or function | Wrap with `torch.profiler.profile` + schedule |
| Goal: quick hotspot | `activities=[CPU, CUDA]`, `record_shapes=False`, `key_averages()` summary |
| Goal: kernel / stream timing | `activities=[CUDA]`, `export_chrome_trace()` for timeline view |
| Goal: CUDA Graph behavior | Wrap graph capture + replay; use `nsys-trace-profiler` for node-level timing |
| Goal: distributed / NCCL overlap | `activities=[CPU, CUDA]`; look for NCCL gaps in Chrome trace |
| Goal: dataloader overhead | Profile with and without data loading; isolate host-side gap |
| Goal: timeline sanity check | `export_chrome_trace()` → open in `chrome://tracing` or Perfetto |
| Duration / step hint | Use `schedule(wait=N, warmup=1, active=M)` |
| Distributed hint | Run profiler on rank 0 only; export per-rank traces separately |

## Default output format

```
PROFILE INSIGHT

What to collect first:
<which profiler setup and why it is the right starting point>

Exact setup:
<copy-pasteable torch.profiler code block>

What to inspect:
<2-4 specific things to look for in the summary or trace>

Best next step:
<if the first trace is insufficient or needs deeper inspection>

Caveats:
<overhead warnings, graph-specific notes, or when nsys is the better tool>
```

## Behavior rules

1. **Insight-first.** Explain what to profile and why before showing code. Never lead with a raw API dump.
2. **Code must be exact and copy-pasteable.** No placeholder pseudocode. Every snippet must run as written with the user's training loop.
3. **Start with the lightest useful trace.** Avoid `profile_memory=True`, `with_stack=True`, or `with_flops=True` unless the goal requires them — each adds significant overhead.
4. **Always specify the schedule.** Use `schedule(wait=1, warmup=1, active=N)` by default to skip cold-start noise. Never profile a training loop without a schedule.
5. **Distinguish summary from timeline.** `key_averages().table()` for hotspot diagnosis; `export_chrome_trace()` for timeline and overlap inspection. Recommend the right one for the goal.
6. **Say explicitly when nsys is the better tool.** CUDA Graph node-level timing and system-wide CPU/GPU overlap require Nsight Systems — say so directly and name the skill (`nsys-trace-profiler`).
7. **Follow the fallback policy.** Emit one best setup, then 1–2 concrete fallbacks. Do not list many equivalent profiler variants.
8. **Separate what the profiler shows from what is inferred.** Distinguish raw numbers from interpretation.

## Fallback policy

Three-tier fallback for when the first trace is insufficient:

- **Direct path:** `profile(activities=[CPU, CUDA], schedule=...) + key_averages().table()` — lightweight summary for hotspot identification.
- **Fallback 1:** add `export_chrome_trace()` for timeline view; or narrow to `activities=[CUDA]` only to reduce overhead; or isolate a single step with `active=1`.
- **Fallback 2:** switch to `nsys-trace-profiler` for system-level CPU/GPU overlap, CUDA Graph node timing, or NCCL kernel-level inspection not visible in torch.profiler.
- **Stop:** after 2 fallbacks, summarize what was measured and what is still unknown.

See `references/fallback-table.md` for the full decision table with 8 specific scenarios.

## Key API notes

- `ProfilerActivity.CPU` — CPU operators and Python overhead.
- `ProfilerActivity.CUDA` — CUDA kernel execution times (device-side).
- `record_shapes=True` — records tensor shapes; ~10% overhead; use when shape variation is suspected.
- `profile_memory=True` — tracks allocations and frees; heavy overhead; only for memory investigations.
- `with_stack=True` — Python call stacks; heavy; only for Python-level attribution.
- `with_flops=True` — FLOPs estimate for supported ops; lightweight; useful for roofline context.
- `schedule(wait, warmup, active, repeat)` — `wait` skips steps entirely; `warmup` warms without recording; `active` records.
- `on_trace_ready=tensorboard_trace_handler('./log')` — writes TensorBoard-compatible trace per active window.
- CUDA Graphs: torch.profiler shows graph launches as a single block. For per-node breakdown, use `nsys-trace-profiler`.
- Distributed: run profiler on rank 0 only (`if dist.get_rank() == 0`); export per-rank if cross-rank comparison is needed.

## Relationship to nsys-trace-profiler

torch.profiler gives Python-level and CUDA kernel visibility within the PyTorch runtime. `nsys-trace-profiler` gives system-level CPU/GPU timeline, CUDA Graph node execution, and NCCL kernel timing. Use torch.profiler first for Python-level hotspot diagnosis; escalate to nsys when you need the full system view or CUDA Graph node detail.

## Reference files

- `references/commands.md` — torch.profiler API reference + common setups per goal
- `references/fallback-table.md` — decision table for 8 common failure scenarios
- `references/trace-guide.md` — reading profiler summary and Chrome traces; common pathologies; nsys handoff guide
- `scripts/profile-snippet.py` — ready-to-use profiler templates for hotspot, graph, and distributed goals
