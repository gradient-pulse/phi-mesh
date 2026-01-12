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

# =============================================================================
# Corpus status helpers (Option A)
# =============================================================================


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def corpus_status(repo_root: str) -> Dict[str, Any]:
    """
    Option A corpus status.
    Looks for:
      - <repo_root>/rgpx_scientist/foundational_papers_index.yml
      - <repo_root>/rgpx_scientist/foundational_papers_manifest.yml

    Paper PDFs are resolved via each index entry's repo_path relative to repo_root.
    """
    rr = Path(repo_root)

    index_path = rr / "rgpx_scientist" / "foundational_papers_index.yml"
    manifest_path = rr / "rgpx_scientist" / "foundational_papers_manifest.yml"

    index_ok = index_path.exists()
    manifest_ok = manifest_path.exists()

    index = _load_yaml_file(index_path) if index_ok else {}
    manifest = _load_yaml_file(manifest_path) if manifest_ok else {}

    index_items = _safe_list(index.get("foundational_papers"))
    manifest_items = _safe_list(manifest.get("foundational_papers"))

    # Parse index list: require paper_id + repo_path
    parsed_index: List[Dict[str, str]] = []
    for item in index_items:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("paper_id", "")).strip()
        rpath = str(item.get("repo_path", "")).strip()
        title = str(item.get("title", "")).strip()
        if pid and rpath:
            parsed_index.append({"paper_id": pid, "repo_path": rpath, "title": title})

    indexed_count = len(parsed_index)

    # Resolve PDFs and detect missing
    present = 0
    missing: List[Dict[str, str]] = []
    for it in parsed_index:
        pdf_path = rr / it["repo_path"]
        if pdf_path.exists():
            present += 1
        else:
            missing.append({"paper_id": it["paper_id"], "repo_path": it["repo_path"]})

    # Cross-check IDs vs manifest (optional but helpful)
    index_ids = {it["paper_id"] for it in parsed_index}
    manifest_ids = set()
    for item in manifest_items:
        if isinstance(item, dict):
            pid = str(item.get("paper_id", "")).strip()
            if pid:
                manifest_ids.add(pid)

    missing_in_manifest = sorted(index_ids - manifest_ids) if manifest_ok else []
    extra_in_manifest = sorted(manifest_ids - index_ids) if manifest_ok else []

    return {
        "index_path": str(index_path),
        "manifest_path": str(manifest_path),
        "index_ok": index_ok,
        "manifest_ok": manifest_ok,
        "indexed_count": indexed_count,
        "pdf_present_count": present,
        "pdf_missing": missing,
        "missing_in_manifest": missing_in_manifest,
        "extra_in_manifest": extra_in_manifest,
    }


# =============================================================================
# Paths / Config
# =============================================================================

APP_DIR = Path(__file__).resolve().parent  # .../phi-mesh/rgpx_scientist
REPO_ROOT = APP_DIR.parent  # .../phi-mesh
PULSE_GLOB = str(REPO_ROOT / "pulse" / "*.yml")

FOUNDATIONAL_INDEX = APP_DIR / "foundational_papers_index.yml"  # Option A

BACKGROUND_CHOICES = ["Natural sciences", "Social sciences", "Economics-business"]

STOPWORDS = set(
    """
a an and are as at be been by can could did do does for from had has have he her his i if in into is it its
may might more most must no not of on or our should so than that the their them then there these they this
to was we were what when where which who why will with you your
""".split()
)

# GitHub (for clickable PDF links in citations)
GITHUB_REPO = "gradient-pulse/phi-mesh"
GITHUB_BRANCH = "main"

# Canonical tag definitions live here (NOT tag_index.yml)
TAG_DESCRIPTIONS_PATH = REPO_ROOT / "meta" / "tag_descriptions.yml"
TAG_PHASE_OVERRIDES_PATH = REPO_ROOT / "meta" / "tag_phase_overrides.yml"  # optional
ALIASES_PATH = REPO_ROOT / "meta" / "aliases.yml"

