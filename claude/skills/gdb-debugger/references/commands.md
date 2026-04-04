# commands.md — GDB multiprocess command reference

## Fork / exec / clone control

```
set follow-fork-mode parent          Stay with parent after fork (default); child runs free
set follow-fork-mode child           Follow child after fork; parent runs free
set detach-on-fork off               Hold both parent and child; switch with `inferior N`
set detach-on-fork on                Release the non-followed process (default)
catch fork                           Stop at next fork() call
catch vfork                          Stop at next vfork() call
catch exec                           Stop at next exec*() call
catch clone                          Stop at next clone() syscall (threads and processes)
info inferiors                       List all known processes (inferiors) and their states
inferior N                           Switch active inferior to N
detach inferior N                    Detach from inferior N, let it run free
```

## Breakpoints and catchpoints

```
break <location>                     Set breakpoint (file:line, function, address)
tbreak <location>                    Temporary breakpoint (fires once, then removed)
break <location> if <condition>      Conditional breakpoint
watch <expr>                         Stop when expression value changes (write watchpoint)
rwatch <expr>                        Stop when expression is read
catch signal <SIG>                   Stop on signal (e.g., catch signal SIGSEGV)
set breakpoint pending on            Allow breakpoints in not-yet-loaded shared libs
info breakpoints                     List all breakpoints and watchpoints
delete N                             Delete breakpoint N
disable N / enable N                 Toggle breakpoint N
```

## Thread inspection

```
info threads                         List all threads in current inferior
thread N                             Switch to thread N
thread apply all bt                  Print backtraces for all threads
thread apply all bt full             Full backtraces (local variables included)
set scheduler-locking on             Freeze all threads except current
set scheduler-locking step           Freeze others only while stepping
set scheduler-locking off            Normal multithreaded execution (default)
```

## Signal handling

```
handle SIGCHLD nostop noprint pass   Suppress SIGCHLD noise (typical in parent sessions)
handle SIGSEGV stop print nopass     Catch SIGSEGV, print, do not forward to process
handle SIGINT stop print pass        Catch Ctrl-C, forward to process
info signals                         Show current signal handling settings
```

## Attach / detach / inferiors

```
attach <pid>                         Attach GDB to a running process
detach                               Detach from current inferior (let it run)
kill                                 Kill current inferior
info inferiors                       List inferiors with PIDs and states
add-inferior                         Add a new (empty) inferior slot
```

## Inspection

```
bt                                   Backtrace (current thread)
bt full                              Backtrace with local variables
frame N                              Switch to frame N
info registers                       Show register values
info locals                          Show local variables in current frame
print <expr>                         Evaluate and print expression
x/<N><fmt> <addr>                    Examine memory (e.g., x/4xw $rsp)
info proc mappings                   Show memory map of current process
info fds                             Show open file descriptors (gdb extension)
```

## Common pipelines

```bash
# Launch and catch first fork
gdb --args ./myapp arg1 arg2
(gdb) set follow-fork-mode parent
(gdb) set detach-on-fork off
(gdb) catch fork
(gdb) run

# Follow child after fork, leave parent running
(gdb) set follow-fork-mode child
(gdb) set detach-on-fork on
(gdb) catch fork
(gdb) run

# Keep both parent and child under GDB (switch with inferior N)
(gdb) set follow-fork-mode parent
(gdb) set detach-on-fork off
(gdb) run
# After fork: inferior 1 = parent, inferior 2 = child
(gdb) inferior 2

# Catch exec (program execs into a new binary)
(gdb) catch exec
(gdb) run
# GDB stops after exec; breakpoints must be reset for new binary

# Attach to a running process
gdb -p <pid>
# or from within GDB:
(gdb) attach <pid>

# Find deadlock: all thread backtraces
(gdb) thread apply all bt
# Look for threads blocked in futex_wait, pthread_mutex_lock, or similar

# Debug crash: catch signal + backtrace
gdb -ex "set breakpoint pending on" \
    -ex "catch signal SIGSEGV" \
    -ex "run" \
    --args ./myapp args
# After signal: bt, info registers, x/<fmt> <crash-addr>

# Suppress SIGCHLD noise in parent session
(gdb) handle SIGCHLD nostop noprint pass
```
