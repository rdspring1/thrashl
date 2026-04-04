#!/usr/bin/env python3
"""
profile-snippet.py — torch.profiler templates for common profiling goals.

Usage:
    python profile-snippet.py hotspot     -- CPU+CUDA hotspot summary
    python profile-snippet.py graph       -- CUDA Graph capture+replay profiling
    python profile-snippet.py distributed -- Rank-0 Chrome trace for distributed jobs

Each template includes REPLACE comments showing where to insert your code.
"""

import sys
import time
import datetime
import torch
from torch.profiler import profile, record_function, ProfilerActivity

GOAL = sys.argv[1] if len(sys.argv) > 1 else "hotspot"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# HOTSPOT: CPU + CUDA summary, minimal overhead, no Chrome trace by default.
# Best first trace for: "what is the hot op?", "is this CPU or GPU bound?"
# ---------------------------------------------------------------------------
def run_hotspot():
    # REPLACE: set up your model and dataloader here
    device = "cuda"
    # model = MyModel().to(device)
    # dataloader = DataLoader(dataset, batch_size=32)

    print("==> Goal: hotspot (CPU + CUDA summary)")
    print("==> Schedule: wait=1, warmup=1, active=3")
    print()

    t0 = time.perf_counter()

    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
        record_shapes=False,
        profile_memory=False,
        with_stack=False,
    ) as prof:
        for step in range(6):  # wait=1 + warmup=1 + active=3 + 1 extra
            with record_function("step"):
                # REPLACE: your training or inference step here
                # loss = model(batch); loss.backward(); optimizer.step()
                torch.cuda.synchronize()  # remove this when inserting real code
            prof.step()

    wall = time.perf_counter() - t0
    print(f"Wall time: {wall:.3f}s\n")

    print("====== Top ops by CUDA time ======")
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))

    print("====== Top ops by CPU time ======")
    print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=20))

    trace_path = f"trace_hotspot_{TIMESTAMP}.json"
    prof.export_chrome_trace(trace_path)
    print(f"\nChrome trace exported: {trace_path}")
    print("Open with: chrome://tracing  or  https://ui.perfetto.dev")


# ---------------------------------------------------------------------------
# GRAPH: CUDA Graph capture + replay profiling.
# Note: torch.profiler shows graph launches as a single block.
# For per-node breakdown, use nsys-trace-profiler with --cuda-graph-trace=node.
# ---------------------------------------------------------------------------
def run_graph():
    device = "cuda"
    print("==> Goal: CUDA Graph profiling")
    print("==> Note: use nsys-trace-profiler for node-level graph timing")
    print()

    # REPLACE: set up static inputs and model
    # static_input = torch.randn(32, 512, device=device)
    # model = MyModel().to(device)

    # --- Graph capture ---
    print("--- Capturing CUDA Graph ---")
    # REPLACE: run warmup iterations before capture
    # for _ in range(3):
    #     _ = model(static_input)
    # torch.cuda.synchronize()

    # g = torch.cuda.CUDAGraph()
    # with torch.cuda.graph(g):
    #     static_output = model(static_input)
    # torch.cuda.synchronize()
    # print("Graph captured.")

    # --- Profile graph replay ---
    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
        record_shapes=False,
    ) as prof:
        for step in range(6):
            with record_function("graph_replay"):
                # REPLACE: g.replay()
                torch.cuda.synchronize()  # placeholder
            prof.step()

    trace_path = f"trace_graph_{TIMESTAMP}.json"
    prof.export_chrome_trace(trace_path)

    print("====== Graph replay — top ops by CUDA time ======")
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
    print(f"\nChrome trace: {trace_path}")
    print("Look for: single short 'cudaGraphLaunch' block vs. eager kernel count")
    print("If graph launch latency ≈ eager launch latency: graph is not amortizing cost.")
    print("For per-node timing: use nsys-trace-profiler with goal=graph")


# ---------------------------------------------------------------------------
# DISTRIBUTED: Rank-0 Chrome trace for overlap and NCCL inspection.
# Requires torch.distributed to be initialized before calling.
# ---------------------------------------------------------------------------
def run_distributed():
    import contextlib
    try:
        import torch.distributed as dist
        rank = dist.get_rank() if dist.is_initialized() else 0
    except Exception:
        rank = 0

    print(f"==> Goal: distributed / NCCL overlap (rank {rank})")
    print(f"==> Profiling: {'rank 0 only' if rank == 0 else 'skipping (not rank 0)'}")
    print()

    if rank == 0:
        prof_ctx = profile(
            activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
            schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
            record_shapes=False,
        )
    else:
        prof_ctx = contextlib.nullcontext()

    with prof_ctx as prof:
        for step in range(6):
            with record_function("step"):
                # REPLACE: your distributed training step here
                # loss = model(batch); loss.backward(); optimizer.step()
                if dist.is_initialized():
                    dist.barrier()
                else:
                    torch.cuda.synchronize()  # placeholder
            if prof is not None:
                prof.step()

    if rank == 0:
        trace_path = f"trace_dist_rank0_{TIMESTAMP}.json"
        prof.export_chrome_trace(trace_path)
        print("====== Top ops by CUDA time (rank 0) ======")
        print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))
        print(f"\nChrome trace: {trace_path}")
        print("In the trace: look for ncclKernel_* rows and GPU idle gaps between compute and allreduce.")
        print("Good overlap: NCCL kernels run concurrently with next forward pass kernels.")
        print("Bad overlap: NCCL finishes, then compute starts (serialized).")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
if GOAL == "hotspot":
    run_hotspot()
elif GOAL == "graph":
    run_graph()
elif GOAL == "distributed":
    run_distributed()
else:
    print(f"Unknown goal '{GOAL}'. Valid goals: hotspot | graph | distributed")
    sys.exit(1)
