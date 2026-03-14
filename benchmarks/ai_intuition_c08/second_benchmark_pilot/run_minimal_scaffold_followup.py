#!/usr/bin/env python3
"""Run minimal-scaffold follow-up on DDXPlus pilot manifest.

This follow-up intentionally uses a constrained answer-only scaffold with
explicit anti-overcall guidance as proposed in `ablation_error_pattern_note.md`.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

MANIFEST_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/pilot_manifest_draft.json")
FIRST_METRICS_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/first_ablation_metrics.json")
METRICS_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/minimal_scaffold_followup_metrics.json")
REPORT_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/minimal_scaffold_followup_report.md")


@dataclass(frozen=True)
class Item:
    item_id: str
    question_stem: str
    options: dict[str, str]
    gold_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run minimal scaffold follow-up on DDXPlus pilot")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--first-metrics", type=Path, default=FIRST_METRICS_PATH)
    parser.add_argument("--metrics", type=Path, default=METRICS_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def load_items(path: Path) -> list[Item]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        Item(
            item_id=row["item_id"],
            question_stem=row["question_stem"],
            options=row["options"],
            gold_label=row["gold_canonical_label"],
        )
        for row in raw["items"]
    ]


def build_minimal_scaffold_prompt(item: Item) -> str:
    return (
        "You are solving a clinical multiple-choice diagnosis case.\\n"
        "Return JSON only as {\"answer\": \"<exact option label>\"}.\\n"
        "Rules:\\n"
        "1) The answer MUST be copied verbatim from one of the provided option labels.\\n"
        "2) Do not output any rationale, confidence, or extra keys.\\n"
        "3) Do not favor severe/cardiac options unless uniquely supported by the evidence IDs.\\n\\n"
        f"Case: {item.question_stem}\\n"
        f"Options: {json.dumps(item.options, ensure_ascii=False)}"
    )


def extract_json_text(response_payload: dict[str, Any]) -> str:
    output_text = response_payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = response_payload.get("output", [])
    if isinstance(output, list):
        for block in output:
            if not isinstance(block, dict):
                continue
            content = block.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    return text

    raise ValueError("No text content found in response payload")


def call_model(base_url: str, api_key: str, model: str, prompt: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}/responses",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def evaluate(items: list[Item], *, model: str, base_url: str, api_key: str) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    correct = 0
    for item in items:
        prompt = build_minimal_scaffold_prompt(item)
        response = call_model(base_url, api_key, model, prompt)
        response_text = extract_json_text(response)
        parsed = json.loads(response_text)
        answer = str(parsed.get("answer", "")).strip()
        is_correct = answer == item.gold_label
        if is_correct:
            correct += 1
        rows.append(
            {
                "item_id": item.item_id,
                "gold": item.gold_label,
                "answer": answer,
                "correct": is_correct,
            }
        )
    return rows, correct


def load_baseline_accuracy(path: Path) -> float | None:
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return float(raw["arms"]["baseline"]["accuracy"])


def write_report(path: Path, *, n_items: int, accuracy: float, correct: int, baseline_accuracy: float | None) -> None:
    if baseline_accuracy is None:
        baseline_line = "- baseline reference: not available in this checkout"
        delta_line = "- gain vs baseline: n/a"
    else:
        baseline_line = f"- baseline reference: **{baseline_accuracy:.4f}**"
        delta_line = f"- gain vs baseline: **{(accuracy - baseline_accuracy):+.4f}**"

    report = "\n".join(
        [
            "# Minimal scaffold follow-up report (DDXPlus pilot)",
            "",
            "This artifact captures the minimal-scaffold follow-up requested after the first three-arm ablation.",
            "",
            "## Prompt variant tested",
            "- Output schema constrained to `{'answer': '<exact option label>'}` only.",
            "- No rationale/confidence fields allowed.",
            "- Added anti-overcall instruction against unjustified severe/cardiac choices.",
            "",
            f"## Results (n={n_items})",
            f"- minimal scaffold follow-up: {correct}/{n_items} = **{accuracy:.4f}**",
            baseline_line,
            delta_line,
            "",
            "## Notes",
            "- Source manifest: `pilot_manifest_draft.json`.",
            "- This run does not modify benchmark core code; it only emits follow-up artifacts.",
            "",
        ]
    )
    path.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")

    items = load_items(args.manifest)
    rows, correct = evaluate(items, model=args.model, base_url=args.base_url, api_key=api_key)

    accuracy = correct / len(items) if items else 0.0
    baseline_accuracy = load_baseline_accuracy(args.first_metrics)

    metrics = {
        "run_label": "minimal_scaffold_followup",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(args.manifest),
        "n_items": len(items),
        "model": args.model,
        "arm": {
            "name": "minimal_scaffold_followup",
            "correct": correct,
            "accuracy": accuracy,
            "items": rows,
        },
        "baseline_reference": {
            "path": str(args.first_metrics),
            "accuracy": baseline_accuracy,
            "gain_vs_baseline": None if baseline_accuracy is None else accuracy - baseline_accuracy,
        },
    }

    args.metrics.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(
        args.report,
        n_items=len(items),
        accuracy=accuracy,
        correct=correct,
        baseline_accuracy=baseline_accuracy,
    )


if __name__ == "__main__":
    main()
