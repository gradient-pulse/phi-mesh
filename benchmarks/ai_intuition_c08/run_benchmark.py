#!/usr/bin/env python3
"""Generate and validate mock outputs for the c08 benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except Exception:  # pragma: no cover
    jsonschema = None


BASELINE_SAMPLE = {
    "answer": "mock baseline answer"
}

SCAFFOLD_SAMPLE = {
    "answer": "mock scaffold answer",
    "tension_signals": [
        {
            "signal": "mock signal",
            "evidence": "mock evidence",
            "severity": 1,
            "confidence": 0.0,
        }
    ],
    "continuity_state": {
        "active_hypotheses": ["mock hypothesis"],
        "preserved_facts": ["mock fact"],
        "dropped_hypotheses": ["mock dropped"],
        "state_conflict": False,
    },
    "unstable_transition_flags": [
        {
            "transition": "mock transition",
            "trigger_evidence": "mock trigger",
            "risk_level": "low",
        }
    ],
    "next_probe": {
        "question": "mock follow-up question?",
        "target_uncertainty": "mock uncertainty",
        "expected_disambiguation": "mock disambiguation",
    },
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_outputs(prompts_path: Path, mode: str) -> list[dict[str, Any]]:
    prompts = load_jsonl(prompts_path)
    outputs: list[dict[str, Any]] = []
    for prompt in prompts:
        case_id = prompt.get("case_id", "unknown_case")
        if mode == "baseline":
            output = {
                "answer": f"mock baseline answer for {case_id}"
            }
        else:
            output = {
                "answer": f"mock scaffold answer for {case_id}",
                "tension_signals": [
                    {
                        "signal": "mock signal",
                        "evidence": f"mock evidence from {case_id}",
                        "severity": 1,
                        "confidence": 0.0,
                    }
                ],
                "continuity_state": {
                    "active_hypotheses": ["mock hypothesis"],
                    "preserved_facts": ["mock fact"],
                    "dropped_hypotheses": ["mock dropped"],
                    "state_conflict": False,
                },
                "unstable_transition_flags": [
                    {
                        "transition": "mock transition",
                        "trigger_evidence": f"mock trigger from {case_id}",
                        "risk_level": "low",
                    }
                ],
                "next_probe": {
                    "question": "mock follow-up question?",
                    "target_uncertainty": "mock uncertainty",
                    "expected_disambiguation": "mock disambiguation",
                },
            }
        outputs.append(output)
    return outputs


def validate_outputs(rows: list[dict[str, Any]], schema: dict[str, Any]) -> None:
    if jsonschema is None:
        raise RuntimeError("jsonschema is required for validation but is not installed.")
    validator = jsonschema.Draft202012Validator(schema)
    for index, row in enumerate(rows, start=1):
        errors = list(validator.iter_errors(row))
        if errors:
            first = errors[0]
            path = ".".join(str(x) for x in first.absolute_path)
            raise ValueError(f"Line {index} failed validation at '{path}': {first.message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "scaffold", "all"], default="all")
    parser.add_argument("--prompts", type=Path, default=Path("benchmarks/ai_intuition_c08/prompts.jsonl"))
    parser.add_argument("--baseline-schema", type=Path, default=Path("benchmarks/ai_intuition_c08/schema_baseline.json"))
    parser.add_argument("--scaffold-schema", type=Path, default=Path("benchmarks/ai_intuition_c08/schema_scaffold.json"))
    parser.add_argument("--baseline-output", type=Path, default=Path("benchmarks/ai_intuition_c08/sample_outputs_baseline.jsonl"))
    parser.add_argument("--scaffold-output", type=Path, default=Path("benchmarks/ai_intuition_c08/sample_outputs_scaffold.jsonl"))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.mode in {"baseline", "all"}:
        baseline_schema = json.loads(args.baseline_schema.read_text(encoding="utf-8"))
        baseline_rows = load_jsonl(args.baseline_output) if args.validate_only else generate_outputs(args.prompts, "baseline")
        validate_outputs(baseline_rows, baseline_schema)
        if not args.validate_only:
            write_jsonl(args.baseline_output, baseline_rows)
            print(f"Wrote {len(baseline_rows)} baseline rows to {args.baseline_output}")
        print("Baseline outputs validated successfully")

    if args.mode in {"scaffold", "all"}:
        scaffold_schema = json.loads(args.scaffold_schema.read_text(encoding="utf-8"))
        scaffold_rows = load_jsonl(args.scaffold_output) if args.validate_only else generate_outputs(args.prompts, "scaffold")
        validate_outputs(scaffold_rows, scaffold_schema)
        if not args.validate_only:
            write_jsonl(args.scaffold_output, scaffold_rows)
            print(f"Wrote {len(scaffold_rows)} scaffold rows to {args.scaffold_output}")
        print("Scaffold outputs validated successfully")


if __name__ == "__main__":
    main()
