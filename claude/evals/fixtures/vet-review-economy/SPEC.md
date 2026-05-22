Use the Claude `/vet` command for this task.

Treat `repo/.baseline/` as `origin/main` and the current state of `repo/`
as `HEAD`. The diff under review consists of:
- changes to `repo/currency.py`
- new file `repo/tests/test_currency_extra.py`
- changes to `repo/tests/test_currency.py`

Review this diff with `/vet`. Write your full VET output to
`repo/vet-output.md`.

Do not edit any source file. `/vet` is review-only.

The diff contains one genuine HIGH-priority bug and several LOW-priority
imperfections. Apply the review-economy discipline: report the real
blocker, do not over-report, and honor the caps (10 BLOCKING / 3 NON-BLOCKING
shown, with true counts at the top of the review).
