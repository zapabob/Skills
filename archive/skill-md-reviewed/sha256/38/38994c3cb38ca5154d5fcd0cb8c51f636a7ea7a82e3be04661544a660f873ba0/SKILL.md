---
name: ggml-quant-format-reverse-engineering
description: Recover a GGML quant block format from a compiled binary.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [gguf, ggml, quantization, reverse-engineering, llama.cpp, disassembly, abliteration, windows]
    category: mlops/inference
---

# Recovering a GGML quant block format from a binary

Decode an undocumented/proprietary GGML quantization type (`pq2_0`, `ptq1_0`,
`q1_0`, `mxfp4`, any fork-specific type) by reading the shipped compiler output,
so a Python codec can be written that round-trips the real file byte-exactly.

## When to Use

- A GGUF uses a weight type that is absent from, or numbered above, your local
  llama.cpp's `GGML_TYPE_COUNT`.
- You must edit/requantize/abliterate weights and need the exact block layout.
- A model card describes a "2-bit direct code edit" recipe but the file turns out
  to store weights in a transform basis.
- A published quant is not reproducible with stock `llama-quantize` and you need
  to know why before touching it.

## Prerequisites

- `llvm-objdump` / `llvm-readobj` (bundled with LLVM) or MSVC `dumpbin`.
- The runtime build that **actually serves the file** — not any llama.cpp clone
  on disk. See Pitfalls.
- Python with `mmap` and `struct`. No third-party packages.

## Procedure

1. **Establish which toolchain owns the file.** Do not assume the source repo in
   your working tree is the one that produced the GGUF. Ask the running server
   (`GET /props` on `llama-server` reports the exact `model_path`), then compare
   each candidate build's `GGML_TYPE_COUNT` against the file's weight type id.
   A build with `GGML_TYPE_COUNT = 49` cannot open a file whose weights are
   type 142.
2. **Identify the type id empirically.** Parse the header yourself and compute
   bytes-per-element from consecutive tensor offsets (`offset[i+1]-offset[i]`
   over `n_elements[i]`, grouped by ggml type). A clean rational like `17/64` is
   the strongest early clue. Confirm against the build's type-name table, which
   usually lives in `ggml-base.dll` / `ggml-cpu.dll` `.rdata`.
3. **Prefer a custom reader over the tool's own dumper**, then diff against it.
   A hand-rolled mmap header parse that reproduces the tool's reported
   `data offset` exactly is the acid test for your reader.
4. **Find the quantizer/dequantizer symbols.** `llvm-objdump -p <dll>` lists
   exports with ordinals and RVAs. Row functions are commonly exported
   (`quantize_row_<t>_ref`, `dequantize_row_<t>`), giving you a disassembly
   address immediately. With MSVC DLLs the `.exe` may be a ~10 KB launcher — the
   real code is in `-impl.dll` and `ggml-base.dll`.
5. **Disassemble and read the geometry off the immediates.** The idioms:
   - `sarq $N, %rax` on the element count → elements per block = `1 << N`
   - `cmpl $0xNN, %reg` on a loop counter → codes per block
   - `addq $0xNN, %dst` at the bottom of the block loop → **bytes per block**
   Cross-check `bytes_per_block / elements_per_block` against the bytes-per-element
   you measured in step 2. Two independent sources must agree before you proceed.
6. **Establish field order from the dequantizer's first accesses.** The scale is
   read from wherever the initial `movzwl`/`movss` points; the code array is read
   from the offset used by the first `movzbl`. Do not assume the scale is last —
   in the measured `pq2_0` it is first, while stock `tq2_0` has it last.
7. **Decode the `.rdata` constants** the function references. Read the 4 bytes at
   each RIP-relative target and reinterpret as `f32`/`u32`. Abs masks, `1.0f`
   reciprocals, and half-precision exponent-domain constants all become legible.
8. **Derive the packing order** from the shift/merge sequence
   (`shl`/`shr` by `2*n`, `or` into a byte) and derive the code semantics from
   the quantize clamp plus the dequantize `dec`/offset.
