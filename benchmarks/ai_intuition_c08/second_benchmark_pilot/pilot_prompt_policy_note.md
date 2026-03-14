# Pilot Prompt Policy Note

## Current decision
Use a **minimal answer-only scaffold with explicit anti-overcall wording** as the default prompt style for the current DDXPlus second benchmark 48-item pilot.

## Recommended default prompt
Operational default policy:
- **Output contract:** JSON-only output with exactly one key: `{"answer": "<exact option label>"}`.
- **Anti-overcall wording:** **Keep it**.
- **Rationale/uncertainty fields:** **Exclude them** (no rationale, confidence, uncertainty, or extra keys).
- **Option-label matching:** answer **must** match one provided option label verbatim.

## Exact wording to keep
Keep these instruction lines verbatim in the pilot default prompt:
- `Return JSON only as {"answer": "<exact option label>"}.`
- `1) The answer MUST be copied verbatim from one of the provided option labels.`
- `2) Do not output any rationale, confidence, or extra keys.`
- `3) Do not favor severe/cardiac options unless uniquely supported by the evidence IDs.`

## Wording to avoid
Do **not** use the following prompt elements in this pilot:
- Any requirement to output rationale/explanation text.
- Any requirement to output confidence/uncertainty fields.
- Multi-field scaffold contracts beyond `answer`.
- Open-ended answer wording that allows non-verbatim label outputs.

## Evidence summary
- **Baseline vs original scaffold:** first ablation shows baseline `15/48 = 0.3125` versus scaffold (no norm) `9/48 = 0.1875` and scaffold (with norm) `9/48 = 0.1875` (scaffold underperforms baseline by `-0.1250`; normalization adds `+0.0000`).
- **Minimal scaffold follow-up vs baseline:** minimal answer-only scaffold + anti-overcall reaches `16/48 = 0.3333`, a `+0.0208` gain vs baseline `0.3125`.
- **Anti-overcall incremental effect:** in 3 paired runs, anti-overcall beats no-anti-overcall every time: run deltas `+0.1250`, `+0.1042`, `+0.1042`.
- **Anti-overcall 3-run stability:** mean accuracy rises from `0.2569` (without anti-overcall) to `0.3681` (with anti-overcall), mean delta `+0.1111`, with a stability call to keep anti-overcall as default.

## Recommended interpretation
For this coded-evidence pilot, extra scaffold burden (rationale/uncertainty output requirements) appears to reduce answer selection quality, while a strict answer-only contract improves focus on label selection. Adding explicit anti-overcall wording provides a consistent incremental lift and mitigates a known severe/cardiac attractor pattern. Therefore, the best current default for the 48-item pilot is minimal answer-only JSON plus anti-overcall and verbatim option-copy constraints.

## Single next validation step
Run **one** additional 3x-per-arm replication on a **second disjoint 48-item slice** comparing minimal scaffold **with vs without** anti-overcall to verify transfer stability before scaling beyond this pilot.
