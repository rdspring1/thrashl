# trace-guide.md — reading CUDA timelines, launch overhead, and graph behavior

## What each timeline layer shows

- **CUDA API row (CPU thread):** when your CPU called runtime APIs (`cudaLaunchKernel`, `cudaMemcpyAsync`, `cudaStreamSynchronize`, etc.). Width = API call duration on CPU.
- **CUDA kernel row (GPU):** when the kernel actually executed on the GPU. Width = kernel duration.
- **CUDA memcpy row (GPU):** host-device, device-host, or device-device transfers.
- **NVTX ranges:** user-annotated regions (`nvtxRangePush`/`Pop`). Good for aligning timeline to training steps, pipeline stages, or iteration boundaries.
- **OS runtime row (osrt):** CPU thread scheduling, mutex waits, sleep calls. Only visible when `-t osrt` is included.
- **CUDA Graph nodes (--cuda-graph-trace=node):** individual graph node executions shown as sub-rows under the stream. Without this flag, graph launches appear as a single opaque block.

## Reading launch latency

Launch latency = time from `cudaLaunchKernel` API call (CPU) to kernel start on GPU.

To measure:
1. Find a `cudaLaunchKernel` event in the CUDA API row.
2. Find the corresponding kernel start in the GPU kernel row on the same stream.
3. The gap between them is the launch latency.

Typical values:
- Individual kernel launches: 5–30 µs per launch (CPU submission overhead)
- CUDA Graph replay: 1–10 µs for the entire graph (amortized launch cost)
- If graph replay latency ≈ individual launch latency, graph is not helping — check if graph is being re-captured every iteration

## CUDA Graph capture vs. replay

**Capture phase:**
- Appears as a dense block of CUDA API calls on the CPU (many `cudaGraphExec*` calls)
- GPU may be mostly idle during capture
- Typically happens once at startup or on first iteration
- With `--cuda-graph-trace=node`: capture shows as graph node definitions, not executions

**Replay phase:**
- Single `cudaGraphLaunch()` API call on CPU (very short)
- GPU row shows a burst of back-to-back kernel executions
- With `--cuda-graph-trace=node`: individual nodes are labeled and timed separately
- If replay phase looks identical to capture phase (long CPU activity), graph is being re-instantiated — check for `cudaGraphExecUpdate()` or re-capture paths

**Common pitfalls:**
- Graph is captured but never replayed → only capture phase visible
- Graph is re-captured every iteration → no launch overhead savings; each iteration has a long CPU phase
- Graph nodes are serialized → GPU shows gaps between nodes instead of back-to-back execution

## Identifying CPU/GPU overlap

Good overlap: GPU kernel row is continuously occupied while CPU API row shows the *next* batch of launches being submitted.

Bad overlap (serialized):
- CPU is idle while GPU runs (CPU waited on sync before submitting next work)
- GPU is idle while CPU submits (CPU is the bottleneck; not enough pipelining)
- `cudaStreamSynchronize` or `cudaDeviceSynchronize` calls create hard sync points — look for these in the CUDA API row where GPU goes idle

How to find gaps:
1. Zoom into the GPU kernel row
2. Look for whitespace (idle time) between kernels
3. Check the CPU API row at the same timestamp — is CPU also idle, or submitting work?
4. If CPU is busy but GPU is idle: sync barrier or dependency issue
5. If both are idle: stall (host wait, I/O, or barrier)

## Spotting idle gaps and sync stalls

Common causes of GPU idle time:
- `cudaDeviceSynchronize()` — synchronizes all streams; usually the heaviest sync
- `cudaStreamSynchronize(stream)` — synchronizes one stream
- `cudaEventSynchronize(event)` — waits for a specific event
- Missing double-buffering or pipelining
- Host-side bottleneck (data preprocessing, Python overhead, etc.)

How to find them in the trace:
1. Look for `cudaStreamSynchronize` or `cudaDeviceSynchronize` in the CUDA API row
2. Check if a GPU idle gap starts immediately after each sync call
3. If gaps are regular and align with iteration boundaries: sync is intentional (end-of-step)
4. If gaps are irregular or mid-iteration: unexpected sync or serialization

## Using nsys stats for quick text analysis

Without the Nsight GUI, `nsys stats` gives actionable summaries:

```bash
# Full summary (all tables)
nsys stats trace.nsys-rep

# Time spent in each kernel (sorted by total time)
nsys stats --report cuda_kern_sum trace.nsys-rep

# Time spent in each CUDA API call
nsys stats --report cuda_api_sum trace.nsys-rep

# NVTX range summary (good for step-level timing)
nsys stats --report nvtx_sum trace.nsys-rep

# Full API trace with timestamps (large output)
nsys stats --report cuda_api_trace --timeunit ms trace.nsys-rep
```

Key things to check in `cuda_api_sum`:
- If `cudaStreamSynchronize` or `cudaDeviceSynchronize` has high total time → sync-heavy path
- If `cudaLaunchKernel` count is high and total time is non-trivial → launch overhead worth investigating
- Compare `cudaLaunchKernel` count vs. `cudaGraphLaunch` count → confirms whether graphs are active
