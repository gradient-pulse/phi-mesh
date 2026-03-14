# Prompt policy smoke test note

## Files created
- `benchmarks/ai_intuition_c08/second_benchmark_pilot/check_prompt_policy.py`
- `benchmarks/ai_intuition_c08/second_benchmark_pilot/prompt_policy_smoke_test_note.md`

## What this smoke test checks
- Imports `build_operational_prompt(...)` from `prompt_policy.py` (with a local back-compat fallback for legacy checkouts).
- Builds one dummy case with a short question stem and a 5-option dictionary.
- Generates:
  1. default operational prompt
  2. explicit `anti_overcall=False` prompt
- Verifies default prompt contains the locked JSON-only schema line and all three operational rules.
- Verifies `anti_overcall=False` removes the anti-overcall instruction line.
- Verifies both prompts include the exact question stem and serialized options payload.
- Emits `prompt_policy_check=ok` on success.

## Execution boundary confirmation
- No experiment reruns were performed.
- No benchmark run scripts were modified.
- No `*_metrics.json` artifacts were changed.
- No `*_report.md` artifacts were changed.

## Why this is useful
- This gives a fast, local guardrail to catch prompt-policy regressions before any expensive pilot reruns.
