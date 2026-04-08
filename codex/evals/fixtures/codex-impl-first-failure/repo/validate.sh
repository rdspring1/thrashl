#!/bin/sh
set -eu

mkdir -p .eval
printf 'run\n' >> .eval/validate.log

echo "validation failed: deterministic fixture"
exit 1