DRIVER_TAG_BLACKLIST = {
    "phi_mesh",
    "circle_pulse",
    "cf",
    "gemini",
    "o3",
    "grok",
    "claude",
    "mistral",
    "deepseek",
    "kimi",
    "ai_cohort",
    "ai_collaboration",
    "ai_reflexivity",
}

# =============================================================================
# Text utils
# =============================================================================


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s_\-]+", " ", text)
    toks = [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]
    return toks

def canon_tag(tag: str, alias_lookup: Dict[str, str]) -> str:
    t = (tag or "").strip()
    if not t:
        return t
    norm = t.lower().replace("-", "_")
    norm = re.sub(r"\s+", "_", norm)
    norm = re.sub(r"_+", "_", norm)
    return alias_lookup.get(norm, norm)

def is_url(s: str) -> bool:
    s = (s or "").strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def github_blob_url(repo_path: str) -> str:
    p = (repo_path or "").lstrip("/")
    return f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{p}"


def normalize_zenodo_key(url: str) -> str:
    """
    Normalize Zenodo-ish URLs into a comparable key.

    Examples:
      https://doi.org/10.5281/zenodo.1234567  -> 10.5281/zenodo.1234567
      https://zenodo.org/records/1234567      -> 1234567
      https://zenodo.org/record/1234567       -> 1234567
    """
    u = (url or "").strip()
    u = u.replace("http://", "https://").strip()

    if "doi.org/" in u:
        return u.split("doi.org/", 1)[1].strip().lower()

    m = re.search(r"zenodo\.org/(records|record)/(\d+)", u, re.IGNORECASE)
    if m:
        return m.group(2)

    return u.lower()


# =============================================================================
# Data models
# =============================================================================


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
    repo_path: str  # path relative to REPO_ROOT, e.g. "foundational_rgp-papers/2025-..."
    zenodo_doi_url: str


# =============================================================================
# IO
# =============================================================================


def load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


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

        alias_lookup = load_aliases()
        tags = [canon_tag(str(t).strip(), alias_lookup) for t in tags_raw] if isinstance(tags_raw, list) else []
        tags = [t for t in tags if t]
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


def build_zenodo_lookup(paper_map: Dict[str, Paper]) -> Dict[str, str]:
    """
    Returns:
      { normalized_zenodo_key: paper_id }

    This lets the app resolve "papers:" entries that are Zenodo URLs into a
    known paper_id, without rewriting old pulses.
    """
    lookup: Dict[str, str] = {}
    for pid, paper in paper_map.items():
        doi = (paper.zenodo_doi_url or "").strip()
        if not doi:
            continue

        lookup[normalize_zenodo_key(doi)] = pid

        # If DOI contains zenodo.<id>, also map numeric id for robustness
        m = re.search(r"zenodo\.(\d+)", doi, re.IGNORECASE)
        if m:
            lookup[m.group(1)] = pid

    return lookup


@st.cache_data(show_spinner=False)
def load_tag_descriptions_local() -> Dict[str, str]:
    """
    Loads meta/tag_descriptions.yml
    Expected schema: { tag_slug: "description string" }
    """
    if not TAG_DESCRIPTIONS_PATH.exists():
        return {}
    doc = yaml.safe_load(TAG_DESCRIPTIONS_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        return {}
    out: Dict[str, str] = {}
    for k, v in doc.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k.strip()] = v.strip()
    return out


