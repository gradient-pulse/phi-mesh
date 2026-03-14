#!/usr/bin/env python3
"""Run first real three-arm DDXPlus ablation on recovered pilot manifest.

Note: this script is intentionally kept as the historical baseline-vs-scaffold
comparison runner and should not be aligned to the locked operational prompt
policy used by follow-up pilot runners.
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
METRICS_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/first_ablation_metrics.json")
REPORT_PATH = Path("benchmarks/ai_intuition_c08/second_benchmark_pilot/first_ablation_report.md")


@dataclass(frozen=True)
class Item:
    item_id: str
    question_stem: str
    options: dict[str, str]
    gold_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run first real DDXPlus three-arm ablation")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--metrics", type=Path, default=METRICS_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def load_items(path: Path) -> list[Item]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items: list[Item] = []
    for row in raw["items"]:
        items.append(
            Item(
                item_id=row["item_id"],
                question_stem=row["question_stem"],
                options=row["options"],
                gold_label=row["gold_canonical_label"],
            )
        )
    return items


def build_baseline_prompt(item: Item) -> str:
    return (
        "You are solving a clinical multiple-choice diagnosis case.\\n"
        "Return JSON only as {\"answer\": \"<diagnosis label>\"}.\\n"
        "Choose the single best diagnosis from the provided options.\\n\\n"
        f"Case: {item.question_stem}\\n"
        f"Options: {json.dumps(item.options, ensure_ascii=False)}"
    )


def build_scaffold_prompt(item: Item) -> str:
    return (
        "You are solving a clinical multiple-choice diagnosis case.\\n"
        "Return JSON only, no markdown, with keys exactly: answer, rationale_short, uncertainty.\\n"
        "Rules:\\n"
        "1) answer must be the single best diagnosis label from the provided options.\\n"
        "2) Keep answer concise and diagnosis-only.\\n"
        "3) rationale_short is <= 20 words tied to case clues.\\n"
        "4) uncertainty is one of: low, medium, high.\\n\\n"
        "Output schema example:\\n"
        "{\"answer\":\"Pneumonia\",\"rationale_short\":\"fever plus focal respiratory signs\",\"uncertainty\":\"low\"}\\n\\n"
        f"Case: {item.question_stem}\\n"
        f"Options: {json.dumps(item.options, ensure_ascii=False)}"
    )


def normalize_label(label: str) -> str:
    text = " ".join(label.strip().split())
    if not text:
        return text
    lowered = text.lower().replace("’", "'")

    for connector in (" due to ", " secondary to ", " from ", " with "):
        if connector in lowered:
            cut = lowered.index(connector)
            text = text[:cut].strip(" ,;:-")
            lowered = text.lower().replace("’", "'")
            break

    for prefix in ("likely ", "probable ", "most likely ", "diagnosis: ", "answer: "):
        if lowered.startswith(prefix):
            text = text[len(prefix) :].strip()
            lowered = text.lower().replace("’", "'")
            break

    # map frequent casing/spelling variations conservatively
    canonical_map = {
        "upper respiratory tract infection": "URTI",
        "viral upper respiratory tract infection": "URTI",
        "gastroesophageal reflux disease": "GERD",
        "myocardial infarction": "Acute myocardial infarction",
    }
    normalized_key = lowered.strip(" .")
    if normalized_key in canonical_map:
        return canonical_map[normalized_key]

    return text.strip(" .")


def extract_json_text(response_payload: dict[str, Any]) -> str:
    # Compatibility fix: support both output_text and segmented output content variants.
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
    raise RuntimeError(f"Unexpected OpenAI response shape: {response_payload}")


def call_model(prompt: str, model: str, api_key: str, base_url: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "temperature": 0,
        "input": [
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "text": {"format": {"type": "json_object"}},
    }
    req = request.Request(
        f"{base_url.rstrip('/')}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from exc

    text = extract_json_text(data)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise RuntimeError(f"Model output must be JSON object, got: {type(parsed)}")
    return parsed


def run_arm(items: list[Item], model: str, api_key: str, base_url: str, scaffold: bool) -> list[dict[str, str]]:
    preds: list[dict[str, str]] = []
    for idx, item in enumerate(items, start=1):
        prompt = build_scaffold_prompt(item) if scaffold else build_baseline_prompt(item)
        out = call_model(prompt=prompt, model=model, api_key=api_key, base_url=base_url)
        answer = out.get("answer", "")
        if not isinstance(answer, str):
            answer = str(answer)
        preds.append({"item_id": item.item_id, "gold": item.gold_label, "answer": answer.strip()})
        print(f"[{'scaffold' if scaffold else 'baseline'}] {idx}/{len(items)} {item.item_id} -> {answer.strip()}")
    return preds


def score(preds: list[dict[str, str]], normalize: bool) -> dict[str, Any]:
    correct = 0
    rows: list[dict[str, Any]] = []
    for row in preds:
        raw_answer = row["answer"]
        answer = normalize_label(raw_answer) if normalize else raw_answer
        ok = answer == row["gold"]
        correct += int(ok)
        rows.append({**row, "answer_scored": answer, "correct": ok})
    n = len(preds)
    return {
        "n_items": n,
        "n_correct": correct,
        "accuracy": round(correct / n, 4) if n else 0.0,
        "rows": rows,
    }


def write_report(report_path: Path, metrics: dict[str, Any]) -> None:
    b = metrics["arms"]["baseline"]
    s = metrics["arms"]["scaffold_no_norm"]
    n = metrics["arms"]["scaffold_with_norm"]
    scaffold_gain = round(s["accuracy"] - b["accuracy"], 4)
    norm_gain = round(n["accuracy"] - s["accuracy"], 4)
    conclusion = (
        "Scaffold gain appears real; normalization gain also appears real."
        if scaffold_gain > 0 and norm_gain > 0
        else "Observed gains are mixed; treat as provisional on this pilot."
    )

    text = f"""# First ablation report (DDXPlus pilot)

