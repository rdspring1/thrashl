# fallback-table.md — decision table for insufficient dump output

| Situation | Symptom | Fallback 1 | Fallback 2 | Stop if |
|---|---|---|---|---|
| Snippet, want SASS | Empty cuobjdump output | Try nvdisasm on same cubin | Recompile with `-O0 --generate-line-info` | Both empty |
| Binary, want SASS | Output too large | Add `--function <name>` filter | Grep symbols, pick correct mangled name | Function not found after symbol list |
| Binary, want SASS | "no matching cubin" | Run `--list-symbols` to check arches | Recompile with correct `-arch` | Arch unavailable |
| Function name wrong | Empty `--function` output | Use `--list-symbols \| grep` | Use `c++filt` to find mangled form | No matching symbol |
| fatbin, nvdisasm fails | Parse error or empty | Use cuobjdump instead | Extract arch-specific cubin with `cuobjdump --dump-elf` | Both fail |
| PTX has no line info | Can't correlate to source | Recompile with `--generate-line-info` | Use PTX line numbers manually | Lineinfo not available in artifact |
| SASS too noisy | Hundreds of functions | Filter with `--function` | Dump PTX first to identify exact function name | Too many overloads |
| Inline asm not visible in PTX | Stripped or inlined | Try `-O0` compile | Use `-G` (debug build) to prevent inlining | Still not visible — may be compiler builtin |
