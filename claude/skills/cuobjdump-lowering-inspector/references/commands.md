# commands.md — nvcc / cuobjdump / nvdisasm / ptxas flag reference

## nvcc

```
-ptx                          Output PTX file only
-cubin                        Output cubin (device object)
-arch=sm_XX                   Target architecture
--generate-line-info          Add line info (for PTX/SASS correlation)
-G                            Full debug info (disables opts; use -O0 for cleaner PTX)
-O0 / -O2 / -O3               Optimization level (O0 = unoptimized PTX, O2 = production)
-keep                         Keep all intermediate files (.ptx, .cubin, etc.)
-o <file>                     Output file
--expt-relaxed-constexpr      Often needed for modern CUDA code
```

## cuobjdump

```
--dump-ptx                    Dump embedded PTX sections
--dump-sass                   Dump SASS (disassembled device code)
--dump-elf                    Dump ELF sections (low-level)
--list-symbols                List all embedded functions/symbols
--function <mangled>          Filter output to one function (exact mangled name required)
-arch sm_XX                   Filter to specific arch (for multi-arch binaries)
-sass                         SASS only (short form)
-ptx                          PTX only (short form)
```

## nvdisasm

```
-g                            Show source line info (requires lineinfo in cubin)
-sf                           Show control flow graph edges
-c                            Show control codes
-fun <mangled>                Filter to specific function
-arch sm_XX                   Override arch for disassembly
--no-vliw                     Don't group VLIW bundles (useful for sm_7x+)
--print-instruction-encoding  Show hex encoding alongside mnemonics
```

## ptxas (compile PTX to cubin)

```
-arch sm_XX                   Target architecture (required)
-o <output.cubin>             Output cubin
-v                            Verbose: show register/smem usage
--allow-expensive-optimizations true  Enable full opts
```

## Common pipelines

```bash
# Snippet → PTX
# Use sm_100a (not sm_100) for .rs rounding, e2m1x4, and other extended Blackwell features
nvcc -arch=sm_100a -ptx -O2 kernel.cu -o kernel.ptx

# Snippet → cubin → SASS
nvcc -arch=sm_100a -cubin --generate-line-info -O2 kernel.cu -o kernel.cubin
cuobjdump --dump-sass --function _ZN12MyKernelEPf kernel.cubin
# or
nvdisasm -g -sf -fun _ZN12MyKernelEPf kernel.cubin

# Snippet → PTX + SASS (both)
nvcc -arch=sm_100a -cubin -ptx --generate-line-info -O2 kernel.cu -keep

# Existing binary: list functions first
cuobjdump --list-symbols myapp | grep -i kernel_name

# Existing binary: dump SASS for one function
cuobjdump --dump-sass --function _ZN... myapp

# Existing cubin/fatbin: same as above
cuobjdump --dump-ptx --dump-sass kernel.fatbin

# PTX → cubin (if you have PTX and want SASS)
ptxas -arch=sm_100a kernel.ptx -o kernel.cubin && nvdisasm kernel.cubin
```