9. **Implement the codec, then prove it on the real bytes.** The decisive test:
   take the file's *own* blocks, dequantize at the **stored** scale, requantize,
   and require byte equality. Report the exact rate.
10. **Mine the binary's own validation strings as the authoritative spec.** Once
    you know the metadata namespace (e.g. `prism.*`), extract every string literal
    the DLL carries about it — `strings`-style scan for `[ -~]{4,}` and filter on
    the namespace. These are the format's own acceptance rules, written by the
    author, and they beat any inference you draw from tensor geometry. A measured
    `pq2_0` build yields 38 such strings, including per-field rules, version
    gating, and the geometry checks:
    - `prism.hadamard block size %u does not divide input dimension %lld for %s`
    - `prism.hadamard has no sign vector for width %u (%s)`
    - `prism.hadamard version 2 requires tied_output=true; version 1 forbids it`
    - `loaded %zu Hadamard-folded weight(s) (%zu inverse-lookup) using %zu rotation(s) and %zu sign vector(s)`
    - `weight '%s' is not a verified Hadamard-aware matmul path`
    Then **run every extracted rule against the reference file** and report
    PASS/FAIL. A file the runtime would refuse to load must pass all of them, so
    this converts the classification from an inference into a check.
    See `references/runtime-string-mining.md`.
11. **Write contract tests** asserting the disassembled constants, the
    fixed-point property, the unpack/repack inverse over all byte patterns, and
    the size/scale invariants any editor must preserve.

11. **To prove the codec can WRITE, build a copy-on-write writer and demand an
    exact identity copy.** A codec that round-trips blocks in memory may still be
    wired to a writer that corrupts the file. Queue zero edits, stream to a new
    path, and require the same length AND the same SHA-256. Then queue one real
    edit and re-check. See `references/byte-exact-gguf-writer.md` for the four
    bugs this catches and `scripts/gguf_identity_copy.py` /
    `scripts/gguf_header_probe.py`.

12. **Persist the plan BEFORE touching payload, then prove the write against it.**
    Write a plan JSON (budget, per-tensor caps, tensor name, block index, the
    intended new code bytes, cumulative bits) as its own step, before the writer
    opens the file. Then audit the finished artifact against that plan, never
    against counters held in memory. A duplicate-`(tensor, block)` check on the
    plan is cheap and catches a real hazard: the writer's edit dict silently keeps
    only the last write for a repeated key while the bit counter has counted it
    twice. See `references/budget-audit-and-vectorization.md`.

## Editing: the invariants an editor must preserve

- **An amplitude knob cannot express a published edit budget — enforce the budget
  explicitly.** Model cards often state the release differs from the base by a
  specific number of bits (e.g. ~1.5 M bits out of 26.87 billion = 0.0028%).
  Because the ternary lattice is a cliff, NO amplitude produces that number —
  measured, the smallest scale-relative strength that yields any edit at all
  flips 0.03% of weights per block, i.e. 15 M bits model-wide, 10x over, while
  anything weaker flips nothing. So enforce the budget by CHOOSING blocks, not by
  shrinking the amplitude:
  1. map the whole run of blocks into the primal basis ONCE (the transform is
     over the input dimension, so it sees the full row — never per pq2_0 block),
  2. score each block by directional alignment `|<w_block, d_block>| / ||w_block||`
     in the PRIMAL basis,
  3. commit blocks in descending score until the budget is spent; skip (never
     truncate) a block whose cost would overshoot, since a block cannot be
     partially flipped.
  Report `bits_committed / bit_budget` and the weight-flip count in the receipt.
  The minimum committed change is one block, so budgets are honoured coarsely —
  state that rather than implying bit-granular control.
