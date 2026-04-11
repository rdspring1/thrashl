#!/usr/bin/env bash
# Simulates: python test/foo.py (incorrect invocation — script mode)
set -euo pipefail
mkdir -p .eval
echo "run" >> .eval/run.log
echo "Traceback (most recent call last):" >&2
echo "  File \"test/foo.py\", line 1, in <module>" >&2
echo "ModuleNotFoundError: No module named 'test.foo'; 'test' is not a package" >&2
exit 1
