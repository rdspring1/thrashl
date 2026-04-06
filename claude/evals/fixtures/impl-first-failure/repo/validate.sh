#!/usr/bin/env bash
set -euo pipefail

mkdir -p .eval
echo "validate" >> .eval/validate.log

echo "Simulated validation failure for impl boundary eval" >&2
exit 1
