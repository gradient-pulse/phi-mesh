# tools/agent_rhythm/make_pulse.py
# Emit a Phi-Mesh pulse YAML from computed NT-rhythm metrics.
# Filename convention: YYYY-MM-DD_<dataset>.yml  (date-first)

import argparse
import json
import os
from datetime import date

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON produced by cli.py")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug (used in filename)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory for the pulse YAML")
    args = ap.parse_args()

    # Load metrics (robust to missing keys)
    with open(args.metrics, "r", encoding="utf-8") as f:
        m = json.load(f) if os.path.getsize(args.metrics) else {}

    n       = m.get("n")
    mean_dt = m.get("mean_dt")
    cv_dt   = m.get("cv_dt")  # coefficient of variation

    # Make a compact one-line summary (strict pulse format prefers one-liners).
    # Unknown values are rendered as '?'.
    def fmt(x):
        if x is None:
            return "?"
        if isinstance(x, float):
            # keep it readable but stable
            return f"{x:.6g}"
        return str(x)

    summary = (
        f"NT rhythm probe on '{args.dataset}': "
        f"n={fmt(n)}, mean_dt={fmt(mean_dt)}, cv_dt={fmt(cv_dt)}."
    )

    # Tags: space-separated → YAML list
    tags = [t for t in args.tags.split() if t.strip()]

    # Prepare YAML text (strict fields: title, summary, tags, papers, podcasts)
    yaml_text = (
        f"title: {args.title}\n"
        f"summary: '{summary}'\n"
        f"tags:\n" +
        "".join([f"  - {t}\n" for t in tags]) +
        "papers: []\n"
        "podcasts: []\n"
    )

    # Ensure output dir exists
    os.makedirs(args.outdir, exist_ok=True)

    # Date-first filename
    today = date.today().isoformat()
    out_path = os.path.join(args.outdir, f"{today}_{args.dataset}.yml")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(yaml_text)

    print(f"[make_pulse] Wrote {out_path}")

if __name__ == "__main__":
    main()
