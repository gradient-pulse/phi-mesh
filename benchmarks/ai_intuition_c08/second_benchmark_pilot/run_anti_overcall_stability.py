#!/usr/bin/env python3
"""Repeat minimal-scaffold arms to assess anti-overcall stability on pilot manifest."""

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
METRICS_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/anti_overcall_stability_metrics.json")
REPORT_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/anti_overcall_stability_report.md")


@dataclass(frozen=True)
class Item:
    item_id: str
    question_stem: str
    options: dict[str, str]
    gold_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repeat anti-overcall stability runs on DDXPlus pilot")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--runs", type=int, default=3)
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


def build_prompt(item: Item, anti_overcall: bool) -> str:
    rules = [
        "1) The answer MUST be copied verbatim from one of the provided option labels.",
        "2) Do not output any rationale, confidence, or extra keys.",
    ]
    if anti_overcall:
        rules.append("3) Do not favor severe/cardiac options unless uniquely supported by the evidence IDs.")

    return (
        "You are solving a clinical multiple-choice diagnosis case.\\n"
        "Return JSON only as {\"answer\": \"<exact option label>\"}.\\n"
        "Rules:\\n"
        + "\\n".join(rules)
        + "\\n\\n"
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




def parse_answer_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
        stripped = "\n".join(lines).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Model output JSON must be an object")
    return parsed

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


def run_arm_once(items: list[Item], *, model: str, base_url: str, api_key: str, anti_overcall: bool) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    correct = 0
    for index, item in enumerate(items, start=1):
        prompt = build_prompt(item, anti_overcall=anti_overcall)
        response = call_model(base_url, api_key, model, prompt)
        response_text = extract_json_text(response)
        parsed = parse_answer_json(response_text)
        answer = str(parsed.get("answer", "")).strip()
        is_correct = answer == item.gold_label
        correct += int(is_correct)
        rows.append(
            {
                "item_id": item.item_id,
                "gold": item.gold_label,
                "answer": answer,
                "correct": is_correct,
            }
        )
        arm_name = "with_anti_overcall" if anti_overcall else "without_anti_overcall"
        print(f"[{arm_name}] {index}/{len(items)} {item.item_id} -> {answer}")

    accuracy = correct / len(items) if items else 0.0
    return {
        "correct": correct,
        "accuracy": accuracy,
        "items": rows,
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_report(path: Path, *, model: str, manifest: Path, n_items: int, runs: int, arms: dict[str, Any]) -> None:
    without_runs = [run["accuracy"] for run in arms["without_anti_overcall"]["runs"]]
    with_runs = [run["accuracy"] for run in arms["with_anti_overcall"]["runs"]]
    mean_without = mean(without_runs)
    mean_with = mean(with_runs)
    mean_delta = mean_with - mean_without

    stable = "yes" if all(delta > 0 for delta in [b - a for a, b in zip(without_runs, with_runs)]) else "mixed"
    keep_default = (
        "Yes — anti-overcall shows a consistent positive delta across all repeated runs."
        if stable == "yes"
        else "Tentative — anti-overcall helps on average, but per-run gains are not fully consistent."
    )

    lines = [
        "# Anti-overcall stability report (DDXPlus pilot)",
        "",
        "## Setup summary",
        f"- Manifest: `{manifest}` ({n_items} items)",
        f"- Model: `{model}`",
        f"- Repeats per arm: {runs}",
        "- Arms compared:",
        "  - minimal scaffold without anti-overcall",
        "  - minimal scaffold with anti-overcall",
        "",
        "## Per-run accuracies",
    ]

    for idx, (wout, win) in enumerate(zip(without_runs, with_runs), start=1):
        lines.append(
            f"- Run {idx}: without={wout:.4f}, with={win:.4f}, delta={win - wout:+.4f}"
        )

    lines.extend(
        [
            "",
            "## Means",
            f"- Mean accuracy (without anti-overcall): **{mean_without:.4f}**",
            f"- Mean accuracy (with anti-overcall): **{mean_with:.4f}**",
            f"- Mean delta (with - without): **{mean_delta:+.4f}**",
            "",
            "## Stability call",
            f"- Stable enough to keep anti-overcall as default pilot instruction? **{keep_default}**",
            "",
            "## Recommended next action",
            "- Run the same 3x/arm protocol on a second disjoint 48-item slice to confirm transfer stability before freezing defaults.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")

    items = load_items(args.manifest)
    arms: dict[str, Any] = {
        "without_anti_overcall": {"runs": []},
        "with_anti_overcall": {"runs": []},
    }

    for run_idx in range(1, args.runs + 1):
        without = run_arm_once(items, model=args.model, base_url=args.base_url, api_key=api_key, anti_overcall=False)
        with_anti = run_arm_once(items, model=args.model, base_url=args.base_url, api_key=api_key, anti_overcall=True)

        arms["without_anti_overcall"]["runs"].append({"run_index": run_idx, **without})
        arms["with_anti_overcall"]["runs"].append({"run_index": run_idx, **with_anti})

    without_acc = [run["accuracy"] for run in arms["without_anti_overcall"]["runs"]]
    with_acc = [run["accuracy"] for run in arms["with_anti_overcall"]["runs"]]

    metrics = {
        "run_label": "anti_overcall_stability",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(args.manifest),
        "n_items": len(items),
        "model": args.model,
        "repeats_per_arm": args.runs,
        "arms": {
            "without_anti_overcall": {
                "mean_accuracy": mean(without_acc),
                "runs": arms["without_anti_overcall"]["runs"],
            },
            "with_anti_overcall": {
                "mean_accuracy": mean(with_acc),
                "runs": arms["with_anti_overcall"]["runs"],
            },
        },
        "mean_delta_with_minus_without": mean(with_acc) - mean(without_acc),
        "all_runs_completed": True,
    }

    args.metrics.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(
        args.report,
        model=args.model,
        manifest=args.manifest,
        n_items=len(items),
        runs=args.runs,
        arms=metrics["arms"],
    )


if __name__ == "__main__":
    main()