- **A published "bit" budget counts PHYSICAL bits, not changed symbols.** This
  is the single most expensive mistake in the whole workflow, and it is silent.
  With 2-bit codes packed four per byte, a symbol moving `00 -> 01` moves ONE
  physical bit while `00 -> 11` moves TWO. Charging every changed symbol a flat
  2 bits overstates the real cost, so a planner that "respects" the budget can
  be over by 25% against the same budget once you measure the file. Measured on
  `pq2_0`: planner reported 1,500,325 (weight_flips x 2), whole-file XOR said
  1,193,847 — a 1.257x ratio, and the artifact was 20% *under* budget, not over.
  Conversely a per-BYTE estimate (`4 per changed byte`) is wrong in the other
  direction. So:
  - the cost function is `popcount(new_bytes XOR old_bytes)`, computed on packed
    code payloads;
  - it is packing-agnostic, so it cannot be fooled by any interpretation of the
    code layout — which is exactly why it is the right primitive;
  - keep symbol accounting only as a separately-named report field, never as the
    budget. Name the fields distinctly (`changed_symbols`,
    `symbol_width_bits`, `physical_xor_bits`) so the two can never be confused
    again. Report `physical_xor_bits` as the headline.
  - **Never compare a planner's self-reported number to the budget as proof.**
    Recompute the count from the written file, independently.
- **Verify a budgeted edit against all four invariants at once**, not just the
  budget: `bits_used <= budget`, block length unchanged, scale bytes unchanged, and
  spare code count zero. The budget path re-enters the transform, so it can break
  a guarantee the un-budgeted path held.
- **A greedy model-wide budget MUST be apportioned across tensors BEFORE
  scanning, or it lands entirely on whichever tensor comes first in the file.**
  This is a silent, arithmetically-valid, semantically-empty result. A planner
  that walks tensors in file order and `break`s when the budget is spent will put
  100% of a 1.5 M budget into `blk.0.ffn_down.weight`'s first 40,944 blocks and
  touch no other layer at all — measured exactly that, on a model with 64 layers.
  Two independent budgets are needed:
  1. **per-tensor caps**, apportioned pro-rata to block count by largest-remainder
     rounding so the caps sum to *exactly* the model budget with no drift and a
     deterministic (name-sorted) tie-break, so a rerun reproduces the same plan;
  2. **the global remaining**, passed as `min(tensor_cap - tensor_spent,
     global_remaining)` into the inner call.
  A per-block early `break` is still needed for speed, but it must test the
  *tensor's* cap, not the global one. Then assert the spread in the receipt:
  distinct tensors touched, distinct layers touched, and blocks per tensor. A
  result touching one tensor is a bug even when the bit count checks out.
  Also give BOTH the signed and primal paths the gate — a budget check added to
  only one path leaves the other path able to scan the whole model forever.
- **Byte length per tensor comes from the NEXT tensor's offset, never from the
  ggml type.** A formula-derived size is wrong for 1-D F32 norms *and* for
  ternary block types simultaneously. Derive `size[i] = offset[i+1] - offset[i]`
  (last tensor runs to EOF) and assert `sum(size) == file_size - data_start`.
- **Never match tensor names with `endswith`.** They look like
  `blk.12.ffn_down.weight`, so `endswith("ffn_down")` selects **zero** tensors
  and returns no error. Use `in`, and extract the category with
  `name.split(".")[-2]`.
- **An amplitude knob with absolute units will be a no-op.** Real block scales
  can be ~0.0115, so a "large" absolute steering length saturates every code and
  the whole sweep collapses to one number. Express strength in *block-scale
  units* and convert via `strength * median(scale)`. A flat sweep line means
  wrong units before it means a code bug.
- **An editor's packing routine must clamp to the ternary maximum, not to the
  spare code.** The quantizer's clamp allows code 3; an editor must not emit it,
  or weights leave the lattice the model was trained on.

## Pitfalls

- **The block scale is stored in a narrower float than you compute.** Recomputing
  `d = max|x|` in float32 and requantizing does **not** reproduce the file. Read
  the stored value (e.g. fp16) and pass it back. This is precisely why
  "edit codes, never scales" preserves file size byte-exactly — and it is the
  invariant to assert in tests.
- **A spare/unused code may exist beyond the nominal set.** Ternary types
  typically use codes `0/1/2` for `-d/0/+d` and allow `3` in the quantize clamp
  for out-of-range values. Measure its real frequency in the file; never emit it
  from an editor, because it moves weights off the trained lattice.
