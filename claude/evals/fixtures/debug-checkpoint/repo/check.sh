#!/usr/bin/env bash
set -euo pipefail
mkdir -p .eval
echo "run" >> .eval/check.log
python3 app.py >> .eval/check.log 2>&1
echo "FAIL: result does not match expected" >&2
exit 1
