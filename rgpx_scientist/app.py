#!/usr/bin/env python3
# phi-mesh/rgpx_scientist/app.py

from __future__ import annotations

import glob
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st
import yaml

# --------- Paths / Config ----------
APP_DIR = Path(__file__).resolve().parent                 # .../phi-mesh/rgpx_scientist
REPO_ROOT = APP_DIR.parent                               # .../phi-mesh
PULSE_GLOB = str(REPO_ROOT / "pulse" / "*.yml")

FOUNDATIONAL_INDEX = APP_DIR / "foundational_papers_index.yml"  # Option A
# PDFs live here (relative to REPO_ROOT): foundational_rgp-papers/...
# (repo_path in index should already point into foundational_rgp-papers/...)

BACKGROUND_CHOICES = ["Natural sciences", "Social sciences", "Economics-business"]

STOPWORDS = set(
    """
a an and are as at be been by can could did do does for from had has have he her his i if in into is it its
may might more most must no not of on or our should so than that the their them then there these they this
to was we were what when where which who why will with you your
""".split()
)

# --------- Text utils ----------
def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s_\-]+", " ", text)
    toks = [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]
    return toks


def is_url(s: str) -> bool:
    s = (s or "").strip().lower()
    return s.startswith("http://") or s.startswith("https://")


# --------- Data models ----------
@dataclass
class Pulse:
    title: str
    date: str
    summary: str
    tags: List[str]
    papers: List[str]
    podcasts: List[str]
    path: str


@dataclass
class Paper:
    paper_id: str
    title: str
    repo_path: str          # path relative to REPO_ROOT, e.g. "foundational_rgp-papers/2025-..."
    zenodo_doi_url: str


# --------- IO ----------
def load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return {}
    return data


@st.cache_data(show_spinner=False)
def load_pulses() -> List[Pulse]:
    pulses: List[Pulse] = []
    for path in sorted(glob.glob(PULSE_GLOB)):
        data = load_yaml(path)

        title = str(data.get("title", "") or "").strip()
        date = str(data.get("date", "") or "").strip()
        summary = str(data.get("summary", "") or "").strip()

        tags_raw = data.get("tags", []) or []
        papers_raw = data.get("papers", []) or []
        podcasts_raw = data.get("podcasts", []) or []

        tags = [str(t).strip() for t in tags_raw if str(t).strip()] if isinstance(tags_raw, list) else []
        papers = [str(p).strip() for p in papers_raw if str(p).strip()] if isinstance(papers_raw, list) else []
        podcasts = [str(p).strip() for p in podcasts_raw if str(p).strip()] if isinstance(podcasts_raw, list) else []

        if not title and not summary:
            continue

        pulses.append(
            Pulse(
                title=title,
                date=date,
                summary=summary,
                tags=tags,
                papers=papers,
                podcasts=podcasts,
                path=path,
            )
        )
    return pulses


@st.cache_data(show_spinner=False)
def load_foundational_papers() -> Dict[str, Paper]:
    """
    Loads phi-mesh/rgpx_scientist/foundational_papers_index.yml (Option A).
    Returns dict: paper_id -> Paper
    """
    if not FOUNDATIONAL_INDEX.exists():
        return {}

    data = load_yaml(FOUNDATIONAL_INDEX)
    items = data.get("foundational_papers", []) or []
    if not isinstance(items, list):
        return {}

    out: Dict[str, Paper] = {}
    for item in items:
        if not isinstance(item, dict):
            continue

        paper_id = str(item.get("paper_id", "") or "").strip()
        title = str(item.get("title", "") or "").strip()
        repo_path = str(item.get("repo_path", "") or "").strip()
        zenodo = str(item.get("zenodo_doi_url", "") or "").strip()

        if not paper_id or not repo_path:
            continue

        out[paper_id] = Paper(
            paper_id=paper_id,
            title=title or paper_id,
            repo_path=repo_path,
            zenodo_doi_url=zenodo,
        )
    return out


