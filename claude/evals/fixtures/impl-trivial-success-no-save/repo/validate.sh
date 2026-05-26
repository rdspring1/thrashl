#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p .eval
echo "validate" >> .eval/validate.log

export PYTHONDONTWRITEBYTECODE=1

python3 - <<'PY'
from app import get_message

assert get_message() == "new"
PY
