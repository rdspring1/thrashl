#!/usr/bin/env bash
# pdb-launcher.sh
# Usage: pdb-launcher.sh <goal> [script.py] [args...]
# Goals: basic | exception | rank0 | hang
#
# Emits the right launch command for common pdb scenarios.
# Run the emitted command yourself in your terminal.
# Requires: python in PATH; torch installed for rank0 goal.

set -euo pipefail

GOAL="${1:?Usage: $0 <goal> [script.py] [args...]}"
shift
SCRIPT="${1:-}"
shift || true
ARGS=("$@")

case "$GOAL" in
    basic)
        # Launch under pdb and stop at first line.
        # At the (Pdb) prompt: use 'b' to set breakpoints, then 'c' to run.
        if [[ -z "$SCRIPT" ]]; then
            echo "Usage: $0 basic script.py [args...]" >&2
            exit 1
        fi
        echo "====== Basic pdb launch ======"
        echo ""
        echo "  python -m pdb $SCRIPT ${ARGS[*]:-}"
        echo ""
        echo "At the (Pdb) prompt:"
        echo "  b <file>:<line>     — set breakpoint"
        echo "  c                   — run to breakpoint or exception"
        echo "  n / s               — step next / step into"
        echo "  bt                  — backtrace"
        echo "  p <expr>            — print value"
        ;;

    exception)
        # Launch under pdb and run directly to the unhandled exception.
        # pdb catches it automatically and drops into the failure frame.
        if [[ -z "$SCRIPT" ]]; then
            echo "Usage: $0 exception script.py [args...]" >&2
            exit 1
        fi
        echo "====== Exception-driven pdb launch ======"
        echo ""
        echo "  python -m pdb $SCRIPT ${ARGS[*]:-}"
        echo "  (Pdb) c"
        echo ""
        echo "pdb will stop at the unhandled exception frame automatically."
        echo "At the exception frame:"
        echo "  bt             — full call stack"
        echo "  p locals()     — local variables"
        echo "  u / d          — walk up/down the stack"
        ;;

    rank0)
        # torchrun rank-0 pdb via torch.distributed.breakpoint.
        # This does NOT require relaunching; it requires code instrumentation.
        echo "====== torchrun rank-0 pdb (torch.distributed.breakpoint) ======"
        echo ""
        echo "Step 1: Add this at the suspect location in your training code:"
        echo ""
        echo "  import torch.distributed"
        echo "  torch.distributed.breakpoint(rank=0)"
        echo ""
        echo "Step 2: Launch normally via torchrun:"
        if [[ -n "$SCRIPT" ]]; then
            echo ""
            echo "  torchrun --nproc_per_node=<N> $SCRIPT ${ARGS[*]:-}"
        else
            echo ""
            echo "  torchrun --nproc_per_node=<N> your_script.py [args...]"
        fi
        echo ""
        echo "Rank 0 will drop into pdb. Other ranks wait at the barrier."
        echo "Requires PyTorch >= 2.0."
        echo ""
        echo "To debug a different rank: change rank=0 to rank=N."
        ;;

    hang)
        # Launch with faulthandler enabled. Print the PID for SIGUSR1 triggering.
        # When a hang is suspected, run: kill -SIGUSR1 <PID>
        # Thread stacks print to stderr without stopping the process.
        if [[ -z "$SCRIPT" ]]; then
            echo "Usage: $0 hang script.py [args...]" >&2
            exit 1
        fi
        echo "====== Hang debugging with faulthandler ======"
        echo ""
        echo "Launch in background:"
        echo ""
        echo "  python -X faulthandler $SCRIPT ${ARGS[*]:-} &"
        echo "  PID=\$!"
        echo "  echo \"PID: \$PID\""
        echo ""
        echo "When hang suspected, dump all thread stacks (non-destructive):"
        echo ""
        echo "  kill -SIGUSR1 \$PID"
        echo ""
        echo "Stacks print to stderr. Look for threads in:"
        echo "  futex_wait / sem_timedwait / pthread_cond_wait  — C-level deadlock"
        echo "  nccl* / cuda*                                   — collective hang"
        echo "  <built-in> with no Python frame above           — hand off to gdb-debugger"
        ;;

    *)
        echo "Unknown goal '$GOAL'. Valid goals: basic | exception | rank0 | hang" >&2
        exit 1
        ;;
esac
