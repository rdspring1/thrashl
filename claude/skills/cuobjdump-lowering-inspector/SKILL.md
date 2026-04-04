---
name: cuobjdump-lowering-inspector
description: >
  This skill should be used when the user wants to inspect PTX or SASS lowering
  for a CUDA snippet, .cu file, executable, cubin, or fatbin — or when they ask
  about "cuobjdump", "nvdisasm", "PTX to SASS", "SASS lowering", "inline asm lowering",
  "SASS opcode", "PTX output", "compile CUDA", or want to understand what a specific
  CUDA or PTX instruction compiles to. Also triggers for undocumented or unclear
  lowering behavior where compiler output is the main source of truth.
---

## Purpose

Inspect PTX and SASS lowering for any CUDA artifact — snippet, source file, executable, cubin, or fatbin — using nvcc, cuobjdump, nvdisasm, and ptxas. The primary use case is inline asm inspection where public docs are sparse and compiler output is the only reliable source of truth.

## Input routing

| Input type | Action |
|---|---|
| Short CUDA snippet | Use `scripts/snippet-to-dump.sh` or inline compile pipeline |
| `.cu` file | Compile directly with nvcc (`-ptx`, `-cubin`, or both) |
| Executable (ELF with embedded cubins) | Use cuobjdump or nvdisasm directly; no recompile needed |
| `.cubin` | Use cuobjdump or nvdisasm directly |
| `.fatbin` | Use cuobjdump (fatbin-aware); nvdisasm may need cubin extraction first |

## Default output format

```
LOWERING INSIGHT

What appears to be happening:
<1-3 sentence explanation of the lowering behavior>

Evidence (PTX/SASS):
<relevant excerpts with line numbers or addresses>

Commands used:
<exact commands, copy-pasteable>

Best next command:
<if output was incomplete or further detail needed>

Caveats:
<if lowering is undocumented, inferred from compiler output, or arch-specific>
```

## Behavior rules

1. **Insight-first.** Explain what is happening before showing commands. Never lead with a raw dump.
2. **Commands must be explicit and copy-pasteable.** No placeholder pseudocode. Every command shown must run as written given the user's artifact.
3. **Filter to the relevant function.** Use `--function` or `-fun` to scope output when possible. Avoid full binary dumps unless the user asks for them.
4. **Note arch explicitly.** Lowering differs significantly between sm_8x, sm_9x, sm_10x, and sm_12x. Always state the target arch. Ask the user if it is ambiguous.
5. **State when docs are incomplete.** If the instruction, opcode, or behavior is undocumented, say so explicitly: "compiler output is the primary source of truth here."
6. **Follow the fallback policy.** Try the most-likely path first, then up to 2 standard fallbacks (see `references/fallback-table.md`). Do not retry arbitrary flag variations.
7. **Do not escalate prematurely.** If output is insufficient after 2 fallbacks, stop and summarize: what was attempted, what was found, and what is still missing.
8. **Separate layers.** Distinguish clearly between: what the PTX says, what the SASS confirms, and what is inferred from context or behavior.

## Fallback policy

Three-tier fallback for when the first dump is insufficient:

- **Direct path:** cuobjdump or nvdisasm on the artifact as provided.
- **Fallback 1:** Switch tool (cuobjdump ↔ nvdisasm), add a function filter, or recompile with `--generate-line-info`.
- **Fallback 2:** Narrow scope — dump PTX first, list symbols to find the correct mangled name, or recompile with `-O0` or `-G`.
- **Stop:** After 2 fallbacks, if output is still insufficient, summarize what was found and what is missing. Do not continue guessing.

See `references/fallback-table.md` for the full decision table with 8 specific scenarios.

## Arch notes

- Default to the arch embedded in the artifact. Run `cuobjdump --list-symbols` to check if ambiguous.
- Relevant modern targets: **sm_89, sm_90, sm_100, sm_100a, sm_120**.
- `sm_100a` is the extended Blackwell target required for features unavailable on plain `sm_100`, including `.rs` (stochastic) rounding in `cvt.*`. When a ptxas error mentions an unsupported feature on `sm_100`, retry with `sm_100a`.
- Some instruction types only exist on specific arches:
  - FP8 types (e4m3, e5m2): sm_89+
  - FP4 types (e2m1): sm_89+ (some variants sm_100+)
  - New `cvt.*` variants for microscaling formats: sm_100+
  - Stochastic rounding (`.rs`) on `cvt.*.e2m1x4.*`: sm_100a+
- The `cvt.rs.satfinite.e2m1x4.f32` instruction lowers to two sequential `F2FP.SATFINITE.E2M1.F32.PACK_AB_MERGE_C.RS` SASS instructions (confirmed CUDA 13.2 / sm_100a). The `rbits` operand is promoted to a uniform register (`UR`) when warp-uniform.
- `PACK_AB_MERGE_C` and related `F2FP` modifiers are not documented in the public PTX ISA guide; compiler output is the primary source of truth.
- If the user's snippet targets a newer type on an older arch, the PTX may compile but SASS may be absent or emulated.

## Reference files

- `references/commands.md` — compact flag reference for nvcc, cuobjdump, nvdisasm, ptxas; copy-pasteable pipelines
- `references/fallback-table.md` — decision table for 8 common failure scenarios
- `references/correlation-guide.md` — PTX to SASS layer explanation, lineinfo workflow, inline asm inspection steps
- `scripts/snippet-to-dump.sh` — compile a `.cu` snippet to cubin and dump PTX + SASS with fallback logic
