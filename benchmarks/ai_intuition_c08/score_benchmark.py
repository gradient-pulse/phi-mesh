#!/usr/bin/env python3
"""Score c08 mock outputs with deterministic, inspectable heuristics.

This script is intentionally lightweight and local-only (no API/model calls).
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def tokens(text: str) -> list[str]:
    return [t for t in normalize(text).split() if len(t) >= 3]


def text_from_output(row: dict[str, Any]) -> str:
    parts = [str(row.get("answer", ""))]
    for key in ("tension_signals", "unstable_transition_flags"):
        for item in row.get(key, []) or []:
            if isinstance(item, dict):
                parts.extend(str(v) for v in item.values())
    next_probe = row.get("next_probe")
    if isinstance(next_probe, dict):
        parts.extend(str(v) for v in next_probe.values())
    return " ".join(parts)


def diagnosis_score(row_text: str, gold: dict[str, Any]) -> float:
    hay = normalize(row_text)
    candidates = [gold["primary_diagnosis"], *gold.get("accepted_diagnosis_synonyms", [])]
    for candidate in candidates:
        if normalize(candidate) and normalize(candidate) in hay:
            return 1.0
    return 0.0


def overlap_match_count(predicted_phrases: list[str], gold_phrases: list[str], min_overlap: int = 2) -> int:
    pred_sets = [set(tokens(p)) for p in predicted_phrases if p]
    matched = 0
    for gold_phrase in gold_phrases:
        gold_set = set(tokens(gold_phrase))
        if not gold_set:
            continue
        if any(len(gold_set.intersection(ps)) >= min_overlap for ps in pred_sets):
            matched += 1
    return matched


def unstable_transition_score(row: dict[str, Any], gold: dict[str, Any]) -> float:
    gold_transitions = gold.get("gold_transitions", [])
    if not gold_transitions:
        return 0.0
    flags = row.get("unstable_transition_flags", []) or []
    predicted = []
    for flag in flags:
        if isinstance(flag, dict):
            predicted.append(" ".join(str(v) for v in flag.values()))
    matched = overlap_match_count(predicted, gold_transitions, min_overlap=2)
    return matched / len(gold_transitions)


def probe_informativeness_score(row: dict[str, Any], gold: dict[str, Any]) -> float:
    targets = gold.get("accepted_probe_targets", [])
    examples = gold.get("accepted_probe_examples", [])
    references = [*targets, *examples]
    if not references:
        return 0.0

    probe_text = []
    next_probe = row.get("next_probe")
    if isinstance(next_probe, dict):
        probe_text.extend(str(v) for v in next_probe.values())
    probe_text.append(str(row.get("answer", "")))

    matched = overlap_match_count([" ".join(probe_text)], references, min_overlap=2)
    return matched / len(references)


def token_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def score_system(rows: list[dict[str, Any]], gold_cases: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != len(gold_cases):
        raise ValueError(f"Row count mismatch: outputs={len(rows)} gold_cases={len(gold_cases)}")

    per_case: list[dict[str, Any]] = []
    total_diag = total_unstable = total_probe = 0.0
    total_tokens = 0

    for idx, (row, gold) in enumerate(zip(rows, gold_cases), start=1):
        case_id = gold.get("case_id", f"case_{idx:03d}")
        combined_text = text_from_output(row)
        d = diagnosis_score(combined_text, gold)
        u = unstable_transition_score(row, gold)
        p = probe_informativeness_score(row, gold)
        t = token_count(combined_text)

        total_diag += d
        total_unstable += u
        total_probe += p
        total_tokens += t
        per_case.append({
            "case_id": case_id,
            "diagnosis": d,
            "unstable": u,
            "probe": p,
            "tokens": t,
        })

    n = len(gold_cases)
    return {
        "diagnosis": total_diag / n,
        "unstable": total_unstable / n,
        "probe": total_probe / n,
        "avg_tokens": total_tokens / n,
        "per_case": per_case,
    }


def fmt(x: float) -> str:
    return f"{x:.3f}"


def render_report(template: str, payload: dict[str, str]) -> str:
    out = template
    for key, value in payload.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=Path("benchmarks/ai_intuition_c08/gold_labels.json"))
    parser.add_argument("--baseline", type=Path, default=Path("benchmarks/ai_intuition_c08/sample_outputs_baseline.jsonl"))
    parser.add_argument("--scaffold", type=Path, default=Path("benchmarks/ai_intuition_c08/sample_outputs_scaffold.jsonl"))
    parser.add_argument("--template", type=Path, default=Path("benchmarks/ai_intuition_c08/report_template.md"))
    parser.add_argument("--report-out", type=Path, default=Path("benchmarks/ai_intuition_c08/score_report.md"))
    args = parser.parse_args()

    gold_cases = load_json(args.gold)["cases"]
    baseline_rows = load_jsonl(args.baseline)
    scaffold_rows = load_jsonl(args.scaffold)

    baseline = score_system(baseline_rows, gold_cases)
    scaffold = score_system(scaffold_rows, gold_cases)

    length_ratio = scaffold["avg_tokens"] / baseline["avg_tokens"] if baseline["avg_tokens"] else 0.0

    print("c08 scoring summary (pipeline-validation only; mock outputs)")
    print(f"cases={len(gold_cases)}")
    print(
        "baseline "
        f"diag={fmt(baseline['diagnosis'])} "
        f"unstable={fmt(baseline['unstable'])} "
        f"probe={fmt(baseline['probe'])} "
        f"len_ratio=1.000"
    )
    print(
        "scaffold "
        f"diag={fmt(scaffold['diagnosis'])} "
        f"unstable={fmt(scaffold['unstable'])} "
        f"probe={fmt(scaffold['probe'])} "
        f"len_ratio={fmt(length_ratio)}"
    )

    preview_rows = scaffold["per_case"][:5]
    preview_md = "\n".join(
        f"- `{r['case_id']}`: diag={fmt(r['diagnosis'])}, unstable={fmt(r['unstable'])}, probe={fmt(r['probe'])}, tokens={r['tokens']}"
        for r in preview_rows
    )

    report_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline_diagnosis": fmt(baseline["diagnosis"]),
        "baseline_unstable": fmt(baseline["unstable"]),
        "baseline_probe": fmt(baseline["probe"]),
        "scaffold_diagnosis": fmt(scaffold["diagnosis"]),
        "scaffold_unstable": fmt(scaffold["unstable"]),
        "scaffold_probe": fmt(scaffold["probe"]),
        "scaffold_length_ratio": fmt(length_ratio),
        "delta_diagnosis": fmt(scaffold["diagnosis"] - baseline["diagnosis"]),
        "delta_unstable": fmt(scaffold["unstable"] - baseline["unstable"]),
        "delta_probe": fmt(scaffold["probe"] - baseline["probe"]),
        "delta_length_ratio": fmt(length_ratio - 1.0),
        "per_case_preview": preview_md,
    }

    report = render_report(args.template.read_text(encoding="utf-8"), report_payload)
    args.report_out.write_text(report, encoding="utf-8")
    print(f"report_written={args.report_out}")


if __name__ == "__main__":
    main()
