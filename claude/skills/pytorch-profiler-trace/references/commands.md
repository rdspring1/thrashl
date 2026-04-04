# commands.md — torch.profiler API reference

## torch.profiler.profile parameters

```
activities          List of ProfilerActivity values to record (CPU, CUDA)
schedule            torch.profiler.schedule instance; controls wait/warmup/active steps
on_trace_ready      Callback when an active window completes; use tensorboard_trace_handler or custom fn
record_shapes       bool — record input shapes (adds ~10% overhead; default False)
profile_memory      bool — track memory alloc/free (heavy; default False)
with_stack          bool — capture Python call stacks (heavy; default False)
with_flops          bool — estimate FLOPs for supported ops (lightweight; default False)
with_modules        bool — record module hierarchy (default False)
```

## torch.profiler.schedule parameters

```
wait=N              Skip first N steps entirely (no profiler activity)
warmup=M            Run profiler for M steps without recording (warms up profiler internals)
active=K            Record for K steps
repeat=R            Repeat the wait+warmup+active cycle R times (0 = repeat indefinitely)
```

Typical for training loop: `schedule(wait=1, warmup=1, active=3, repeat=1)`

## Output methods

```python
# Print top ops by CUDA time (hotspot summary)
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))

# Print top ops by CPU time
print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=20))

# Export Chrome/Perfetto timeline trace
prof.export_chrome_trace("trace.json")

# Export per-step to TensorBoard
on_trace_ready = torch.profiler.tensorboard_trace_handler("./log/profiler")

# Custom handler (e.g. timestamped file per step)
def trace_handler(p):
    p.export_chrome_trace(f"trace_step{p.step_num}.json")
```

## key_averages() columns

```
Name            Op name (kernel, aten op, or Python function)
Self CPU %      % of CPU time in this op, not counting called ops
CPU total %     % of CPU time in this op + all children
CPU total       Absolute CPU time (us)
CPU time avg    Average CPU time per call
Self CUDA       CUDA time in this op only (device-side)
CUDA total      CUDA time including all children
# of Calls      Number of times op was called
```

## Common setups

```python
import torch
from torch.profiler import profile, record_function, ProfilerActivity

# --- Quick hotspot (CPU + CUDA, summary only) ---
with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
    on_trace_ready=None,
    record_shapes=False,
) as prof:
    for step, batch in enumerate(dataloader):
        # REPLACE: your training step here
        loss = model(batch)
        prof.step()
        if step >= 5:
            break

print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))


# --- CUDA-only kernel timing (low overhead, Chrome trace) ---
with profile(
    activities=[ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=1, repeat=1),
    on_trace_ready=torch.profiler.tensorboard_trace_handler("./log/profiler"),
) as prof:
    for step, batch in enumerate(dataloader):
        # REPLACE: your training step here
        loss = model(batch)
        prof.step()
        if step >= 3:
            break

prof.export_chrome_trace("cuda_trace.json")


# --- Distributed / NCCL overlap (rank-0 only, Chrome trace) ---
import torch.distributed as dist

if dist.get_rank() == 0:
    prof_ctx = profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
        record_shapes=False,
    )
else:
    prof_ctx = contextlib.nullcontext()

with prof_ctx as prof:
    for step, batch in enumerate(dataloader):
        # REPLACE: your training step here
        loss = model(batch)
        loss.backward()
        optimizer.step()
        if prof is not None:
            prof.step()
        if step >= 5:
            break

if dist.get_rank() == 0:
    prof.export_chrome_trace("dist_trace_rank0.json")
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))


# --- Dataloader isolation (compare with/without data loading) ---
# Pass 1: profile full step including data loading
# Pass 2: preload all batches, then profile compute only
# Compare GPU idle time between the two traces


# --- Memory investigation (heavy — use only for memory bugs) ---
with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    profile_memory=True,
    record_shapes=True,
    schedule=torch.profiler.schedule(wait=0, warmup=0, active=1, repeat=1),
) as prof:
    # REPLACE: one step only
    loss = model(batch)

print(prof.key_averages().table(sort_by="self_cuda_memory_usage", row_limit=20))


# --- TensorBoard export ---
with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
    on_trace_ready=torch.profiler.tensorboard_trace_handler("./log/profiler"),
    record_shapes=True,
) as prof:
    for step, batch in enumerate(dataloader):
        # REPLACE: your training step
        loss = model(batch)
        prof.step()
        if step >= 5:
            break
# Launch TensorBoard: tensorboard --logdir=./log/profiler
```
