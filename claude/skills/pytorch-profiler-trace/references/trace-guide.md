# trace-guide.md — reading PyTorch profiler output

## Reading key_averages() table

Key columns and what they mean:

```
Name            Op name: aten operator, custom kernel, or Python function via record_function()
Self CPU %      CPU time spent in this op alone (excludes child ops) — shows where CPU is burning
CPU total %     CPU time in this op + all children — shows call-tree cost
CPU total       Absolute CPU time (μs) — sort by this for CPU hotspots
CPU time avg    Average CPU time per call — high count + low avg = launch overhead
Self CUDA       CUDA time on device for this op only (μs) — sort by cuda_time_total for GPU hotspots
CUDA total      CUDA time including children
# of Calls      How many times this op fired — very high counts suggest loop-level overhead
```

Sort options for `key_averages().table(sort_by=...)`:
- `"cuda_time_total"` — GPU hotspots (default for CUDA diagnosis)
- `"cpu_time_total"` — CPU hotspots
- `"self_cpu_time_total"` — where CPU time is actually spent (not attributed to children)
- `"self_cuda_memory_usage"` — memory allocations (requires `profile_memory=True`)

## Reading a Chrome / Perfetto trace

Load `trace.json` in `chrome://tracing` or https://ui.perfetto.dev (handles larger files).

Timeline rows to look for:
- **Python thread rows** — Python-level ops and `record_function()` blocks; width = CPU time
- **CUDA stream rows** — kernel executions on the device; gaps = GPU idle time
- **`cudaLaunchKernel` rows** — CPU-side launch API calls; many short calls = launch overhead
- **`ncclKernel_*` rows** — NCCL collective kernels on CUDA streams
- **`ProfilerStep#N` blocks** — marks each profiler step; use to align with training iteration

What to look for:
1. **GPU idle gaps** — whitespace in CUDA stream rows; aligned with data loading → dataloader stall; aligned with allreduce → NCCL serialization
2. **CPU/GPU overlap** — GPU kernels running while CPU is submitting next batch = good; CPU idle while GPU runs = GPU bottleneck; CPU busy while GPU is idle = CPU bottleneck
3. **Launch overhead** — many `cudaLaunchKernel` calls packed tightly before the first kernel starts; consider CUDA Graphs
4. **Step boundaries** — compare step durations; outliers indicate GC, logging, or checkpoint overhead

## Common pathologies

**Host bottleneck (CPU-bound):**
- `key_averages()`: CPU total >> CUDA total
- Chrome trace: CUDA stream idle while Python thread is busy
- Fix: vectorize Python ops, reduce per-element Python, use `torch.compile`

**Launch overhead:**
- Chrome trace: many short `cudaLaunchKernel` calls; GPU starts late after CPU submits
- `key_averages()`: high `# of Calls` count on small ops
- Fix: fuse ops, use `torch.compile`, or CUDA Graphs for static graphs

**Missing overlap (compute/comm serialized):**
- Chrome trace: compute kernels finish → gap → NCCL allreduce → next compute
- Fix: ensure optimizer and backward are on different streams; use `torch.distributed` with `bucket_cap_mb` tuning

**Dataloader stall:**
- Chrome trace: regular GPU idle gaps aligned with iteration boundaries
- Confirm: profile with `num_workers=0` — if gaps disappear, loader is the cause
- Fix: increase `num_workers`, enable `persistent_workers=True`, prefetch to GPU

**Graph replay not helping:**
- Chrome trace: graph launch call takes as long as individual kernel launches
- `key_averages()`: no reduction in `# of Calls` or launch overhead
- Fix: check if graph is being re-captured each iteration; confirm `cudaGraphLaunch` is in the hot path

**NCCL serialization:**
- Chrome trace: allreduce blocks the start of next forward pass
- Fix: overlap with `DDP(find_unused_parameters=False)`, gradient bucketing, or ZeRO-style sharding

## When to escalate to nsys-trace-profiler

Switch to `nsys-trace-profiler` when:
- You need **CUDA Graph node-level timing** — torch.profiler shows graph launches as a single block
- You need a **full system-level CPU/GPU timeline** including non-PyTorch CUDA activity
- You need **NCCL kernel-level detail** with explicit stream rows
- torch.profiler overhead is distorting results even with minimal config
- You need to correlate **CPU thread scheduling** (OS-level) with GPU activity

Use `nsys-trace-profiler` with goal `graph` or `overlap` for these cases.

## Perfetto / chrome://tracing tips

- **Load:** drag `trace.json` onto `chrome://tracing` or upload at https://ui.perfetto.dev
- **Zoom:** scroll to zoom; drag to pan; press `W`/`S`/`A`/`D` to navigate
- **Filter by thread:** click a thread row name to highlight; use search (`/`) for kernel names
- **Measure a gap:** click the start of a gap, shift-click the end — duration appears at the bottom
- **Find a kernel:** press `/`, type part of the kernel name (e.g., `nccl`, `volta_sgemm`)
- **Large traces:** use Perfetto — Chrome freezes on files > ~200 MB
