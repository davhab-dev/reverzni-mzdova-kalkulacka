# Záchytný bod projektu – Reverzní mzdová kalkulačka

Datum: 2026-10-21

## Funkční stav
- Repozitář: https://github.com/davhab-dev/reverzni-mzdova-kalkulacka
- Web: https://davhab-dev.github.io/reverzni-mzdova-kalkulacka/
- Hlavní stránka: `index.html`
- Stav ověření pro kalkulačku: `status.json`
- Otisky sledovaných oficiálních stránek: `source_snapshot.json`
- Týdenní workflow: `.github/workflows/check-sources.yml`
- Skript kontroly: `scripts/check_sources.py`

## Automatická kontrola
- GitHub Actions workflow „Kontrola oficiálních zdrojů“ již byl ručně spuštěn a doběhl úspěšně.
- Plán: každé pondělí v 06:17 UTC (08:17 v českém letním čase, 07:17 v českém zimním čase).
- Kontrola porovnává obsah vybraných stránek Finanční správy, ČSSZ a VZP.
- Změna obsahu stránky je pouze signál k ručnímu posouzení; sama o sobě nedokazuje změnu zákonné sazby.
- Mzdové parametry nebyly automaticky právně ověřeny a nesmějí být označeny jako aktuální jen na základě technického běhu workflow.

## Právě provedená změna
- Do kalkulačky se doplnil text „Další automatická kontrola: každé pondělí ráno“.
- Přidán odkaz „Spustit kontrolu nyní“, který otevře stránku GitHub Actions. Ruční spuštění vyžaduje přihlášení a kliknutí na „Run workflow“; tlačítko v kalkulačce nespouští workflow přímo.

## Další doporučené kroky
1. Počkejte na dokončení publikování GitHub Pages a ověřte nový text a odkaz na webu.
2. Ověřte aktuálnost výpočtových parametrů pro rok 2026 proti oficiálním předpisům a opravte případné nesrovnalosti.
3. Vylepšete kontrolní skript tak, aby ověřoval konkrétní právní hodnoty, pokud je lze spolehlivě strojově získat, a aby stav „aktuální“ mohl nastat pouze po potvrzené kontrole.
4. Případně později přidejte bezpečné zprostředkování přímého spuštění workflow; žádný GitHub token nesmí být uložen v HTML.

