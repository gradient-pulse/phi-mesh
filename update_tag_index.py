# --- Alias + YAML helpers -----------------------------------------------------
from pathlib import Path
import yaml
import re
from typing import Dict, Iterable, Any

def load_alias_map(path: str | Path) -> dict:
    """Load meta/aliases.yml → return {'canonical': [aliases...], ...} or {}."""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return (data.get("aliases") or {}) if isinstance(data, dict) else {}

def build_alias_index(alias_spec: dict) -> Dict[str, str]:
    """
    Build alias → canonical index.
    - Exact alias strings map to canonical.
    - Also add a lowercase-normalized lookup for resilience.
    """
    idx: Dict[str, str] = {}
    def norm(s: str) -> str:
        # loose normalization for lookup only (not for output)
        return re.sub(r"[\s_\-]+", " ", s).strip().casefold()

    for canonical, aliases in alias_spec.items():
        if not isinstance(aliases, Iterable) or isinstance(aliases, (str, bytes)):
            continue
        # canonical should also match itself
        idx[canonical] = canonical
        idx[norm(canonical)] = canonical
        for a in aliases:
            if not a:
                continue
            idx[a] = canonical
            idx[norm(a)] = canonical
    return idx

def normalize_tag(tag: str, alias_index: Dict[str, str]) -> str:
    """
    Map tag → canonical using alias_index. If not found, attempt loose match by
    collapsing separators + casefold; otherwise return the original tag unchanged.
    """
    if not isinstance(tag, str):
        return tag
    if tag in alias_index:
        return alias_index[tag]
    key = re.sub(r"[\s_\-]+", " ", tag).strip().casefold()
    return alias_index.get(key, tag)

def to_plain_dict(obj: Any) -> Any:
    """
    Recursively convert OrderedDict/other mapping types to plain dicts/lists so
    yaml.safe_dump doesn’t raise RepresenterError.
    """
    from collections.abc import Mapping
    if isinstance(obj, Mapping):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_plain_dict(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_plain_dict(v) for v in obj]
    return obj
# ----------------------------------------------------------------------------- 
