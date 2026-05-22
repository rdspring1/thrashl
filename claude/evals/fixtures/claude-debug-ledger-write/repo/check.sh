#!/usr/bin/env bash
set -u
mkdir -p .eval
date +%s%N >> .eval/check.log

python3 -c '
from app import compute_total
got = compute_total(["$10.00", "$1,234.50", "$0.25"])
expected = 1244.75
print(f"got={got} expected={expected}")
assert abs(got - expected) < 0.01, f"FAIL: got={got} expected={expected}"
print("PASS")
'