- **Zero blocks encode as the *zero code*, not zero bytes.** With `d = 0` the
  reciprocal is 0, so every code becomes 1 and each code byte is `0b01010101`
  (`0x55`). Asserting `{0x00}` here is a test bug, not a codec bug.
- **A transform basis changes what "editing codes" means.** Check the KV metadata
  for a non-standard namespace before assuming weight-space edits. In a signed
  basis the sign is a DIAGONAL operator and does not commute with the transform,
  so it must be applied on exactly ONE side — applying it on both sides fails
  silently and by a wide margin. See `references/pq2-0-hadamard-basis-case.md`.
- **Metadata self-consistency is the strongest basis-layout evidence.** When
  `sign_widths` sums to exactly `len(sign_values)`, and every width is a whole
  number of the declared block size, the layout is pinned. Cross-check that
  against each tensor's `dims[-1]` before writing any transform code.
- **A whole-row exact/inexact probe is a BOOLEAN and it lies.** Requantizing a
  full dequantized row back to codes is NOT a fixed point once the values pass
  through a transform: fp error pushes boundary weights across a ternary step, so
  some rows come back byte-identical and others "fail" — and that ratio is
  meaningless. Measured on `pq2_0`, a single category showed 5/8 exact rows and 3/8
  not, while a *different* category with the identical basis showed 1/8. Reading
  that as "these widths use a different basis" sends you hunting for a nonexistent
  repeat/segment scheme. **Measure drift in BLOCK-SCALE units
  (`max|requantized - original| / scale`) instead of a boolean.** A drift of
  exactly `1.0` is one ternary step, i.e. rounding noise; `>= 2` would indicate a
  genuinely wrong basis. Under this metric every folded width in the measured
  file scored `1.0000` — one correct verdict across all of them, where the boolean
  produced six contradictory ones.
- **The runtime's own strings can correct an earlier geometry-based conclusion.**
  In the same case, tensor dimensions suggested a fused projection width was a
  plain concatenation of sign segments, and the boolean probe appeared to
  confirm a repeat scheme was wrong. The DLL strings then revealed an indexed
  `prism.hadamard.signs.%u` keyed by SEGMENT index (not occurrence) and a
  `gdn_v_grouped` flag, which is what actually distinguishes head-wise folding
  from a concatenated segment. Re-derive the classification from the strings, then
  confirm with the drift metric.
- **A magnitude/sparsity comparison cannot discriminate two sign conventions.**
  A ±1 vector does not change |x|, so both candidates score identically. The
  evidence is `sign_mode = 'explicit'` plus a nonzero sign imbalance.
- **A pointer table is not a contiguous string table.** The type-name table in a
  PE `.rdata` is usually an array of pointers; walking NUL-separated strings
  recovers nothing. Parse the PE section headers, convert file offset → RVA, and
  search `.rdata` for 8-byte little-endian values pointing at the strings.
- **Guard every untrusted length before slicing.** A wrong field width turns a
  length into a multi-exabyte request and dies with `MemoryError` instead of a
  diagnosable error. Mirror the reference reader's max-length and
  remaining-file-size checks.
- **Array metadata order is `type, then count`, not the reverse.** Getting this
  backwards reads a plausible-looking huge count and derails the whole parse.
- **`mmap.size` is a method, not an attribute.** `hasattr(m, "size")` is true and
  returns a *bound method*; comparing `int > m.size` raises `TypeError` on a
  builtin. Use `m.size()` under an `isinstance(m, mmap.mmap)` check, else `len()`.
- **`read_bytes()` on a multi-GB GGUF pins that much RAM.** Parse the header via
  `mmap` and read tensor bytes one block at a time.
- **Do not substitute a same-named type from a different codebase.** Fork A's
  `tq2_0` (256 elems/block, scale last) and fork B's `pq2_0` (128 elems/block,
  scale first) are unrelated. Check the type id and the exporting build.
- **When a test fails, decide whether the code or the expectation is wrong.**
  Reading the disassembly settles it; do not loosen the assertion.