# --------- Scoring / selection ----------
def score_pulse(query_tokens: List[str], pulse: Pulse) -> float:
    # Simple lexical scoring: query overlap with title+summary+tags (weighted)
    hay = " ".join([pulse.title, pulse.summary, " ".join(pulse.tags)]).lower()
    score = 0.0
    title_l = pulse.title.lower()
    summary_l = pulse.summary.lower()
    tags_l = [t.lower() for t in pulse.tags]

    for t in query_tokens:
        if t in title_l:
            score += 3.0
        if t in summary_l:
            score += 2.0
        if any(t == tag for tag in tags_l):
            score += 4.0
        if t in hay:
            score += 0.5

    # slight boost for having papers/podcasts
    if pulse.papers:
        score += 0.3
    if pulse.podcasts:
        score += 0.2
    return score


def pick_driver_and_cluster(top_pulses: List[Pulse], query_tokens: List[str]) -> Tuple[str, List[str]]:
    # Driver tag: most frequent tag among top pulses, with slight match preference to query tokens
    tag_counts = Counter()
    tag_match_bonus = Counter()

    for p in top_pulses:
        for tag in p.tags:
            tag_counts[tag] += 1
            norm = tag.lower().replace("-", "_")
            if any(tok in norm for tok in query_tokens):
                tag_match_bonus[tag] += 1

    if not tag_counts:
        return ("least_action", ["least_action", "meso_scale", "contextual_filter"])

    best_tag = max(tag_counts.keys(), key=lambda t: (tag_counts[t], tag_match_bonus[t]))
    others = [t for t, _ in tag_counts.most_common(8) if t != best_tag]
    cluster = [best_tag] + others[:4]
    return (best_tag, cluster)


def background_hints(background: str) -> Dict[str, str]:
    if background == "Natural sciences":
        return {
            "style": "Use precise language (hypotheses, boundary conditions, measurements). Prefer mechanisms and test design.",
            "examples": "Examples: turbulence, control, stability, scaling laws, phase transitions, sensitivity to perturbations.",
        }
    if background == "Social sciences":
        return {
            "style": "Use operational definitions and observables. Prefer coordination, institutions, incentives, path dependence, regime shifts.",
            "examples": "Examples: coordination failure, legitimacy, norms, feedback loops, lock-in, polarization, institutional brittleness.",
        }
    return {
        "style": "Use decision and execution language. Prefer constraints, incentives, robustness, ROI-of-experiments, failure modes, deployment risks.",
        "examples": "Examples: fragility under distribution shift, operational thresholds, scenario stress tests, rollout design, governance constraints.",
    }


def render_links(pulses: List[Pulse]) -> Tuple[List[str], List[str]]:
    papers: List[str] = []
    podcasts: List[str] = []
    for p in pulses:
        papers.extend(p.papers)
        podcasts.extend(p.podcasts)

    def dedup(xs: List[str]) -> List[str]:
        seen = set()
        out: List[str] = []
        for x in xs:
            if x and x not in seen:
                out.append(x)
                seen.add(x)
        return out

    return dedup(papers), dedup(podcasts)


def resolve_paper_ref(ref: str, paper_map: Dict[str, Paper]) -> Tuple[str, str, str, Path | None]:
    """
    Returns (kind, label, url, abs_path)
      kind: "url" | "local" | "raw"
      label: friendly label for display
      url: zenodo/url if available
      abs_path: local pdf path if local
    """
    ref = (ref or "").strip()
    if not ref:
        return ("raw", "", "", None)

    if is_url(ref):
        return ("url", ref, ref, None)

    if ref in paper_map:
        p = paper_map[ref]
        abs_path = (REPO_ROOT / p.repo_path).resolve()
        return ("local", p.title, p.zenodo_doi_url, abs_path)

    return ("raw", ref, "", None)


# --------- UI ----------
st.set_page_config(page_title="RGPx Scientist (V0)", layout="wide")

st.title("RGPx Scientist (V0)")
st.caption("Reframe → Retrieve → Hypothesize → Minimal tests → Failure modes → Citations (Mesh-grounded)")

background = st.selectbox("Background", BACKGROUND_CHOICES, index=0)
q = st.text_area(
    "Research question",
    placeholder="Describe the non-linear phenomenon or the stuck point. Keep it concrete.",
    height=120,
)

