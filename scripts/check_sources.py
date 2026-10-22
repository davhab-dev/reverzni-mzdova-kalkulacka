#!/usr/bin/env python3
"""Fail-closed validation of payroll constants against official Czech sources.

A source-page change is not treated as a parameter change. Values are checked
explicitly, and the calculator's implementation is inspected before status can
be marked verified. This script intentionally does not rewrite legal constants
from loosely matched page text: ambiguous changes require human review.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "status.json"
SNAPSHOT_PATH = ROOT / "source_snapshot.json"
INDEX_PATH = ROOT / "index.html"
SOURCES = {
    "financni_sprava": "https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/obecne-informace",
    "financni_sprava_qa": "https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/dotazy-a-odpovedi/2026/aktualni-dotazy-a-odpovedi-k-dani-z",
    "cssz": "https://www.cssz.cz/documents/20143/2872693/TZ__P%C5%99ehled%20nejd%C5%AFle%C5%BEit%C4%9Bj%C5%A1%C3%ADch%20%C3%BAdaj%C5%AF%20pro%20soci%C3%A1ln%C3%AD%20zabezpe%C4%8Den%C3%AD%20v%20roce%202026.pdf/3c0800f6-15d0-a4df-8a9e-35b93969b355",
    "vzp": "https://www.vzp.cz/platci/informace/zamestnavatel/vymerovaci-zaklad-a-vypocet-pojistneho",
}

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_tags = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.hidden_tags.append(tag)
    def handle_endtag(self, tag):
        if tag in self.hidden_tags:
            # Remove the most recent matching tag; tolerate malformed page HTML.
            self.hidden_tags.reverse()
            try:
                self.hidden_tags.remove(tag)
            except ValueError:
                pass
            self.hidden_tags.reverse()
    def handle_data(self, data):
        if not self.hidden_tags:
            value = re.sub(r"\s+", " ", data).strip()
            if value:
                self.parts.append(value)

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def fetch_text(url):
    req = Request(url, headers={"User-Agent": "ReverzniMzdovaKalkulacka/2.1 (official-parameter-audit)"})
    with urlopen(req, timeout=25) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    if raw[:4] == b"%PDF":
        proc = subprocess.run(["pdftotext", "-", "-"], input=raw, capture_output=True, check=True)
        text = re.sub(r"\s+", " ", proc.stdout.decode("utf-8", errors="replace")).strip()
    else:
        parser = VisibleText()
        parser.feed(raw.decode(charset, errors="replace"))
        text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    if len(text) < 200:
        raise RuntimeError("Zdroj vrátil nečekaně málo čitelného textu")
    return text

def matches(text, pattern):
    return re.search(pattern, text, re.IGNORECASE) is not None

def main():
    checked_at = now_iso()
    year = datetime.now(timezone.utc).year
    index = INDEX_PATH.read_text(encoding="utf-8")
    texts, errors, fingerprints = {}, [], {}
    try:
        old_snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        old_snapshot = {"sources": {}}

    for key, url in SOURCES.items():
        try:
            text = fetch_text(url)
            texts[key] = text
            fingerprints[key] = {
                "url": url,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "checked_at": checked_at,
            }
            print(f"OK {key}")
        except Exception as exc:
            errors.append({"source": key, "message": str(exc)})
            fingerprints[key] = old_snapshot.get("sources", {}).get(
                key, {"url": url, "sha256": None, "checked_at": None}
            )
            print(f"ERROR {key}: {exc}")

    checks = []
    def check(label, source, pattern):
        source_ok = source in texts and matches(texts[source], pattern)
        checks.append({"parameter": label, "source": source, "matched": source_ok})
        if not source_ok:
            print(f"REVIEW REQUIRED: official evidence missing for {label}")

    # Source evidence: these patterns must match actual visible official-page text.
    check("employee social insurance 7.1%", "cssz",
          r"employee.{0,80}7[,.]1\s*%|zaměstnan.{0,100}7[,.]1\s*%|7[,.]1\s*%.{0,100}zaměstnan")
    check("employee health insurance rate 4.5% (one third of 13.5%)", "vzp",
          r"13[,.]5\s*%.{0,160}(jednu třetinu|one third)|13[,.]5\s*%")
    check("taxpayer credit 30,840 CZK/year", "financni_sprava",
          r"30\s*840\s*Kč.{0,100}základní sleva na poplatníka|základní sleva na poplatníka.{0,100}30\s*840\s*Kč")
    check("taxpayer credit 2,570 CZK/month", "financni_sprava",
          r"2\s*570\s*Kč.{0,100}měsíčně|měsíčně.{0,100}2\s*570\s*Kč")
    check("child credit 1,267 CZK/month", "financni_sprava",
          r"1\s*267\s*Kč")
    check("child credit 1,860 CZK/month", "financni_sprava",
          r"1\s*860\s*Kč")
    check("child credit 2,320 CZK/month", "financni_sprava",
          r"2\s*320\s*Kč")
    check("minimum wage / health minimum base 22,400 CZK", "vzp",
          r"22\s*400\s*Kč")
    check("health minimum premium 3,024 CZK", "vzp",
          r"3\s*024\s*Kč")
    check("15%/23% tax threshold 146,901 CZK/month", "financni_sprava",
          r"146\s*901\s*Kč")
    check("tax base rounds upward to hundreds above 100 CZK", "financni_sprava",
          r"do 100\s*Kč.{0,100}celé koruny nahoru.{0,180}celé stokoruny nahoru")
    check("minimum child bonus 50 CZK", "financni_sprava_qa",
          r"alespoň 50\s*Kč|alespoň ve výši 50\s*Kč")
    check("child bonus income threshold 11,200 CZK", "financni_sprava_qa",
          r"11\s*200\s*Kč")

    # Guard against claiming verification if the actual calculator code has drifted.
    code_checks = [
        ("social rate implementation", r"Math\.ceil\(gross\s*\*\s*71\s*/\s*1000\)"),
        ("health rate implementation", r"Math\.ceil\(Math\.ceil\(gross\s*\*\s*135\s*/\s*1000\)\s*/\s*3\)"),
        ("monthly 23% threshold implementation", r"const\s+threshold\s*=\s*146901\s*;"),
        ("taxpayer credit implementation", r"options\.credit\s*\?\s*2570\s*:\s*0"),
        ("invalidity credits implementation", r"options\.invalidity\s*\|\|\s*0"),
        ("ZTP/P credit implementation", r"options\.ztpp\s*\?\s*1345\s*:\s*0"),
        ("child bonus threshold implementation", r"gross\s*>=\s*11200"),
        ("minimum child bonus implementation", r"potentialBonus\s*>=\s*50"),
        ("child credit values implementation", r"i===1\?1267:i===2\?1860:2320"),
        ("ZTP/P child doubling implementation", r"total\s*\+=\s*base\s*\+\s*\(i>n-z\s*\?\s*base\s*:\s*0\)"),
    ]
    for label, pattern in code_checks:
        ok = matches(index, pattern)
        checks.append({"parameter": "code: " + label, "source": "index.html", "matched": ok})
        if not ok:
            print(f"REVIEW REQUIRED: calculator code does not match audited rule: {label}")

    failed = [item["parameter"] for item in checks if not item["matched"]]
    if errors:
        state = "unknown"
        message = "Nepodařilo se načíst všechny oficiální zdroje; aktuálnost nelze potvrdit."
    elif failed:
        state = "review"
        message = "Některé parametry nebo části výpočtu nebylo možné potvrdit. Kalkulačka nebyla automaticky změněna; je nutná kontrola."
    else:
        state = "verified"
        message = "Všechny kontrolované hodnoty i sledované části implementace odpovídají pravidlům nalezeným na oficiálních zdrojích."

    STATUS_PATH.write_text(json.dumps({
        "status": state, "checked_at": checked_at, "parameter_year": year,
        "check_type": "official_source_and_calculator_code_audit",
        "message": message, "changed_sources": [], "errors": errors,
        "checks": checks, "failed_parameters": failed,
        "review_required": state != "verified",
        "automatic_parameter_updates": False,
        "automatic_update_policy": "Legal constants are never rewritten from loosely matched web text; source drift fails closed to manual review."
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SNAPSHOT_PATH.write_text(json.dumps({
        "checked_at": checked_at, "sources": fingerprints
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Result: {state}; failed={len(failed)}; errors={len(errors)}")

if __name__ == "__main__":
    main()
