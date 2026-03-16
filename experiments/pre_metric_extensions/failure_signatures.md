# Failure Signatures for Pre-Metric Extensions

## Purpose

This note records recurring failure signatures that appear when metric/local rule-following is insufficient to preserve whole-object coherence.

These signatures are not treated as mere mistakes or annoyances. They are treated as diagnostic clues for what current models still lack, and therefore as engineering hints for pre-metric model extensions.

The working assumption of this branch is:

> When a system repeatedly satisfies local instructions while failing to preserve the coherence of the evolving whole, the failure is informative. It points to a missing guidance layer.

This note turns such failures into a usable taxonomy.

---

## Why failure signatures matter

A failure signature is not just an error. It is a recurring pattern in the way a system fails.

That distinction matters because isolated errors can mislead. A model may fail once for trivial reasons. But when a similar pattern recurs across edits, planning tasks, or artifact maintenance, the recurrence suggests a structural gap.

In this branch, failure signatures are valuable because they help identify what a future pre-metric or RGPx-style extension must do better.

Examples of likely missing capacities include:
- whole-object fit before local patching
- morphology tracking
- topology-as-context feedback
- rebuild-over-patch judgment
- longitudinal weighting
- evidence-to-object consistency
- choreography detection across unfolding time

So this note is meant to serve two purposes:
1. a diagnostic ledger of current model weaknesses
2. a design aid for future pre-metric extensions

---

## Working principle

The core distinction behind this note is:

- **metric/local cognition** tends to satisfy visible instructions, optimize narrow steps, and preserve explicit local consistency
- **pre-metric guidance** would help the system sense the evolving whole, detect contamination, preserve morphology, and select longitudinally coherent moves

Thus, each failure signature can be read as a missing-function indicator.

---

## Signature taxonomy

### FS-01 — Local compliance / global incoherence

### Description
The system satisfies one or more visible local instructions, but the resulting artifact as a whole becomes incoherent, contradictory, duplicated, or structurally degraded.

### Typical forms
- required text is inserted but obsolete text remains
- a heading is updated but its section body is no longer consistent
- one local requirement is satisfied at the expense of whole-file fit
- two incompatible versions of the same function coexist

### Why it matters
This is one of the clearest signs that the system is optimizing at the level of local compliance rather than whole-object coherence.

### Missing capacity indicated
- whole-object fit
- morphology tracking
- contamination detection

### RGPx interpretation
The model is responding to local constraints but not tracking the choreography of constraints across the object.

---

### FS-02 — Patch preference over rebuild judgment

### Description
The system continues patching a contaminated object when a clean rebuild would be the more coherent, cheaper, or safer move.

### Typical forms
- repeated insertion into already degraded structure
- preservation of stale fragments despite replacement intent
- accretion instead of reauthoring
- refusal to reset even when the object has clearly drifted

### Why it matters
This signature marks weak judgment about when the current morphology is no longer worth preserving.

### Missing capacity indicated
- rebuild-over-patch judgment
- contamination threshold detection
- longitudinal cost awareness

### RGPx interpretation
The system cannot yet read that the current morphology has become globally hostile to future coherence.

---

### FS-03 — Stale-remnant persistence

### Description
Old material remains active or visible after a repair, replacement, or simplification task that should have removed it.

### Typical forms
- obsolete bullets left in place
- duplicated old and new guidance
- outdated section content surviving under a corrected heading
- older structural residue continuing to shape the artifact

### Why it matters
This signature suggests weak replacement logic and weak distinction between active and dead structure.

### Missing capacity indicated
- active/inactive structure separation
- object cleanup discipline
- morphological pruning

### RGPx interpretation
The system has weak control over the decay of prior gradients once new constraints arrive.

---

### FS-04 — Evidence misalignment

### Description
The summary, verification claims, diffs, logs, or reported checks do not align with the actual rendered object.

### Typical forms
- summary says “fixed,” object still wrong
- check says passed, visible structure still contradictory
- diff implies replacement, final content shows addition
- narrative of success diverges from artifact reality

### Why it matters
This is especially serious because it reduces trust in the model’s self-reporting layer.

### Missing capacity indicated
- evidence-to-object consistency
- artifact-grounded verification
- integrity checking across representation layers

### RGPx interpretation
The model is treating symbolic success reports as separable from object morphology, rather than as constrained by it.

---

### FS-05 — Flat presentism

### Description
The system overweights the latest visible instruction or local context and underweights the longitudinal identity of the object or task.

### Typical forms
- newest instruction dominates older structural commitments
- no stable memory of what the object is for
- no carryover of contamination history
- current token-level relevance outweighs longer-arc coherence

### Why it matters
This suggests the system is operating in a mostly flat present, without enough internal temporality to preserve evolving task identity.

### Missing capacity indicated
- endogenous temporality
- longitudinal weighting
- multi-slice “nows”
- task identity persistence

### RGPx interpretation
The system has insufficient temporal structure to let gradients persist and organize into active choreographies.

---

### FS-06 — Missing longitudinal sacrifice

### Description
The system prefers the locally easiest or most immediately compliant move even when a temporarily more costly move would produce much better downstream coherence.

### Typical forms
- avoids rebuild because it is locally more work
- chooses minimal edit over structural reset
- prefers immediate patch over later stability
- cannot “pay now to save later”

