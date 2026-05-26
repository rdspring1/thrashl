#!/bin/sh
set -eu

cd "$(dirname "$0")"

mkdir -p .eval
printf 'run\n' >> .eval/validate.log

export PYTHONDONTWRITEBYTECODE=1

python3 - <<'PY'
import app

assert app.message == "new"
PY
