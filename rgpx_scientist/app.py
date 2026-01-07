import os
import glob
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import streamlit as st
import yaml

# --------- Config ----------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PULSE_GLOB = os.path.join(REPO_ROOT, "pulse", "*.yml")

BACKGROUND_CHOICES = ["Natural sciences", "Social sciences", "Economics-business"]

STOPWORDS = set("""
a an and are as at be been by can could did do does for from had has have he her his i if in into is it its
may might more most must no not of on or our should so than that the their them then there these they this
to was we were what when where which who why will with you your
""".split())

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_\-]+", " ", text)
    toks = [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]
    return toks

@dataclass
class Pulse:
    title: str
    date: str
    summary: str
    tags: List[str]
    papers: List[str]
    podcasts: List[str]
    path: str

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

def load_pulses() -> List[Pulse]:
    pulses: List[Pulse] = []
    for path in sorted(glob.glob(PULSE_GLOB)):
        data = load_yaml(path)
        title = str(data.get("title", "")).strip()
        date = str(data.get("date", "")).strip()
        summary = str(data.get("summary", "")).strip()
        tags = data.get("tags", []) or []
        papers = data.get("papers", []) or []
        podcasts = data.get("podcasts", []) or []
        if not title and not summary:
            continue
        pulses.append(Pulse(
            title=title,
            date=date,
            summary=summary,
            tags=[str(t).strip() for t in tags if str(t).strip()],
            papers=[str(p).strip() for p in papers if str(p).strip()],
            podcasts=[str(p).strip() for p in podcasts if str(p).strip()],
            path=path,
        ))
    return pulses

def score_pulse(query_tokens: List[str], pulse: Pulse) -> float:
    # Simple lexical scoring: query overlap with title+summary+tags (weighted)
    hay = " ".join([pulse.title, pulse.summary, " ".join(pulse.tags)]).lower()
    score = 0.0
    for t in query_tokens:
        if t in pulse.title.lower():
            score += 3.0
        if t in pulse.summary.lower():
            score += 2.0
        if any(t == tag.lower() for tag in pulse.tags):
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
            if any(tok in tag.lower().replace("-", "_") for tok in query_tokens):
                tag_match_bonus[tag] += 1

    if not tag_counts:
        return ("least_action", ["least_action", "meso_scale", "contextual_filter"])

    # combine counts + bonus
    best_tag = max(tag_counts.keys(), key=lambda t: (tag_counts[t], tag_match_bonus[t]))
    # cluster: top 5 tags by frequency excluding driver, plus driver first
    others = [t for t, _ in tag_counts.most_common(8) if t != best_tag]
    cluster = [best_tag] + others[:4]
    return (best_tag, cluster)

def background_hints(background: str) -> Dict[str, str]:
    if background == "Natural sciences":
        return {
            "style": "Use precise language (hypotheses, boundary conditions, measurements). Prefer mechanisms and test design.",
            "examples": "Examples: turbulence, control, stability, scaling laws, phase transitions, sensitivity to perturbations."
        }
    if background == "Social sciences":
        return {
            "style": "Use operational definitions and observables. Prefer coordination, institutions, incentives, path dependence, regime shifts.",
            "examples": "Examples: coordination failure, legitimacy, norms, feedback loops, lock-in, polarization, institutional brittleness."
        }
    return {
        "style": "Use decision and execution language. Prefer constraints, incentives, robustness, ROI-of-experiments, failure modes, deployment risks.",
        "examples": "Examples: fragility under distribution shift, operational thresholds, scenario stress tests, rollout design, governance constraints."
    }

def render_links(pulses: List[Pulse]) -> Tuple[List[str], List[str]]:
    papers = []
    podcasts = []
    for p in pulses:
        papers.extend(p.papers)
        podcasts.extend(p.podcasts)
    # de-dup while preserving order
    def dedup(xs: List[str]) -> List[str]:
        seen = set()
        out = []
        for x in xs:
            if x and x not in seen:
                out.append(x)
                seen.add(x)
        return out
    return dedup(papers), dedup(podcasts)

# --------- UI ----------
st.set_page_config(page_title="RGPx Scientist (V0)", layout="wide")

st.title("RGPx Scientist (V0)")
st.caption("Reframe → Retrieve → Hypothesize → Minimal tests → Failure modes → Citations (Mesh-grounded)")

background = st.selectbox("Background", BACKGROUND_CHOICES, index=0)
q = st.text_area("Research question", placeholder="Describe the non-linear phenomenon or the stuck point. Keep it concrete.", height=120)

if st.button("Generate (retrieval-first)"):
    pulses = load_pulses()
    if not pulses:
        st.error("No pulses found. Expected pulse/*.yml at repo root.")
        st.stop()

    query_tokens = tokenize(q)
    scored = [(score_pulse(query_tokens, p), p) for p in pulses]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for s, p in scored if s > 0][:8]
    if not top:
        top = [p for _, p in scored[:5]]

    driver, cluster = pick_driver_and_cluster(top, query_tokens)
    hints = background_hints(background)
    papers, podcasts = render_links(top)

    # ---- Output sections ----
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
            st.caption(os.path.relpath(p.path, REPO_ROOT))

        st.subheader("Citations")
        if papers:
            st.write("**Papers**")
            for link in papers[:10]:
                st.write(link)
        if podcasts:
            st.write("**Podcasts**")
            for link in podcasts[:10]:
                st.write(link)

        st.subheader("UD check")
        st.write("Did this increase coherence (Unity) or did it lose you (Disunity)?")
        st.write("- If **Unity**: proceed by clicking the driver tag in the tag map and reading the top pulse.")
        st.write("- If **Disunity**: switch background selector and re-run; if still Disunity, rephrase the question with one concrete observable.")
