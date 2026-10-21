# Záchytný bod projektu – Reverzní mzdová kalkulačka

Datum záchytného bodu: 2026-10-21

## Projekt a nasazení
- Název: Reverzní mzdová kalkulačka
- GitHub repozitář: https://github.com/davhab-dev/reverzni-mzdova-kalkulacka
- Web na GitHub Pages: https://davhab-dev.github.io/reverzni-mzdova-kalkulacka/
- Hlavní stránka: index.html
- Autor v kalkulačce: David Habán

## Aktuální funkce
- Přepínače směru výpočtu: „ČISTÁ → HRUBÁ“ a „HRUBÁ → ČISTÁ“.
- Vstup měsíční mzdy.
- Základní sleva na poplatníka.
- Volby daňového zvýhodnění na děti, invalidity a ZTP/P.
- Rozpis odvodů a daně.
- Modrý vzhled a responzivní rozvržení.
- Stav aktuálnosti parametrů načítaný ze status.json.
- Zobrazen text o další automatické kontrole „každé pondělí ráno“ a odkaz „Spustit kontrolu nyní“, který otevře GitHub Actions; sám přímo nespouští workflow.

## Kontrola zdrojů
- Workflow: .github/workflows/check-sources.yml
- Skript: scripts/check_sources.py
- Stav: status.json
- Otisky zdrojů: source_snapshot.json
- Kontrola je plánována týdně v pondělí v 06:17 UTC (08:17 během českého letního času, 07:17 v zimě).
- Poslední doložený běh GitHub Actions skončil úspěšně.
- Důležité omezení: kontrola změn obsahu webových stránek není sama o sobě ověřením správnosti mzdových parametrů. Automatizace nesmí označit sazby za ověřené, dokud nebyly skutečně porovnány s platnými oficiálními pravidly.
- V kalkulačce může být stav „Aktuálnost mzdových parametrů nebyla ověřena“; to je vhodnější než nepodložené tvrzení o aktuálnosti.

## Poslední provedené úpravy
- Popisky směrů výpočtu změněny na velká písmena.
- Přidána informace o týdenní kontrole a odkaz na stránku workflow.
- Vytvořen soubor CHECKPOINT.md v repozitáři při předchozím záchytném bodu.

## Doporučené další kroky (priorita)
1. **Audit výpočtového algoritmu pro rok 2026**: ověřit výpočty a zaokrouhlování proti aktuálním oficiálním pravidlům, zvláště 23% daňovou hranici, sociální a zdravotní pojistné, slevy a daňové zvýhodnění na děti včetně pořadí dítěte a případného ZTP/P.
2. Vytvořit testovací příklady (včetně hraničních hodnot) a porovnat výsledky s důvěryhodným oficiálním výpočtem.
3. Zlepšit automatickou kontrolu tak, aby hlídala konkrétní parametry a platnost předpisů, ne jen otisky obsahu stránek.
4. Přidat praktickou funkci porovnání dvou mezd.
5. Přidat tisk / export výsledku.
6. Zvážit volbu roku výpočtu až po vyřešení správného modelu parametrů pro jednotlivé roky.

## Designová doporučení
- Zachovat jednoduchý modrý design a přehledné rozhraní.
- Před přidáváním funkcí dát přednost přesnosti výpočtů a důvěryhodnosti.
- Veřejné rozhraní nemá zobrazovat technické detaily monitoringu ani interní zdroje; pouze stručný, srozumitelný stav aktuálnosti.

## Jak navázat
Uživatel může napsat: „Vraťme se k záchytnému bodu Reverzní mzdové kalkulačky.“ První doporučený úkol po návratu je audit výpočtů pro rok 2026.
