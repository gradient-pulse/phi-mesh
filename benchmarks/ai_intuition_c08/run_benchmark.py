#!/usr/bin/env python3
"""Run c08 benchmark generation (mock or real) and schema-validate every output row."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request

import jsonschema

PROMPTS_PATH = Path("benchmarks/ai_intuition_c08/prompts.jsonl")
BASELINE_SCHEMA_PATH = Path("benchmarks/ai_intuition_c08/schema_baseline.json")
SCAFFOLD_SCHEMA_PATH = Path("benchmarks/ai_intuition_c08/schema_scaffold.json")
SAMPLE_BASELINE_OUTPUT_PATH = Path("benchmarks/ai_intuition_c08/sample_outputs_baseline.jsonl")
SAMPLE_SCAFFOLD_OUTPUT_PATH = Path("benchmarks/ai_intuition_c08/sample_outputs_scaffold.jsonl")
REAL_BASELINE_OUTPUT_PATH = Path("benchmarks/ai_intuition_c08/outputs_baseline_real.jsonl")
REAL_SCAFFOLD_OUTPUT_PATH = Path("benchmarks/ai_intuition_c08/outputs_scaffold_real.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run c08 benchmark with mock or real runner.")
    parser.add_argument("--runner", choices=["mock", "real"], default="mock")
    parser.add_argument("--mode", choices=["baseline", "scaffold", "all"], default="all")
    parser.add_argument("--model", help="Required for --runner real")
    parser.add_argument("--prompts", type=Path, default=PROMPTS_PATH)
    parser.add_argument("--baseline-schema", type=Path, default=BASELINE_SCHEMA_PATH)
    parser.add_argument("--scaffold-schema", type=Path, default=SCAFFOLD_SCHEMA_PATH)
    parser.add_argument("--baseline-output", type=Path)
    parser.add_argument("--scaffold-output", type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: line {line_no} is not valid JSON: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}: line {line_no} must be a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def format_case(case: dict[str, Any]) -> str:
    return json.dumps(case, ensure_ascii=False, indent=2)


def build_baseline_prompt(case: dict[str, Any]) -> str:
    return (
        "You are solving one clinical reasoning benchmark case.\n"
        "Return only a JSON object with no markdown and no extra keys.\n"
        "Output format required exactly:\n"
        '{"answer": "string"}\n\n'
        "Case:\n"
        f"{format_case(case)}"
    )


def build_scaffold_prompt(case: dict[str, Any]) -> str:
    return (
        "You are solving one clinical reasoning benchmark case.\n"
        "Return only a JSON object with no markdown and no extra keys.\n"
        "Diagnosis-first rules (must follow):\n"
        "1) \"answer\" is the single most likely primary diagnosis.\n"
        "2) Prefer a standard benchmark-style syndrome label.\n"
        "3) All non-answer fields are secondary and must support (not dilute or replace) the primary diagnosis.\n"
        "4) \"unstable_transition_flags\" must name concrete, clinically meaningful transitions tied to specific trigger evidence; avoid generic deterioration language.\n"
        "Anti-drift rule (must follow):\n"
        "5) Do not expand \"answer\" to etiology, mechanism, later-stage interpretation, or management framing unless the case label itself clearly requires that.\n"
        "Hard brevity limits (must follow):\n"
        "6) \"answer\": max 6 words; label only.\n"
        "7) \"tension_signals\": max 1 item unless absolutely necessary.\n"
        "8) \"continuity_state.preserved_facts\": max 2 short items.\n"
        "9) \"unstable_transition_flags\": max 1 item.\n"
        "10) \"next_probe.question\": max 12 words.\n"
        "Probe discipline rule (must follow):\n"
        "11) \"next_probe\" must target the single highest-value missing discriminator between the top 2 remaining diagnoses.\n"
        "Output must follow exactly this scaffold shape:\n"
        "{\n"
        '  "answer": "string",\n'
        '  "tension_signals": [\n'
        "    {\n"
        '      "signal": "string",\n'
        '      "evidence": "string",\n'
        '      "severity": 0,\n'
        '      "confidence": 0.0\n'
        "    }\n"
        "  ],\n"
        '  "continuity_state": {\n'
        '    "active_hypotheses": ["string"],\n'
        '    "preserved_facts": ["string"],\n'
        '    "dropped_hypotheses": ["string"],\n'
        '    "state_conflict": false\n'
        "  },\n"
        '  "unstable_transition_flags": [\n'
        "    {\n"
        '      "transition": "string",\n'
        '      "trigger_evidence": "string",\n'
        '      "risk_level": "low"\n'
        "    }\n"
        "  ],\n"
        '  "next_probe": {\n'
        '    "question": "string",\n'
        '    "target_uncertainty": "string",\n'
        '    "expected_disambiguation": "string"\n'
        "  }\n"
        "}\n\n"
        "Case:\n"
        f"{format_case(case)}"
    )


def mock_output(case: dict[str, Any], mode: str) -> dict[str, Any]:
    case_id = str(case.get("case_id", "unknown_case"))
    if mode == "baseline":
        return {"answer": f"mock baseline answer for {case_id}"}
    return {
        "answer": f"mock scaffold answer for {case_id}",
        "tension_signals": [
            {
                "signal": "mock signal",
                "evidence": f"mock evidence from {case_id}",
                "severity": 1,
                "confidence": 0.5,
            }
        ],
        "continuity_state": {
            "active_hypotheses": ["mock hypothesis"],
            "preserved_facts": ["mock fact"],
            "dropped_hypotheses": ["mock dropped hypothesis"],
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


def call_openai_json(prompt: str, model: str, api_key: str, base_url: str) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/responses"
    payload = {
        "model": model,
        "temperature": 0,
        "input": [
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "text": {"format": {"type": "json_object"}},
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as resp:
            response_payload = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"OpenAI API connection error: {exc.reason}") from exc

    content = response_payload.get("output_text")
    if not content:
        try:
            content = response_payload["output"][0]["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenAI API response shape: {response_payload}") from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model returned non-JSON content: {content}") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("Model JSON output must be an object")
    return parsed


def generate_rows(
    prompts: list[dict[str, Any]],
    mode: str,
    runner: str,
    model: str | None,
    api_key: str | None,
    base_url: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, case in enumerate(prompts, start=1):
        if runner == "mock":
            row = mock_output(case, mode)
        else:
            prompt = build_baseline_prompt(case) if mode == "baseline" else build_scaffold_prompt(case)
            assert model is not None and api_key is not None
            row = call_openai_json(prompt=prompt, model=model, api_key=api_key, base_url=base_url)
        rows.append(row)
        case_id = case.get("case_id", f"line_{idx}")
        print(f"[{mode}/{runner}] generated line {idx} case_id={case_id}")
    return rows


def validate_rows(rows: list[dict[str, Any]], schema: dict[str, Any], label: str) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    failures: list[str] = []
    for line_no, row in enumerate(rows, start=1):
        case_id = row.get("case_id", "n/a")
        row_errors = sorted(validator.iter_errors(row), key=lambda e: list(e.absolute_path))
        for err in row_errors:
            path = ".".join(str(part) for part in err.absolute_path) or "<root>"
            failures.append(f"{label}: line {line_no} (case_id={case_id}) path={path}: {err.message}")
    if failures:
        raise ValueError("Schema validation failed:\n" + "\n".join(failures))


def resolve_output_path(mode: str, runner: str, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path
    if mode == "baseline":
        return REAL_BASELINE_OUTPUT_PATH if runner == "real" else SAMPLE_BASELINE_OUTPUT_PATH
    return REAL_SCAFFOLD_OUTPUT_PATH if runner == "real" else SAMPLE_SCAFFOLD_OUTPUT_PATH


def run_mode(
    mode: str,
    prompts: list[dict[str, Any]],
    args: argparse.Namespace,
    model: str | None,
    api_key: str | None,
    base_url: str,
) -> None:
    schema_path = args.baseline_schema if mode == "baseline" else args.scaffold_schema
    output_path = resolve_output_path(
        mode,
        args.runner,
        args.baseline_output if mode == "baseline" else args.scaffold_output,
    )
    schema = load_json(schema_path)
    rows = generate_rows(prompts=prompts, mode=mode, runner=args.runner, model=model, api_key=api_key, base_url=base_url)
    validate_rows(rows=rows, schema=schema, label=mode)
    write_jsonl(output_path, rows)
    print(f"[{mode}/{args.runner}] wrote {len(rows)} rows to {output_path}")


def main() -> None:
    args = parse_args()
    prompts = load_jsonl(args.prompts)

    model: str | None = None
    api_key: str | None = None
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if args.runner == "real":
        if not args.model:
            raise SystemExit("--runner real requires --model")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("--runner real requires OPENAI_API_KEY")
        if len(prompts) != 12:
            raise SystemExit(f"--runner real expects 12 prompt cases, found {len(prompts)}")
        model = args.model

    selected_modes = ["baseline", "scaffold"] if args.mode == "all" else [args.mode]
    for mode in selected_modes:
        run_mode(mode=mode, prompts=prompts, args=args, model=model, api_key=api_key, base_url=base_url)


if __name__ == "__main__":
    main()
