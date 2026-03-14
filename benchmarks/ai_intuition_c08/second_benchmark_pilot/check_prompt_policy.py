#!/usr/bin/env python3
"""Tiny local smoke test for locked operational prompt policy."""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass

try:
    from prompt_policy import build_operational_prompt
except ModuleNotFoundError:
    # Back-compat fallback for checkouts where prompt construction still lives in a runner.
    from run_anti_overcall_stability import build_prompt as build_operational_prompt


@dataclass(frozen=True)
class _DummyItem:
    question_stem: str
    options: dict[str, str]


def _render_prompt(*, question_stem: str, options: dict[str, str], anti_overcall: bool | None = None) -> str:
    """Call the operational prompt builder across legacy/new call signatures."""
    params = inspect.signature(build_operational_prompt).parameters

    if "question_stem" in params and "options" in params:
        kwargs = {"question_stem": question_stem, "options": options}
        if anti_overcall is not None and "anti_overcall" in params:
            kwargs["anti_overcall"] = anti_overcall
        return build_operational_prompt(**kwargs)

    item = _DummyItem(question_stem=question_stem, options=options)
    if "anti_overcall" in params:
        value = True if anti_overcall is None else anti_overcall
        return build_operational_prompt(item, anti_overcall=value)
    return build_operational_prompt(item)


def main() -> None:
    question_stem = "Adult with cough, fever, and pleuritic chest pain; choose the best diagnosis."
    options = {
        "Pneumonia": "Fever and focal lung findings",
        "URTI": "Mild upper-airway symptoms",
        "GERD": "Burning chest discomfort after meals",
        "Costochondritis": "Reproducible chest wall tenderness",
        "Acute myocardial infarction": "Ischemic chest pain pattern",
    }

    default_prompt = _render_prompt(question_stem=question_stem, options=options)
    no_guardrail_prompt = _render_prompt(
        question_stem=question_stem,
        options=options,
        anti_overcall=False,
    )

    required_lines = [
        'Return JSON only as {"answer": "<exact option label>"}.',
        "1) The answer MUST be copied verbatim from one of the provided option labels.",
        "2) Do not output any rationale, confidence, or extra keys.",
        "3) Do not favor severe/cardiac options unless uniquely supported by the evidence IDs.",
    ]
    for line in required_lines:
        assert line in default_prompt, f"Missing required default policy line: {line}"

    assert (
        "3) Do not favor severe/cardiac options unless uniquely supported by the evidence IDs."
        not in no_guardrail_prompt
    ), "anti_overcall=False prompt unexpectedly contains anti-overcall rule"

    serialized_options = json.dumps(options, ensure_ascii=False)
    assert question_stem in default_prompt, "Question stem missing from default prompt"
    assert question_stem in no_guardrail_prompt, "Question stem missing from anti_overcall=False prompt"
    assert serialized_options in default_prompt, "Serialized options missing from default prompt"
    assert serialized_options in no_guardrail_prompt, "Serialized options missing from anti_overcall=False prompt"

    print("prompt_policy_check=ok")


if __name__ == "__main__":
    main()
