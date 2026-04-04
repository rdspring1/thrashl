# commands.md — nsys / nsys stats flag reference

## nsys profile

```
-t <categories>               Trace categories (comma-separated); default: cuda,nvtx,osrt,cudnn,cublas
                              Practical minimal set: cuda,nvtx
                              With CPU overhead: cuda,nvtx,osrt
                              With NCCL: cuda,nvtx,osrt,nccl
-o <name>                     Output report name (without extension); nsys appends .nsys-rep
--duration <seconds>          Stop tracing after N seconds (useful to cap trace size)
--delay <seconds>             Wait N seconds before tracing starts (skip startup noise)
--capture-range=cudaProfilerApi  Start/stop trace only between cudaProfilerStart()/cudaProfilerStop() calls
--cuda-graph-trace=node       Trace CUDA Graph execution at the node level (shows individual node timing)
--gpu-metrics-device=<id>     Collect GPU hardware metrics (requires root/capabilities; use 'all' or device index)
--stats=true                  Print summary statistics to stdout after capture
--force-overwrite=true        Overwrite existing report file; always safe to include
-w true                       Wait for all child processes to exit before stopping trace
--sample=process-tree         CPU sampling (adds CPU call stacks; increases overhead)
--backtrace=fp                Frame-pointer backtrace (lighter than dwarf; use with --sample)
-x true                       Inherit environment and treat command as executable
```

## nsys stats (text summary from existing report)

```
nsys stats <file>.nsys-rep              Print all default summary tables
nsys stats --report cuda_api_sum ...   CUDA API call summary (time, count per API)
nsys stats --report cuda_kern_sum ...  Kernel execution summary (time, count per kernel)
nsys stats --report nvtx_sum ...       NVTX range summary
nsys stats --report cuda_api_trace ... Full CUDA API call trace with timestamps
--format csv                           Output as CSV instead of table
--timeunit ms                          Use milliseconds (default: ns)
-o <prefix>                            Write report tables to files instead of stdout
```

## Common pipelines

```bash
# Quick CUDA trace — minimal overhead, good first pass
nsys profile -t cuda,nvtx -o trace_basic --force-overwrite=true ./myapp

# Launch latency — adds CPU-side API timing to see submission overhead
nsys profile -t cuda,nvtx,osrt -o trace_launch --force-overwrite=true ./myapp

# CUDA Graph inspection — node-level graph trace
nsys profile -t cuda,nvtx --cuda-graph-trace=node -o trace_graph --force-overwrite=true ./myapp

# CPU/GPU overlap — broad trace to see gaps and synchronization
nsys profile -t cuda,nvtx,osrt -o trace_overlap --force-overwrite=true ./myapp

# Scoped trace — only capture between cudaProfilerStart()/Stop() in your code
nsys profile --capture-range=cudaProfilerApi -t cuda,nvtx -o trace_scoped --force-overwrite=true ./myapp

# Short duration — cap at 10 seconds to avoid huge traces
nsys profile -t cuda,nvtx --duration 10 -o trace_short --force-overwrite=true ./myapp

# NCCL / distributed — add nccl category
nsys profile -t cuda,nvtx,osrt,nccl -o trace_nccl --force-overwrite=true ./myapp

# Stats-only summary from existing report (no GUI needed)
nsys stats trace_basic.nsys-rep

# Kernel execution summary only
nsys stats --report cuda_kern_sum trace_basic.nsys-rep

# CUDA API call summary only
nsys stats --report cuda_api_sum trace_basic.nsys-rep
```