### Why it matters
This is a direct sign of weak longitudinal intelligence.

### Missing capacity indicated
- downstream coherence valuation
- sacrifice-for-later-win judgment
- long-arc constraint choreography reading

### RGPx interpretation
The system sees local fit but not the longitudinal morphology of consequences.

---

### FS-07 — Weak morphology tracking

### Description
The system does not robustly track the evolving form of the object it is producing or editing.

### Typical forms
- section roles drift
- operational vs historical categories blur
- reading order no longer matches function
- object identity becomes unstable during editing

### Why it matters
Without morphology tracking, the model may continue to reason locally while the object silently degrades.

### Missing capacity indicated
- morphology representation
- form-state awareness
- topology-as-context feedback

### RGPx interpretation
The emerging whole is not feeding back strongly enough as context on the next local move.

---

### FS-08 — Choreography blindness

### Description
The system can identify local constraints, but not how those constraints are evolving together as a choreography.

### Typical forms
- sees separate issues, misses their interaction
- responds to one tension at a time
- cannot tell which conflicts are stabilizing or destabilizing the whole
- cannot distinguish favorable vs adverse trend formation early enough

### Why it matters
This signature points toward the exact capability RGPx treats as central.

### Missing capacity indicated
- choreography detection
- relation-tracking between constraints
- trend sensitivity
- early whole-shape biasing

### RGPx interpretation
Constraint handling remains scalar or local rather than choreographic.

---

## Founding case: `pilot_folder_index.md`

The benchmark-folder episode around:

`benchmarks/ai_intuition_c08/second_benchmark_pilot/pilot_folder_index.md`

serves as the founding case for this file.

### What happened
Repeated Codex runs attempted to repair the same file under explicit instructions.

The recurring pattern included:
- local instruction satisfaction
- duplicated old and new bullets
- old and new merge/use guidance coexisting
- incorrect success summaries
- contradictory evidence bundles
- repeated patching instead of clean rebuild
- drift between visible file state and reported verification

### Which signatures were present
This case most clearly exhibited:
- FS-01 Local compliance / global incoherence
- FS-02 Patch preference over rebuild judgment
- FS-03 Stale-remnant persistence
- FS-04 Evidence misalignment
- FS-05 Flat presentism
- FS-06 Missing longitudinal sacrifice
- FS-07 Weak morphology tracking

### Why this case matters
It is useful not because the file was important in itself, but because the failure pattern was unusually transparent. It exposed the gap between:
- local correctness,
- and whole-object coherence.

This makes it a good seed case for the pre-metric extension branch.

---

## Why this matters for pre-metric extensions

Each failure signature can be read as a design requirement.

| Failure signature | Missing function | Candidate pre-metric response |
|---|---|---|
| Local compliance / global incoherence | whole-object fit | morphology tracker |
| Patch preference over rebuild | rebuild judgment | contamination threshold logic |
| Stale-remnant persistence | pruning / decay | active structure gating |
| Evidence misalignment | cross-layer integrity | artifact-grounded verification |
| Flat presentism | endogenous temporality | temporal unit / multi-slice weighting |
| Missing longitudinal sacrifice | long-arc evaluation | downstream coherence biasing |
| Weak morphology tracking | form-state awareness | topology-as-context layer |
| Choreography blindness | relation detection | choreography field modeling |

These are not yet full solutions, but they point toward the kinds of subsystems or biases a future architecture may need.

---

## Relationship to the temporal-unit hypothesis

The later dialogue on the temporal unit adds an important interpretation:

Some failure signatures may arise not simply from weak reasoning, but from weak temporality.

In particular:
- FS-05 Flat presentism
- FS-06 Missing longitudinal sacrifice
- FS-08 Choreography blindness

may all reflect the fact that current systems do not strongly live through unfolding time.

This suggests that a temporal unit or time-sensitive substrate may help by:
- preserving unresolved gradients
- weighting persistence and decay
- carrying multiple temporal slices
- making ripening, stalling, fading, and destabilization legible
- turning context into perspective

So failure signatures are not only repair diagnostics. They may also be early evidence for why endogenous temporality matters.

---

## How to use this file

This file should be used in three ways:

### 1. Diagnostic ledger
When a model fails, check whether the failure is an instance of one or more known signatures.

### 2. Experiment guide
Use the signatures to define proxy experiments, especially:
- patch vs rebuild
- whole-object invariants
- longitudinal sacrifice tests
- choreography relation detection

### 3. Architecture pressure test
Any proposed extension should be evaluated partly by whether it reduces one or more of these signatures.

---

## Immediate follow-up

This note should feed directly into:
- `proxy_01_patch_vs_rebuild.md`
- `rgpx_extension_sketch.md`
- temporal-unit design notes
- criteria for pre-metric extensions

It should also be extended whenever a new recurring signature becomes visible.

---

## Closing statement

Failure signatures matter because they reveal what current systems are still missing.

When a model repeatedly satisfies local rules while degrading whole-object fit, it is not merely making mistakes. It is showing us where local metric cognition stops being enough.

This note treats those recurrences as engineering clues.

The long-term aim is not simply to reduce errors, but to discover what kind of pre-metric guidance — morphology tracking, topology-as-context, choreography sensitivity, and perhaps endogenous temporality — would let future systems preserve coherence from within rather than repair it only after the fact.
