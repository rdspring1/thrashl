# commands.md — pdb command reference

## Core pdb commands

```
n                             Next line — execute current line, don't step into calls
s                             Step — step into function calls
r                             Return — run until current function returns
c                             Continue — run until next breakpoint or unhandled exception
u                             Up — go up one frame in the call stack
d                             Down — go down one frame in the call stack
l                             List — show source context around current line
l <line>                      List source around given line number
b <file>:<line>               Set breakpoint at file:line
b <file>:<line>, <condition>  Set conditional breakpoint (e.g., b train.py:42, step > 100)
b <function>                  Set breakpoint at function entry
tbreak <location>             Temporary breakpoint (fires once, then removed)
cl <N>                        Clear breakpoint N (use `info break` to list)
p <expr>                      Print expression value
pp <expr>                     Pretty-print expression
whatis <expr>                 Print type of expression
args                          Print arguments of current function
bt                            Backtrace — print full call stack
where                         Alias for bt
q                             Quit pdb
! <statement>                 Execute arbitrary Python statement
interact                      Start interactive Python interpreter at current frame
commands N                    Define commands to run automatically when breakpoint N fires
```

## Conditional breakpoints

```python
# Stop only when a variable has an unexpected value
b module.py:55, loss != loss          # NaN check
b trainer.py:120, batch_idx == 500    # specific iteration
b model.py:88, x.shape[0] != 32      # shape mismatch
```

## Exception-driven debugging

```bash
# Run to unhandled exception — frame is preserved automatically
python -m pdb script.py args
(Pdb) c    # continue; stops at first unhandled exception
(Pdb) bt   # inspect stack at exception site
(Pdb) p locals()   # inspect local variables
```

## Launching

```bash
# Basic launch under pdb
python -m pdb script.py arg1 arg2

# Enable faulthandler for hangs and segfaults
python -X faulthandler script.py args

# Disable all breakpoint() calls globally (silence workers)
PYTHONBREAKPOINT=0 python script.py

# Run with faulthandler in background, capture PID for SIGUSR1
python -X faulthandler script.py args &
PID=$!
echo "PID: $PID — to dump threads: kill -SIGUSR1 $PID"

# Inject breakpoint in code (no relaunch needed)
# Add to the suspect location:
breakpoint()
```

## Common pipelines

```bash
# Launch and run to unhandled exception
python -m pdb script.py
(Pdb) c

# Conditional breakpoint on iteration or value
python -m pdb script.py
(Pdb) b trainer.py:88, step == 200
(Pdb) c

# Inspect tensor state at a breakpoint
(Pdb) p tensor.shape
(Pdb) p tensor.dtype
(Pdb) p tensor.min().item()
(Pdb) p tensor.max().item()
(Pdb) p tensor.isnan().any().item()

# torchrun rank-0 debugging (PyTorch 2.0+)
# Add to suspect location in training code:
#   torch.distributed.breakpoint(rank=0)
# Then launch normally:
torchrun --nproc_per_node=N script.py

# Dataloader num_workers=0 workaround
# In code:
#   DataLoader(dataset, num_workers=0, ...)
# Or pass as arg if configurable:
python script.py --num-workers 0

# Faulthandler hang dump (thread stack dump without stopping the process)
python -X faulthandler script.py &
PID=$!
# When hang suspected:
kill -SIGUSR1 $PID
# Stacks print to stderr; look for threads blocked in C extensions

# Inspect all local variables at current frame
(Pdb) p locals()
(Pdb) pp locals()   # pretty-print for readability
```
