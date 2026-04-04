#!/usr/bin/env bash
# capture-trace.sh
# Usage: capture-trace.sh <goal> <command...>
# Goals: basic | launch | graph | overlap | scoped
#
# Outputs: <goal>_<timestamp>.nsys-rep, then prints nsys stats summary
# Requires: nsys in PATH

set -euo pipefail

GOAL="${1:?Usage: $0 <goal> <command...>}"
shift
CMD=("$@")

if [[ ${#CMD[@]} -eq 0 ]]; then
    echo "Error: no command provided after goal" >&2
    exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="${GOAL}_${TIMESTAMP}"

case "$GOAL" in
    basic)
        TRACE_FLAGS=(-t cuda,nvtx)
        ;;
    launch)
        # Adds osrt to expose CPU-side API submission timing
        TRACE_FLAGS=(-t cuda,nvtx,osrt)
        ;;
    graph)
        # Node-level CUDA Graph trace; shows capture vs replay
        TRACE_FLAGS=(-t cuda,nvtx --cuda-graph-trace=node)
        ;;
    overlap)
        # Broad trace for CPU/GPU overlap and sync stall analysis
        TRACE_FLAGS=(-t cuda,nvtx,osrt)
        ;;
    scoped)
        # Only captures between cudaProfilerStart()/cudaProfilerStop() in the binary
        TRACE_FLAGS=(--capture-range=cudaProfilerApi -t cuda,nvtx)
        ;;
    *)
        echo "  [Unknown goal '$GOAL'; falling back to basic trace]"
        TRACE_FLAGS=(-t cuda,nvtx)
        ;;
esac

echo "==> Goal: $GOAL"
echo "==> Output: ${OUTPUT}.nsys-rep"
echo "==> Command: ${CMD[*]}"
echo ""

nsys profile \
    "${TRACE_FLAGS[@]}" \
    -o "$OUTPUT" \
    --force-overwrite=true \
    "${CMD[@]}"

echo ""
echo "====== nsys stats summary ======"
nsys stats "${OUTPUT}.nsys-rep" \
    || { echo "  [nsys stats failed; report may still be valid — open in Nsight GUI]"; }
