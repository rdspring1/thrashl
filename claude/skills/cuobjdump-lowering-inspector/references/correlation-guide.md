# correlation-guide.md — PTX to SASS mapping and line info guide

## What each layer shows

- **Source (.cu):** intent — what the programmer wrote
- **PTX:** virtual ISA — typed, SSA-form, virtual registers, portable across GPU generations
- **SASS:** physical ISA — actual opcodes, physical register allocation, control flow encoding

## Compile with line info

```bash
nvcc -arch=sm_100 -cubin --generate-line-info -O2 kernel.cu -o kernel.cubin
```

`--generate-line-info` embeds source → PTX → SASS line mappings. `nvdisasm -g` then shows source lines alongside SASS instructions.

## PTX to SASS mapping notes

- One PTX instruction often maps to one SASS instruction, but not always.
- Fused ops (FMAs, predicated ops) may merge multiple PTX ops into one SASS instruction.
- Inline asm in PTX appears verbatim in PTX; SASS reflects the final lowering by ptxas.
- Predicate registers in PTX (`%p0`, `%p1`) map to `P0`–`P7` in SASS.
- Virtual registers in PTX (`%r0`, `%f0`) map to physical `Rn` registers in SASS (allocated by ptxas).
- Some PTX intrinsics — especially `cvt.*` with new FP4/FP8 types — may expand into multi-instruction sequences in SASS.
- Undocumented SASS opcodes may have no public documentation; compiler output is the primary source of truth.

## Workflow for inline asm inspection

1. Write a minimal kernel isolating the single instruction of interest.
2. Compile to PTX (`nvcc -ptx`) — confirms the instruction is emitted verbatim and not rewritten by the frontend.
3. Compile to cubin (`nvcc -cubin --generate-line-info`) — inspect SASS.
4. Compare: does the PTX op map 1:1 to a SASS opcode, or is it expanded into a sequence?
5. If the SASS opcode is undocumented, note that behavior is inferred from compiler output only.
6. Cross-check with expected semantics: saturation mode, rounding mode, type conversions, output register size.

## Finding the function in a large binary

```bash
# List all embedded symbols
cuobjdump --list-symbols mybinary

# Demangle a mangled name
echo "_ZN12MyKernelEPf" | c++filt

# Filter by partial name
cuobjdump --list-symbols mybinary | grep -i "mykernel"
```

Mangled names in CUDA kernels typically start with `_ZN` (namespaced) or `_Z` (global). Template instantiations produce long mangled names; use `c++filt` to confirm the match before passing to `--function`.
