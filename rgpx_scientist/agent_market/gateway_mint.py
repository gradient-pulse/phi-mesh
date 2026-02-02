import os, re, json, hashlib
from datetime import datetime, timedelta, timezone
import yaml
import urllib.request

LEDGER_PATH = "rgpx_scientist/agent_market/ledger.json"
AGENT_ID_RE = re.compile(r"^agent:@[A-Za-z0-9_]{1,32}$")

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_yaml_block(issue_body: str) -> dict:
    # Expect a fenced ```yaml block. If multiple exist, take the first.
    m = re.search(r"```yaml\s*(.*?)\s*```", issue_body, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError("No ```yaml fenced block found in issue body.")

    yaml_text = m.group(1)

    # YAML forbids tab indentation; submissions often contain tabs in copied output.
    yaml_text = yaml_text.replace("\t", "  ")

    return yaml.safe_load(yaml_text)

def load_ledger() -> dict:
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ledger(ledger: dict) -> None:
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        f.write("\n")

def issue_comment(repo: str, issue_number: int, token: str, body: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    payload = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "rgpx-gateway-mint",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        resp.read()

def is_duplicate_recent(ledger: dict, output_hash: str, window_days: int = 14) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    for ev in ledger.get("events", []):
        if ev.get("output_hash") != output_hash:
            continue
        ts = ev.get("timestamp_utc")
        if not ts:
            continue
        try:
            t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            continue
        if t >= cutoff:
            return True
    return False

def main():
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = int(os.environ.get("ISSUE_NUMBER", "0"))
    issue_url = os.environ.get("ISSUE_URL", "")
    repo = os.environ.get("REPO", "")
    token = os.environ.get("GITHUB_TOKEN", "")

    try:
        data = parse_yaml_block(issue_body)
    except Exception as e:
        issue_comment(repo, issue_number, token, f"❌ Gateway parse failed: {e}")
        raise

    agent_id = (data.get("agent_id") or "").strip()
    prompt = (data.get("prompt") or "").strip()
    output = (data.get("output") or "").strip()
    domain = (data.get("domain") or "").strip()
    claim = (data.get("claim") or "").strip()
    ts_in = (data.get("timestamp_utc") or "").strip()

    # Minimal “growth-first” gate: require agent_id + non-empty prompt/output.
    # (You can tighten later.)
    errors = []
    if not AGENT_ID_RE.match(agent_id):
        errors.append("agent_id must match: agent:@handle (letters/numbers/_), max 32 chars after @.")
    if len(prompt) < 40:
        errors.append("prompt too short (min 40 chars).")
    if len(output) < 200:
        errors.append("output too short (min 200 chars).")

    if errors:
        issue_comment(repo, issue_number, token, "❌ Gateway FAIL (no credit):\n- " + "\n- ".join(errors))
        return

    prompt_hash = sha256(prompt)
    output_hash = sha256(output)

    ledger = load_ledger()

    # Hard guard: one issue can mint at most once
    for ev in ledger.get("events", []):
        if ev.get("event") == "mint" and int(ev.get("issue_number", -1)) == issue_number:
            issue_comment(repo, issue_number, token, "⛔ Already minted for this issue. No additional credit.")
            return

    # Dedupe guard: prevent farming via identical outputs within the window
    if is_duplicate_recent(ledger, output_hash, window_days=14):
        issue_comment(repo, issue_number, token, "⛔ Duplicate within 14 days (by output_hash). No credit minted.")
        return

    # Receipt ID: stable enough for now
    receipt_seed = f"{agent_id}|{issue_number}|{output_hash}"
    receipt_id = sha256(receipt_seed)[:16]

    ts = ts_in if ts_in else now_utc_iso()

    event = {
        "timestamp_utc": ts,
        "event": "mint",
        "receipt_id": receipt_id,
        "credit_delta": 1,
        "agent_id": agent_id,
        "domain": domain,
        "claim": claim,
        "prompt_hash": prompt_hash,
        "output_hash": output_hash,
        "issue_url": issue_url,
        "issue_number": issue_number,
        "note": "v0 growth-first gate: minimal prompt/output length + agent_id format"
    }

    ledger.setdefault("agents", {})
    ledger.setdefault("events", [])

    # Maintain agent balance summary
    agent = ledger["agents"].setdefault(agent_id, {"earned": 0})
    agent["earned"] = int(agent.get("earned", 0)) + 1

    ledger["events"].append(event)
    ledger["version"] = ledger.get("version", "0.2")

    save_ledger(ledger)

    issue_comment(
        repo,
        issue_number,
        token,
        f"✅ Credited: 1\n\nreceipt_id: `{receipt_id}`\noutput_hash: `{output_hash[:12]}…`\nledger updated."
    )

if __name__ == "__main__":
    main()