if st.button("Generate (retrieval-first)"):
    pulses = load_pulses()
    if not pulses:
        st.error("No pulses found. Expected phi-mesh/pulse/*.yml (relative to this app).")
        st.stop()

    paper_map = load_foundational_papers()

    query_tokens = tokenize(q)
    scored = [(score_pulse(query_tokens, p), p) for p in pulses]
    scored.sort(key=lambda x: x[0], reverse=True)

    top = [p for s, p in scored if s > 0][:8]
    if not top:
        top = [p for _, p in scored[:5]]

    driver, cluster = pick_driver_and_cluster(top, query_tokens)
    hints = background_hints(background)
    papers, podcasts = render_links(top)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Problem restatement")
        st.write(q.strip() if q.strip() else "(No question provided.)")

        st.subheader("Competing explanations (starter set)")
        st.write(
            "- Explanation A (mechanism): Identify the dominant feedback loop(s) and the constraint that makes the response non-linear.\n"
            "- Explanation B (threshold/phase): Identify which parameter likely pushes the system across a regime boundary.\n"
            "- Explanation C (context/filter): Identify which context/condition selects a different internal routine (or measurement interpretation)."
        )
        st.caption(hints["style"] + " " + hints["examples"])

        st.subheader("Discriminating tests (minimal experiments)")
        st.write(
            "1) Perturb one control parameter slightly and measure sensitivity/variance.\n"
            "2) Hold context fixed; change representation/measurement; check invariance.\n"
            "3) Stress the suspected boundary condition; look for discontinuity or hysteresis."
        )

        st.subheader("Boundary conditions")
        st.write(
            "- What must be true for the phenomenon to appear?\n"
            "- What breaks it (limits, saturation, time-scale separation, measurement artifacts)?\n"
            "- Which variables are confounded and need isolation?"
        )

        st.subheader("Failure modes")
        st.write(
            "- Mis-specified observable (measuring a proxy that flips meaning across regimes).\n"
            "- Hidden context shift (different conditions activate different dynamics).\n"
            "- Overfitting to a regime (test plan doesn’t cross the suspected threshold)."
        )

    with col2:
        st.subheader("GC (tag cluster) → click-path suggestion")
        st.write("Driver tag:")
        st.code(driver)
        st.write("Cluster:")
        st.code(" → ".join(cluster))

        st.subheader("CF (most relevant pulses)")
        for p in top[:5]:
            st.markdown(f"**{p.title}** ({p.date})")
            if p.summary:
                st.write(p.summary[:420] + ("…" if len(p.summary) > 420 else ""))
            st.caption(os.path.relpath(p.path, str(REPO_ROOT)))

        st.subheader("Citations")
        if papers:
            st.write("**Papers**")
            for i, ref in enumerate(papers[:10]):
                kind, label, url, abs_path = resolve_paper_ref(ref, paper_map)

                if kind == "url":
                    st.write(label)

                elif kind == "local":
                    st.markdown(f"**{label}**")
                    if url:
                        st.write(url)

                    if abs_path is not None and abs_path.exists():
                        try:
                            pdf_bytes = abs_path.read_bytes()
                            st.download_button(
                                label="Download PDF",
                                data=pdf_bytes,
                                file_name=abs_path.name,
                                mime="application/pdf",
                                key=f"dl_{i}_{abs_path.name}",
                            )
                        except Exception as e:
                            st.warning(f"Could not read PDF: {abs_path} ({e})")
                    else:
                        st.warning(f"PDF not found at: {abs_path}")

                else:
                    st.write(label)

        if podcasts:
            st.write("**Podcasts**")
            for link in podcasts[:10]:
                st.write(link)

        st.subheader("UD check")
        st.write("Did this increase coherence (Unity) or did it lose you (Disunity)?")
        st.write("- If **Unity**: proceed by clicking the driver tag in the tag map and reading the top pulse.")
        st.write("- If **Disunity**: switch background selector and re-run; if still Disunity, rephrase the question with one concrete observable.")