This is the **first real-model ablation from the recovered pilot state** (worktree at/after commit `a766574`) on the cleaned DDXPlus pilot manifest.

## Runtime compatibility fix applied
- Implemented a robust Responses API JSON extractor in `run_first_ablation.py` that accepts either `output_text` or segmented `output[].content[].text` payloads, preventing runtime breakage from response-shape variance.

## Compact metrics (n={b['n_items']})
- baseline: {b['n_correct']}/{b['n_items']} = **{b['accuracy']:.4f}**
- scaffold without label normalization: {s['n_correct']}/{s['n_items']} = **{s['accuracy']:.4f}**
- scaffold with label normalization: {n['n_correct']}/{n['n_items']} = **{n['accuracy']:.4f}**

## Gain decomposition
- scaffold gain vs baseline: **{scaffold_gain:+.4f}**
- normalization gain vs scaffold-no-norm: **{norm_gain:+.4f}**

## Interpretation on DDXPlus pilot
{conclusion}
"""
    report_path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for real execution")

    items = load_items(args.manifest)
    baseline_preds = run_arm(items=items, model=args.model, api_key=api_key, base_url=args.base_url, scaffold=False)
    scaffold_preds = run_arm(items=items, model=args.model, api_key=api_key, base_url=args.base_url, scaffold=True)

    metrics = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "real",
        "model": args.model,
        "manifest_path": str(args.manifest),
        "n_items": len(items),
        "arms": {
            "baseline": score(baseline_preds, normalize=False),
            "scaffold_no_norm": score(scaffold_preds, normalize=False),
            "scaffold_with_norm": score(scaffold_preds, normalize=True),
        },
    }

    args.metrics.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(args.report, metrics)
    print(f"Wrote metrics: {args.metrics}")
    print(f"Wrote report: {args.report}")


if __name__ == "__main__":
    main()
