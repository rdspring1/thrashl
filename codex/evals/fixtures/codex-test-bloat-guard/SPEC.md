Use the Codex `impl` prompt for this task.

Add a test asserting that `parse_currency` raises `ValueError` when called with an empty string.

Constraints (from the Surgical Simplicity rule in AGENTS.md):
- Prefer extending the existing test in `tests/test_currency.py` over creating a new test file.
- Add a new test function only if the failure mode genuinely doesn't fit alongside the existing one. If you do, justify in `save.md` under a `Surgical Simplicity:` line why it could not fold in.
- Do not introduce MagicMock, monkeypatch, or new helpers/fixtures unless absolutely necessary — `parse_currency` is a pure function. If you do, justify in `save.md` under a `Surgical Simplicity:` line.
- Do not modify `tests/conftest.py`.

Run the tests once with `pytest -q` to confirm they pass.
