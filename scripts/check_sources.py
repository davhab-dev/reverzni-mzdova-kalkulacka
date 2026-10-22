#!/usr/bin/env python3
"""Verify calculator constants against explicit values published by official sources.

This checker does not infer new legal values from arbitrary page changes. If a
required value cannot be found or a calculator constant differs, it marks the
status for review instead of claiming the calculator is current.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "status.json"
SNAPSHOT_PATH = ROOT / "source_snapshot.json"
SOURCES = {
    "financni_sprava": "https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/obecne-informace",
    "financni_sprava_qa": "https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/dotazy-a-odpovedi/2026/aktualni-dotazy-a-odpovedi-k-dani-z",
    "mpsv_socialni": "https://mpsv.gov.cz/socialni-pojisteni",
    "vzp": "https://www.vzp.cz/platci/informace/zamestnavatel/vymerovaci-zaklad-a-vypocet-pojistneho",
}

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.hidden:
            self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden:
            value = re.sub(r"\\s+", " ", data).strip()
            if value:
                self.parts.append(value)

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def fetch_text(url):
    req = Request(url, headers={"User-Agent": "ReverzniMzdovaKalkulacka/2.0"})
    with urlopen(req, timeout=30) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    parser = VisibleText()
    parser.feed(raw.decode(charset, errors="replace"))
    text = re.sub(r"\\s+", " ", " ".join(parser.parts)).strip()
    if len(text) < 200:
        raise RuntimeError("Zdroj vrátil nečekaně málo čitelného textu")
    return text

def has_any(text, patterns):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def main():
    checked_at = now_iso()
    year = datetime.now(timezone.utc).year
    old_status = json.loads(STATUS_PATH.read_text(encoding="utf-8")) if STATUS_PATH.exists() else {}
    old_snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")) if SNAPSHOT_PATH.exists() else {"sources": {}}
    texts, errors, fingerprints = {}, [], {}
    import hashlib
    for key, url in SOURCES.items():
        try:
            text = fetch_text(url)
            texts[key] = text
            fingerprints[key] = {"url": url, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "checked_at": checked_at}
            print(f"OK {key}")
        except Exception as exc:
            errors.append({"source": key, "message": str(exc)})
            fingerprints[key] = old_snapshot.get("sources", {}).get(key, {"url": url, "sha256": None, "checked_at": None})
            print(f"ERROR {key}: {exc}")

    checks = []
    def check(label, source, patterns):
        passed = source in texts and has_any(texts[source], patterns)
        checks.append({"parameter": label, "source": source, "matched": passed})
        if not passed:
            print(f"REVIEW REQUIRED: {label}")

    # Values currently hard-coded in calc() in index.html. Patterns deliberately
    # require explicit official-source text, not just a page hash change.
    check("employee social insurance 7.1%", "mpsv_socialni", [r"zaměstnanc.{0,80}7[,.]1\s*%", r"7[,.]1\s*%.{0,80}zaměstnanc"])
    check("taxpayer credit 30,840 CZK/year", "financni_sprava", [r"30\s*840\s*Kč.{0,80}poplatník", r"poplatník.{0,80}30\s*840\s*Kč"])
    check("taxpayer credit 2,570 CZK/month", "financni_sprava", [r"2\s*570\s*Kč.{0,80}měsíčně", r"měsíčně.{0,80}2\s*570\s*Kč"])
    check("child credit 1,267 CZK/month", "financni_sprava_qa", [r"1\s*267\s*Kč"])
    check("child credit 1,860 CZK/month", "financni_sprava_qa", [r"1\s*860\s*Kč"])
    check("child credit 2,320 CZK/month", "financni_sprava_qa", [r"2\s*320\s*Kč"])
    check("minimum wage 22,400 CZK", "vzp", [r"22\s*400\s*Kč"])
    # The current tax-band threshold and all rounding/bonus rules also need
    # source-level verification; fail closed until their official evidence is
    # explicitly added to this checker.
    check("23% tax-band monthly threshold", "financni_sprava", [r"146\s*901", r"36násobku.{0,100}průměrné mzdy"])
    check("minimum child bonus 50 CZK", "financni_sprava_qa", [r"50\s*Kč"])
    check("child bonus income threshold 11,200 CZK", "financni_sprava_qa", [r"11\s*200\s*Kč"])

    failed = [x["parameter"] for x in checks if not x["matched"]]
    if errors:
        state = "unknown"
        message = "Kontrolu oficiálních zdrojů se nepodařilo dokončit."
    elif failed:
        state = "review"
        message = "Některé finanční parametry se nepodařilo potvrdit v oficiálních zdrojích. Je nutná kontrola; kalkulačka nebyla automaticky změněna."
    else:
        state = "verified"
        message = "Kontrolované finanční hodnoty byly nalezeny v oficiálních zdrojích. Ověření pokrývá pouze uvedené parametry."

    STATUS_PATH.write_text(json.dumps({
        "status": state, "checked_at": checked_at, "parameter_year": year,
        "check_type": "explicit_official_parameter_checks", "message": message,
        "changed_sources": [], "errors": errors, "checks": checks,
        "failed_parameters": failed, "review_required": state != "verified"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SNAPSHOT_PATH.write_text(json.dumps({"checked_at": checked_at, "sources": fingerprints}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Result: {state}; failed={len(failed)}; errors={len(errors)}")

if __name__ == "__main__":
    main()