- **In a vectorized kernel, copy the packing expression from the reference
  decoder LITERALLY — do not re-derive it, and do not "optimize" it into
  nibbles.** A numba port that read `byte & 0x0F` / `byte >> 4` (4 bits per
  element) instead of `(byte >> (2 * (i & 3))) & 3` (2 bits per element) produced
  32 elements per block instead of `QK_PQ2 = 128`, which indexed the level table
  out of range on the upper half of every block and surfaced only as `NaN`. The
  tell was that the *scale decode helper tested clean in isolation* while
  `deq_group` produced `NaN` — i.e. the bug was in the indexing, not the float
  path. Debug in this order: verify the float/scale helper alone, then dump the
  first mismatching element and its index, then re-read the reference index
  expression character by character.
- **Do not byte-swap an fp16 value that is already a typed view.** A
  `uint16` view of two little-endian bytes IS the fp16 bit pattern. Reordering
  the bytes shifts the exponent field and manufactures `NaN`/`inf` from perfectly
  ordinary small scales.
- **Prove a vectorized kernel bit-exact against the pure-Python reference on REAL
  blocks, not synthetic input.** Sample blocks from the actual file, run both
  paths, require `np.array_equal` (`max|diff| == 0`, not a tolerance). Real blocks
  carry the actual code-value distribution, including any spare code, which is
  part of what has to round-trip. Measured: a port that agreed on synthetic bytes
  still had to agree on 512 real blocks before it was trusted.
- **A pure-Python per-block loop is the bottleneck; it will not finish.** At
  ~0.5 M blocks/s a 209,920,000-block model is ~90 s per pass, and any loop with
  real work per block is far worse. Vectorize the hot kernels (dequant, pack,
  popcount) with numba/numpy and keep the pure-Python version as the oracle.
  Measure the achieved rate and print the implied model-wide single-pass time —
  that number is what tells you whether the design is viable before you wait on
  it.
- **Long jobs need real detachment, not `background=true`.** On Windows, a child
  launched through a bounded tool call dies with its parent, and long planning /
  writing passes over multi-GB files exceed that bound. Launch with
  `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW`, stdout/stderr
  redirected to a log file, and poll the log. A practical pattern is a tiny
  launcher script that takes `--log` and a command and prints the child PID as
  the log's first line.
  - **Clear `__pycache__` after editing a module the detached child imports.**
    Otherwise a re-run can execute the *previous* source and you will debug a bug
    you already fixed; the symptom is a traceback pointing at a line that no
    longer exists in the file.
  - **Log progress incrementally and check the log is growing**, not just that
    the process exists. A job that prints only at the end gives you no signal, and
    a run that neither progresses nor crashes is usually stuck on I/O.
- **Point pip and numba caches at a drive with space.** On a nearly-full system
  drive, `pip install` fails with `OSError(28, 'No space left on device')` even
  when the *target* venv is on a roomy volume, because `%TEMP%` and the pip cache
  are still on the full drive. Set `TMP`, `TEMP`, `PIP_CACHE_DIR` and
  `NUMBA_CACHE_DIR` to the roomy volume. Likewise, a WSL distro whose vhdx lives
  on the full drive cannot start at all.

## Verification

- **Audit the artifact, never the planner's own counters.** A budget that the
  planner reports as respected proves nothing. The gate is a whole-file XOR
  partition, which is the strongest statement the contract allows:
  `whole_file_xor_bits == code_region_xor_bits`, with
  `scale_xor_bits == 0`, `header_xor_bits == 0`, and `other_xor_bits == 0`
  (that last one covers every non-pq2_0 tensor, KV metadata, the tensor table and
  tail padding). If all four hold, every changed bit in the output is inside a
  pq2_0 code payload.
  - Implement it as **one sequential pass per file over large chunks** (64 MiB),
    with a precomputed `popcount` LUT indexed by `np.bitwise_xor(a, b)`. Measured
    7.2 GB in ~100-155 s. Partition by absolute file offset, not per block.
  - **Do not write a per-block comparator over two memory-mapped files.** A
    first attempt interleaved seeks between two mmaps and ran a pure-Python loop
    over 209,920,000 blocks; it ran >40 minutes on a 7.2 GB pair without a
    verdict, which makes it useless as a gate. Seeks across two mmaps plus a
    Python-level per-block loop is the anti-pattern; whole-file sequential chunk
    reads with vectorised XOR is the fix. If an auditor cannot produce a verdict
    in minutes, it is not a gate — delete and rewrite it rather than waiting.