@st.cache_data(show_spinner=False)
def load_tag_phase_overrides() -> Dict[str, str]:
    """
    Optional helper. If meta/tag_phase_overrides.yml exists, it can pin tags to Δ / GC / CF.

    Supported schemas (any of these):
      1) Flat mapping:
         my_tag: "Δ" | "GC" | "CF"
         other_tag: {phase: "CF"}

      2) phases:
         phases:
           Δ:  [tag1, tag2]
           GC: [tag3]
           CF: [tag4]

      3) overrides (common alt-name):
         overrides:
           Δ:  [tag1, tag2]
           GC: [tag3]
           CF: [tag4]

      4) cycle naming:
         cycles:
           cycle_1: [tag1, tag2]   # treated as Δ
           cycle_2: [tag3]         # treated as GC
           cycle_3: [tag4]         # treated as CF

      5) direct keys:
         delta: [tag1]
         gc:    [tag2]
         cf:    [tag3]
    """
    if not TAG_PHASE_OVERRIDES_PATH.exists():
        return {}

    doc = yaml.safe_load(TAG_PHASE_OVERRIDES_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        return {}

    out: Dict[str, str] = {}

    def _phase_norm(p: str) -> str:
        p = (p or "").strip().lower()
        if p in {"Δ", "delta", "d", "cycle1", "cycle_1", "cycle-1", "cycle 1", "c1"}:
            return "Δ"
        if p in {"gc", "cycle2", "cycle_2", "cycle-2", "cycle 2", "c2"}:
            return "GC"
        if p in {"cf", "cycle3", "cycle_3", "cycle-3", "cycle 3", "c3"}:
            return "CF"
        if "delta" in p:
            return "Δ"
        if "gc" in p:
            return "GC"
        if "cf" in p:
            return "CF"
        return ""

    def _ingest_list(phase: str, tags: Any) -> None:
        ph = _phase_norm(phase)
        if not ph or not isinstance(tags, list):
            return
        for t in tags:
            if isinstance(t, str) and t.strip():
                out[t.strip()] = ph

    # (1) flat mapping + dict mapping
    for k, v in doc.items():
        if isinstance(k, str) and isinstance(v, str) and v.strip():
            ph = _phase_norm(v)
            if ph:
                out[k.strip()] = ph
        if isinstance(k, str) and isinstance(v, dict) and isinstance(v.get("phase"), str):
            ph = _phase_norm(str(v.get("phase")))
            if ph:
                out[k.strip()] = ph

    # helper to read nested blocks like doc["phases"] or doc["overrides"]
    def _ingest_block(block: Any) -> None:
        if not isinstance(block, dict):
            return
        for phase, tags in block.items():
            if isinstance(phase, str):
                _ingest_list(phase, tags)

    # (2) phases:
    _ingest_block(doc.get("phases"))

    # (3) overrides:
    _ingest_block(doc.get("overrides"))

    # (4) cycles:
    cycles = doc.get("cycles")
    if isinstance(cycles, dict):
        for cyc, tags in cycles.items():
            if not isinstance(cyc, str):
                continue
            cyc_n = cyc.strip().lower().replace("-", "_").replace(" ", "_")
            if cyc_n in {"cycle_1", "c1"}:
                _ingest_list("Δ", tags)
            elif cyc_n in {"cycle_2", "c2"}:
                _ingest_list("GC", tags)
            elif cyc_n in {"cycle_3", "c3"}:
                _ingest_list("CF", tags)

    # (5) direct keys: delta/gc/cf
    for key in ("delta", "gc", "cf"):
        if key in doc:
            _ingest_list(key, doc.get(key))

    return out
    
@st.cache_data(show_spinner=False)
def load_aliases() -> Dict[str, str]:
    """
    Loads meta/aliases.yml and returns lookup: variant -> canonical
    Expected schema:
      aliases:
        canonical_tag:
          - variant1
          - variant2
    """
    if not ALIASES_PATH.exists():
        return {}
    doc = yaml.safe_load(ALIASES_PATH.read_text(encoding="utf-8")) or {}
    aliases = doc.get("aliases", {}) if isinstance(doc, dict) else {}
    if not isinstance(aliases, dict):
        return {}

    lookup: Dict[str, str] = {}

    def _norm(s: str) -> str:
        s = (s or "").strip().lower()
        s = s.replace("-", "_")
        s = re.sub(r"\s+", "_", s)
        s = re.sub(r"_+", "_", s)
        return s

    for canon, variants in aliases.items():
        if not isinstance(canon, str):
            continue
        canon_n = _norm(canon)
        lookup[canon_n] = canon_n
        if isinstance(variants, list):
            for v in variants:
                if isinstance(v, str):
                    lookup[_norm(v)] = canon_n

    return lookup

# =============================================================================
# Scoring / selection
# =============================================================================


def score_pulse(query_tokens: List[str], pulse: Pulse) -> float:
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

    if pulse.papers:
        score += 0.3
    if pulse.podcasts:
        score += 0.2
    return score


def pick_driver_and_cluster(top_pulses: List[Pulse], query_tokens: List[str]) -> Tuple[str, List[str]]:
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

    candidates = [t for t in tag_counts.keys() if t not in DRIVER_TAG_BLACKLIST]
    if not candidates:
        candidates = list(tag_counts.keys())

    best_tag = max(candidates, key=lambda t: (tag_counts[t], tag_match_bonus[t]))
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


# =============================================================================
# Paper reference resolution (supports BOTH: paper_id and Zenodo URL)
# =============================================================================


def resolve_paper_ref(ref: str, paper_map: Dict[str, Paper], zenodo_lookup: Dict[str, str]) -> Tuple[str, str, str]:
    """
    Returns (label, pdf_url, zenodo_url)

    - If ref is paper_id: uses index directly
    - If ref is Zenodo URL and matches an indexed paper's zenodo_doi_url: resolves to that paper_id
    - Otherwise:
        - If ref is URL: returns it as zenodo_url only
        - Else: returns label as raw string
    """
    ref = (ref or "").strip()
    if not ref:
        return ("", "", "")

    # paper_id direct
    if ref in paper_map:
        p = paper_map[ref]
        return (p.title or ref, github_blob_url(p.repo_path), p.zenodo_doi_url or "")

    # Zenodo URL in pulses
    if is_url(ref):
        key = normalize_zenodo_key(ref)
        pid = zenodo_lookup.get(key)
        if pid and pid in paper_map:
            p = paper_map[pid]
            return (p.title or pid, github_blob_url(p.repo_path), ref)  # keep the exact pulse URL
        return (ref, "", ref)

    # unknown string
    return (ref, "", "")


# =============================================================================
# Δ / GC / CF helpers (visible structure)
# =============================================================================


def phase_of_tag(tag: str, overrides: Dict[str, str]) -> str:
    """
    Returns 'Δ', 'GC', 'CF'.
    Uses overrides first; otherwise conservative heuristics.
    """
    if tag in overrides:
        ph = overrides[tag].upper()
        if "CF" in ph:
            return "CF"
        if "GC" in ph:
            return "GC"
        if "Δ" in ph or "DELTA" in ph:
            return "Δ"

    t = tag.lower()
    if any(x in t for x in ["context", "filter", "boundary", "constraint", "selection", "phase", "regime"]):
        return "CF"
    if any(x in t for x in ["choreograph", "resonance", "rhythm", "feedback", "coupling", "loop", "oscillat"]):
        return "GC"
    return "Δ"


def split_by_phase(tags: List[str], overrides: Dict[str, str]) -> Dict[str, List[str]]:
    out = {"Δ": [], "GC": [], "CF": []}
    for t in tags:
        out[phase_of_tag(t, overrides)].append(t)
    return out


def tag_desc(tag: str, desc_map: Dict[str, str]) -> str:
    d = desc_map.get(tag, "")
    return d.strip() if d else "(No description found in meta/tag_descriptions.yml)"


# =============================================================================
# UI
# =============================================================================

st.set_page_config(page_title="RGPx Scientist (V0)", layout="wide")

st.title("RGPx Scientist (V0)")
st.caption("Reframe → Retrieve → Δ/GC/CF → Minimal tests → Citations (Mesh-grounded)")

# --------- Corpus panel (Option A) ----------
with st.expander("Corpus (foundational papers) status", expanded=True):
    cs = corpus_status(str(REPO_ROOT))
    alias_lookup = load_aliases()
    if alias_lookup:
        st.success(f"Loaded aliases: {len(alias_lookup)} mappings (meta/aliases.yml)")
    else:
        st.warning("No aliases loaded (meta/aliases.yml missing or empty).")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("Index file")
        st.code(cs["index_path"])
        st.write("Present ✅" if cs["index_ok"] else "Missing ❌")
    with c2:
        st.write("Manifest file")
        st.code(cs["manifest_path"])
        st.write("Present ✅" if cs["manifest_ok"] else "Missing ❌")
    with c3:
        st.metric("Indexed papers", cs["indexed_count"])
        st.metric("PDFs present", cs["pdf_present_count"])

    if not cs["index_ok"] or not cs["manifest_ok"]:
        st.error("Corpus config missing. Add the missing file(s) above.")
    else:
        if cs["missing_in_manifest"]:
            st.warning("Index contains paper_id(s) missing from manifest:")
            st.code("\n".join(cs["missing_in_manifest"]))
        if cs["extra_in_manifest"]:
            st.info("Manifest contains paper_id(s) not present in index:")
            st.code("\n".join(cs["extra_in_manifest"]))

    if cs["pdf_missing"]:
        st.error(f"Missing PDFs: {len(cs['pdf_missing'])}")
        st.write("Fix list (paper_id → repo_path):")
        st.code("\n".join([f"{m['paper_id']} -> {m['repo_path']}" for m in cs["pdf_missing"]]))
    else:
        if cs["indexed_count"] > 0:
            st.success("All indexed PDFs are present.")
        else:
            st.warning("Index is present but contains 0 valid entries (paper_id + repo_path).")

    # quick sanity check for tag_descriptions.yml
    tag_desc_map = load_tag_descriptions_local()
    if tag_desc_map:
        st.success(f"Loaded tag definitions: {len(tag_desc_map)} tags (meta/tag_descriptions.yml)")
    else:
        st.warning("Tag definitions not loaded (meta/tag_descriptions.yml missing or unreadable).")

    phase_overrides = load_tag_phase_overrides()
    if phase_overrides:
        st.success(f"Loaded tag phase overrides: {len(phase_overrides)} tags (meta/tag_phase_overrides.yml)")
    else:
        st.info("No tag phase overrides loaded (meta/tag_phase_overrides.yml missing or empty).")

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
    zenodo_lookup = build_zenodo_lookup(paper_map)

    tag_desc_map = load_tag_descriptions_local()
    phase_overrides = load_tag_phase_overrides()

    query_tokens = tokenize(q)
    scored = [(score_pulse(query_tokens, p), p) for p in pulses]
    scored.sort(key=lambda x: x[0], reverse=True)

    top = [p for s, p in scored if s > 0][:8]
    if not top:
        top = [p for _, p in scored[:5]]

    driver, cluster = pick_driver_and_cluster(top, query_tokens)
    phased = split_by_phase(cluster, phase_overrides)

    hints = background_hints(background)
    papers, podcasts = render_links(top)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Problem restatement")
        st.write(q.strip() if q.strip() else "(No question provided.)")
        st.caption(hints["style"] + " " + hints["examples"])

        st.subheader("Δ (what to measure next)")
        deltas = phased["Δ"][:5] or cluster[:3]
        for t in deltas:
            d = tag_desc(t, tag_desc_map)
            short = d[:220] + ("…" if len(d) > 220 else "")
            st.markdown(f"- **{t}** — {short}")

        st.subheader("GC (mode hypotheses)")
        gcs = phased["GC"][:4]
        if not gcs:
            st.write("No explicit GC tags found in this slice; treat retrieved pulses as the source of coupled-mode hypotheses.")
        for t in gcs:
            d = tag_desc(t, tag_desc_map)
            short = d[:220] + ("…" if len(d) > 220 else "")
            st.markdown(f"- **{t}** — {short}")

        st.subheader("CF (boundary / filter suspects)")
        cfs = phased["CF"][:4]
        if not cfs:
            st.write("No explicit CF tags found in this slice; default CF suspects: environment / measurement pipeline / control-loop / hidden constraint.")
        for t in cfs:
            d = tag_desc(t, tag_desc_map)
            short = d[:220] + ("…" if len(d) > 220 else "")
            st.markdown(f"- **{t}** — {short}")

        st.subheader("Φ-trace hook (plateau / transition marker)")
        st.write(
            "Plot your key observable(s) against the smallest perturbation you changed (bias / timing / cable / ordering). "
            "Look for plateaus, hysteresis, or sudden re-ordering of what dominates the outcome. "
            "Goal: locate a transition boundary, not optimize inside one regime."
        )

        st.subheader("Smallest discriminating tests (binary)")
        st.write(
            "1) **Freeze calibration**, vary measurement/analysis only → does the step-change persist?\n"
            "2) **Freeze measurement pipeline**, vary calibration/order only → does the step-change persist?\n"
            "3) **A/B revert one micro-change** (single cable/setting) 10–20 times → toggle probability?\n"
            "4) **Reference injection / known signal** → invariant recovery across the step-change?\n"
            "5) **Environmental sentinel logging** (temp / field proxy / vibration / timing) → coincident threshold?"
        )

        st.subheader("Failure modes (quick)")
        st.write(
            "- Mis-specified observable (proxy flips meaning across regimes).\n"
            "- Hidden context shift (different conditions activate different internal routines).\n"
            "- Overfitting to one regime (test plan never crosses the suspected boundary)."
        )

    with col2:
        st.subheader("Δ→GC→CF click-path suggestion")
        st.write("Driver tag:")
        st.code(driver)
        if driver:
            with st.expander("Driver definition", expanded=False):
                st.write(tag_desc(driver, tag_desc_map))

        st.write("Cluster:")
        st.code(" → ".join(cluster))

        with st.expander("Cluster definitions", expanded=False):
            for t in cluster:
                st.markdown(f"**{t}**")
                st.write(tag_desc(t, tag_desc_map))
                st.divider()

        st.subheader("CF (most relevant pulses)")
        for p in top[:5]:
            st.markdown(f"**{p.title}** ({p.date})")
            if p.summary:
                st.write(p.summary[:420] + ("…" if len(p.summary) > 420 else ""))
            st.caption(os.path.relpath(p.path, str(REPO_ROOT)))

        st.subheader("Citations")

        if papers:
            st.write("**Papers**")
            for ref in papers[:12]:
                label, pdf_url, zenodo_url = resolve_paper_ref(ref, paper_map, zenodo_lookup)

                if not label:
                    continue

                # Prefer a GitHub PDF link if we can resolve
                if pdf_url:
                    st.markdown(f"- [{label}]({pdf_url})")
                else:
                    # If it's a URL, render clickable; else plain text
                    if is_url(label):
                        st.markdown(f"- [{label}]({label})")
                    else:
                        st.markdown(f"- {label}")

                # If we have (or were given) a Zenodo URL, show it as secondary
                if zenodo_url:
                    if is_url(zenodo_url):
                        st.markdown(f"  - Zenodo: [{zenodo_url}]({zenodo_url})")
                    else:
                        st.markdown(f"  - Zenodo: {zenodo_url}")

        if podcasts:
            st.write("**Podcasts**")
            for link in podcasts[:12]:
                link = (link or "").strip()
                if not link:
                    continue
                if is_url(link):
                    st.markdown(f"- [{link}]({link})")
                else:
                    st.markdown(f"- {link}")

        st.subheader("UD check")
        st.write("Did this move you toward a cleaner next experiment (Unity) or did it add noise (Disunity)?")
        st.write("- If **Unity**: open the driver tag in the tag map and follow the top pulse.")
        st.write("- If **Disunity**: rephrase with one concrete observable and one perturbation you can control; then re-run.")
