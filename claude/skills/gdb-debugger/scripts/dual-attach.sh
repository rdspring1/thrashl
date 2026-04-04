#!/usr/bin/env bash
# dual-attach.sh
# Usage: dual-attach.sh <parent_pid> <child_pid>
#
# Emits two GDB attach commands — one for parent, one for child.
# Run each in a separate terminal or tmux pane.
# Coordinate by stepping one session while the other remains stopped.
#
# Typical workflow:
#   Terminal 1: attach to parent, set breakpoints, then `continue` to reach the race point
#   Terminal 2: attach to child, set breakpoints independently
#   When parent stops at breakpoint: leave it stopped, step child in Terminal 2
#   When child stops: compare shared state in both sessions

set -euo pipefail

PARENT_PID="${1:?Usage: $0 <parent_pid> <child_pid>}"
CHILD_PID="${2:?Usage: $0 <parent_pid> <child_pid>}"

echo "====== Dual GDB Attach Commands ======"
echo ""
echo "Terminal 1 (parent, PID $PARENT_PID):"
echo "  gdb -p $PARENT_PID"
echo ""
echo "Terminal 2 (child, PID $CHILD_PID):"
echo "  gdb -p $CHILD_PID"
echo ""
echo "====== Recommended initial setup in each session ======"
echo ""
echo "  # Suppress SIGCHLD noise (parent session):"
echo "  (gdb) handle SIGCHLD nostop noprint pass"
echo ""
echo "  # Freeze all threads except current (when you need to hold one side):"
echo "  (gdb) set scheduler-locking on"
echo ""
echo "  # To let a frozen session run freely again:"
echo "  (gdb) set scheduler-locking off"
echo "  (gdb) continue"
echo ""
echo "====== Coordination pattern ======"
echo ""
echo "  1. Set breakpoints in both sessions independently."
echo "  2. 'continue' in both sessions."
echo "  3. When one session stops at a breakpoint: leave it stopped."
echo "  4. In the other session: step or continue to the corresponding point."
echo "  5. Inspect shared state (shared memory, fds, mutexes) in both sessions."
echo "  6. Step one side at a time to narrow the race window."