- **Prove the auditor itself before trusting a verdict.** An auditor that returns
  PASS on two identical files proves nothing on its own — it may be passing for
  the wrong reason. Two cheap, mandatory tests:
  - **false-positive test**: base vs an identity copy must give
    `whole_file_xor_bits == 0` and exit 0;
  - **fault-injection tests**: copy the file and flip exactly one bit in each
    region, then require the auditor to *name the right bucket* — 1 bit in a code
    payload -> `code_xor_bits == 1`; 1 bit in a scale -> `scale_xor_bits == 1`;
    1 bit in the header -> `header_xor_bits == 1`. Each must exit non-zero.
    Getting the attribution right matters more than getting the total right: a
    tool that reports "some bits changed" cannot enforce an invariant.
  - Test the **budget boundary** explicitly (`B` passes, `B+1` fails). An auditor
    that has only ever seen "under budget" is not exercising the comparison.
- A hand-rolled header parse reproduces the reference tool's `data offset` and
  `alignment`; tensor regions neither overlap nor overrun the file; computed data
  end equals file size with zero trailing bytes.
- `sum(tensor.size)` equals `file_size - data_start` exactly, and consecutive
  offsets are contiguous with zero gaps.
- Measured bytes-per-element from tensor offsets equals
  `bytes_per_block / elements_per_block` from the disassembly.
- The codec round-trips the real file's blocks at a 100% exact rate across many
  tensors, not just the first.
- An editor applied to a block changes values while leaving block length and the
  scale bytes bit-identical.
- A zero-edit identity copy through the writer matches the source SHA-256.
- A one-edit copy matches in length and hash, differing ONLY inside the intended
  byte ranges — verify by diffing the first differing offset.

## Support files

- `references/pq2-0-hadamard-basis-case.md` — full worked case: measured type
  table, RVA/exports, disassembly excerpts, block layout, code semantics, the
  round-trip proof, the signed-basis one-sided-sign rule, the per-width basis
  classification, the steering granularity/amplitude threshold, and the spare
  code trap.
- `references/runtime-string-mining.md` — scanning a binary for its own
  validation strings and turning them into PASS/FAIL checks against the reference
  file; the fastest route to an authoritative spec when you have no source.
- `references/byte-exact-gguf-writer.md` — the four bugs that break a
  copy-on-write GGUF writer, how each presents, and the invariant that catches it.
- `references/budget-audit-and-vectorization.md` — physical-vs-symbol bit
  accounting with the measured numbers, the layer-concentration bug, the
  whole-file XOR auditor, the auditor's own fault-injection tests, and the
  numba pitfalls (nibble-vs-2-bit packing, fp16 view byte-swap).
- `scripts/whole_file_xor_audit.py` — the decisive artifact gate: partitions the
  base/variant XOR into code / scale / header / other and requires the change to
  be confined to code payloads. Sequential chunked reads, ~100-155 s for 7.2 GB.
- `scripts/audit_fault_injection.py` — false-positive plus per-region 1-bit fault
  injection; proves the auditor detects and *attributes* defects.
- `scripts/vector_kernel_selftest.py` — bit-exactness gate comparing vectorized
  kernels against the pure-Python reference on real blocks from the file.
- `scripts/launch_detached.py` — Windows `DETACHED_PROCESS` launcher that keeps a
  multi-GB planning/writing job alive past the calling tool's timeout.
- `scripts/gguf_identity_copy.py` — end-to-end copy + SHA-256 identity proof.
- `scripts/gguf_header_probe.py` — seconds-long header completeness proof; run
  it before every full copy.
- `scripts/gguf_writer_support.py` — reader/writer scaffolding the two probes
  share; adapt field names to your reader.
