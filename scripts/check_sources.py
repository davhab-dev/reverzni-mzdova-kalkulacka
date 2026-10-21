#!/usr/bin/env python3
"""Checks whether selected official pages have changed.

A page-content change is only a signal for human review; it is NOT proof
that a statutory wage parameter changed. The status stays unverified until
the calculator's actual parameters are reviewed by a person.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "status.json"
SNAPSHOT_PATH = ROOT / "source_snapshot.json"

SOURCES = {
    "financni_sprava": "https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/obecne-informace",
    "cssz": "https://www.cssz.cz/web/cz/pojistne-na-socialni-zabezpeceni",
    "vzp": "https://www.vzp.cz/platci/informace/pojistne/pojistne-zamestnancu",
}

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback

def fetch_text(url):
    request = Request(url, headers={"User-Agent": "ReverzniMzdovaKalkulackaSourceCheck/1.0 (scheduled source-change check)"})
    with urlopen(request, timeout=25) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    parser = VisibleText()
    parser.feed(html)
    visible = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    if len(visible) < 200:
        raise RuntimeError("Stránka vrátila nečekaně málo čitelného textu")
    return visible

def main():
    checked_at = now_iso()
    previous = load_json(SNAPSHOT_PATH, {"sources": {}})
    previous_sources = previous.get("sources", {})
    next_sources = {}
    changed = []
    errors = []

    for key, url in SOURCES.items():
        try:
            visible = fetch_text(url)
            digest = hashlib.sha256(visible.encode("utf-8")).hexdigest()
            old = previous_sources.get(key, {}).get("sha256")
            if old and old != digest:
                changed.append(key)
            next_sources[key] = {"url": url, "sha256": digest, "checked_at": checked_at}
            print(f"OK {key}: {digest[:12]}")
        except Exception as exc:
            errors.append({"source": key, "message": str(exc)})
            # Preserve last successful fingerprint, if any, so a temporary
            # outage does not become a false source-content change.
            if key in previous_sources:
                next_sources[key] = previous_sources[key]
            else:
                next_sources[key] = {"url": url, "sha256": None, "checked_at": None}
            print(f"ERROR {key}: {exc}")

    old_status = load_json(STATUS_PATH, {"status": "unknown"}).get("status", "unknown")
    if errors:
        state = "unknown"
        message = "Kontrolu oficiálních zdrojů se nepodařilo dokončit."
    elif changed:
        state = "new"
        message = "Obsah alespoň jednoho oficiálního zdroje se změnil. Je nutné ověřit, zda to ovlivňuje mzdové parametry."
    else:
        # A first run establishes the technical baseline only. It does not
        # certify that the calculator's parameter values are correct.
        all_have_baseline = all(previous_sources.get(k, {}).get("sha256") for k in SOURCES)
        if all_have_baseline and old_status == "verified":
            state = "verified"
            message = "Od posledního ověření nebyly zjištěny změny ve sledovaném obsahu zdrojů."
        elif old_status == "new":
            state = "new"
            message = "Byla zjištěna změna zdroje; stav čeká na ruční kontrolu mzdových parametrů."
        else:
            state = "unknown"
            message = "Zdroje byly technicky zkontrolovány, ale mzdové parametry kalkulačky zatím nebyly potvrzeny."

    STATUS_PATH.write_text(json.dumps({
        "status": state,
        "checked_at": checked_at,
        "parameter_year": 2026,
        "check_type": "official_page_content_change_detection",
        "message": message,
        "changed_sources": changed,
        "errors": errors,
        "review_required": state in ("new", "unknown")
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    SNAPSHOT_PATH.write_text(json.dumps({
        "checked_at": checked_at,
        "sources": next_sources
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Result: {state}; changed={changed}; errors={len(errors)}")

if __name__ == "__main__":
    main()
