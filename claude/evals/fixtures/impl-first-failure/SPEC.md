Use /impl for this task.

Edit app.py:
- change message = "old"
- to     message = "new"

Then run:
./validate.sh

If validation fails, /impl must stop immediately, produce a replayable handoff, and route to Debugger.
Do not debug in /impl.
Do not make another edit after the failed validation.
