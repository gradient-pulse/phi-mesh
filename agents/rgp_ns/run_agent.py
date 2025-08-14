# --- helpers: write auto pulse ------------------------------------------------
from pathlib import Path
import yaml, re, datetime as dt

def _norm_tag(s: str) -> str:
    return re.sub(r"[\s\-]+", "_", (s or "").strip())

def _ensure_experimenter_pulse(tags):
    base = [t for t in (tags or []) if t]
    # case/underscore-insensitive guard
    lower = { _norm_tag(t).casefold() for t in base }
    if "experimenterpulse" not in lower:
        base.append("ExperimenterPulse")
    return sorted(set(base), key=_norm_tag)

def write_auto_pulse(dataset_id: str, summary: str, extra_tags=None, papers=None, podcasts=None):
    """Create/append an auto pulse under pulse/auto/ for this run."""
    extra_tags   = extra_tags   or []
    papers       = papers       or []
    podcasts     = podcasts     or []

    ts = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    title = f"{dataset_id}: Experimenter auto-pulse"
    tags  = _ensure_experimenter_pulse(["RGP"] + extra_tags)  # always include RGP + ExperimenterPulse

    payload = {
        "title":   title,
        "date":    ts,
        "summary": summary.strip(),
        "tags":    tags,
        # keep only URL-backed entries; title optional
        "papers":   [it for it in (papers or [])   if isinstance(it, dict) and it.get("url")],
        "podcasts": [it for it in (podcasts or []) if isinstance(it, dict) and it.get("url")],
        "status": "auto",
    }

    outdir = Path("pulse/auto")
    outdir.mkdir(parents=True, exist_ok=True)
    # timestamp-first filename sorts chronologically
    fname = f"{dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{_norm_tag(dataset_id)}.yml"
    with (outdir / fname).open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    print(f"auto-pulse: wrote {outdir / fname}")
