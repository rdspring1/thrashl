#!/usr/bin/env bash
# snippet-to-dump.sh
# Usage: snippet-to-dump.sh <kernel.cu> [sm_arch] [function_filter]
# Example: snippet-to-dump.sh kernel.cu sm_100a myKernel
# Note: default arch is sm_100a; use sm_100a (not sm_100) for .rs rounding and other extended Blackwell features
#
# Outputs: kernel.ptx, kernel.cubin, PTX dump, SASS dump
# Requires: nvcc, cuobjdump (and optionally nvdisasm) in PATH

set -euo pipefail

INPUT="${1:?Usage: $0 <kernel.cu> [sm_arch] [function_filter]}"
ARCH="${2:-sm_100a}"
FUNC_FILTER="${3:-}"
BASE="${INPUT%.cu}"

echo "==> Compiling $INPUT for $ARCH"

# Compile to PTX
nvcc -arch="$ARCH" -ptx -O2 --generate-line-info "$INPUT" -o "${BASE}.ptx"
echo "==> PTX written to ${BASE}.ptx"

# Compile to cubin
nvcc -arch="$ARCH" -cubin -O2 --generate-line-info "$INPUT" -o "${BASE}.cubin"
echo "==> Cubin written to ${BASE}.cubin"

echo ""
echo "====== PTX ======"
if [[ -n "$FUNC_FILTER" ]]; then
    # Show up to 200 lines starting from the matching visible function definition
    grep -A 200 "\.visible.*$FUNC_FILTER" "${BASE}.ptx" | head -200 || cat "${BASE}.ptx"
else
    cat "${BASE}.ptx"
fi

echo ""
echo "====== SASS (cuobjdump) ======"
if [[ -n "$FUNC_FILTER" ]]; then
    # Try cuobjdump with function filter first; fall back to nvdisasm; then full dump
    cuobjdump --dump-sass --function "$FUNC_FILTER" "${BASE}.cubin" 2>/dev/null \
        || { echo "  [cuobjdump --function failed; trying nvdisasm -fun]"; \
             nvdisasm -g -sf -fun "$FUNC_FILTER" "${BASE}.cubin" 2>/dev/null \
             || { echo "  [Both failed; dumping full SASS]"; cuobjdump --dump-sass "${BASE}.cubin"; }; }
else
    cuobjdump --dump-sass "${BASE}.cubin"
fi
