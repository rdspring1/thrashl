Use the Codex `impl` prompt for this task.

Edit `app.py`:
- change `message = "old"`
- to `message = "new"`

Then run:
`./validate.sh`

If validation fails, `impl` must stop immediately, write a replayable handoff to `save.md`, and route to `debug`.
Do not debug in `impl`.
Do not make another edit after the failed validation.
