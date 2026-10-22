# UX audit – provedené změny a ověření

Datum: 2026-10-22

## Checkpoint
Původní stav index.html byl zaznamenán před změnami v souboru UX_AUDIT_CHECKPOINT.md. Výchozí blob SHA: 0da1299cd37b15c467bc715731f44ee38e1f1daa.

## Provedené změny
- Odstraněna neověřená formulace slibující automatickou kontrolu každé pondělí.
- Stavový panel nyní zobrazuje datum technické kontroly ze status.json, pokud je dostupné, a výslovně odlišuje kontrolu obsahu zdrojů od ověření správnosti sazeb.
- Popisek výsledku používá běžné psaní a méně výraznou tloušťku písma; přepínače režimu mají čitelnější velikost textu.
- Vstup odmítá záporné a nečíselné hodnoty s vysvětlující zprávou.
- Rozpis odděluje daň před slevami, osobní slevy, zvýhodnění na děti a daňový bonus.
- Přidána volba počtu dětí s průkazem ZTP/P a zohlednění zdvojnásobeného zvýhodnění.
- Doplněno vysvětlení předpokladů výpočtu.

## Kontrola oficiálních parametrů pro rok 2026
- Finanční správa potvrzuje měsíční slevu na poplatníka 2 570 Kč, hranici zálohové daně 146 901 Kč, sazby 15 % a 23 %, dětské zvýhodnění 1 267 / 1 860 / 2 320 Kč měsíčně a hranici příjmu pro měsíční daňový bonus 11 200 Kč.
- ČSSZ uvádí sazbu sociálního pojištění zaměstnance 7,1 %.
- VZP uvádí minimální mzdu 22 400 Kč jako minimální vyměřovací základ zdravotního pojištění pro rok 2026.

Zdroje:
- Finanční správa: https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/obecne-informace
- Finanční správa – dotazy a odpovědi 2026: https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/zamestnanci-zamestnavatele/dotazy-a-odpovedi/2026/aktualni-dotazy-a-odpovedi-k-dani-z
- ČSSZ: https://www-in.cssz.cz/web/lang/sazby-pojistneho?lang=en
- VZP: https://www.vzp.cz/platci/informace/zamestnavatel/vymerovaci-zaklad-a-vypocet-pojistneho

## Zbývající omezení
- Nejde o kompletní mzdovou účtárenskou certifikaci. Výpočet stále předpokládá standardní pracovní poměr a neřeší všechny výjimky, poměrné měsíce, souběhy příjmů ani individuální výjimky z minimálního vyměřovacího základu.
- Počet dětí se ZTP/P v UI zadává jako počet; implementace zvýhodnění přiřazuje tyto děti k nejvyšším pořadím v zadaném počtu dětí. Pokud je důležité přesné pořadí konkrétního dítěte, je vhodnější budoucí UI s individuálním nastavením každého dítěte.
- Změny byly ověřeny kontrolou obsahu souboru na GitHubu; automatické browserové testy ani kompletní testování čtečkou obrazovky nebyly v tomto běhu provedeny.


## Navazující checkpoint a úpravy – 2026-10-22

- Před pokračováním byl vytvořen checkpoint `UX_CALC_CHECKPOINT_2026-10-22.md`, který zaznamenává výchozí blob SHA aktuálního `index.html`.
- Opraven rozpis daně: „Daň po osobních slevách“, skutečně uplatněné zvýhodnění na děti a daň po zvýhodnění nyní vycházejí z oddělených mezivýsledků.
- Vysvětlení u ZTP/P na děti nyní výslovně uvádí, že kalkulačka předpokládá ZTP/P u dětí s nejvyšším pořadím. Jde o zjednodušení, nikoliv univerzální model každé rodinné situace.
- Zpřesněno upozornění, že výběr slev sám o sobě nepotvrzuje nárok a že kalkulačka nepokrývá všechny individuální výjimky.
- Změna kódu: commit `8817bd83f3c64c263d6268b4b385fa4c4bc73e83`.
- Omezení: nebyl proveden automatizovaný test v prohlížeči ani nezávislá mzdová certifikace. Stav `status.json` zůstává `unknown`; výpočet se proto nesmí označovat za oficiálně ověřený. Před tvrzením o správnosti pro rok 2026 je nutné ověřit sazby, zaokrouhlování, limity a všechny mezní případy podle platných oficiálních pravidel.


## Tisk výsledku – 2026-10-22

- Přidáno tlačítko „Vytisknout výsledek“, které otevře standardní tiskový dialog prohlížeče.
- Tisková sestava používá bílé pozadí a úsporné rozvržení; skryje vstupní formulář, přepínače režimu, stavový panel a ovládací prvky.
- Výsledek a podrobný rozpis zůstávají ve výstupu viditelné i tehdy, když je rozpis na obrazovce zavřený.
- Změna v index.html: commit 5bf8f32b42a00bddaa7655c1db5684dafc9e7b98.
- Ověření: kontrola přítomnosti CSS pro tisk, tlačítka a obsluhy window.print(). Skutečný tisk z prohlížeče nebyl v tomto běhu proveden.


## Automatická pravidelná kontrola – 2026-10-22

- Workflow kontroly oficiálních zdrojů je naplánován denně (GitHub Actions), místo dosavadního týdenního spuštění.
- Stavový panel při načtení stránky porovnává čas poslední kontroly se sedmidenním limitem a kontroluje, zda stav odpovídá aktuálnímu kalendářnímu roku.
- Při zastaralém záznamu, chybějícím datu nebo nesouladu roku zobrazí upozornění „Kontrola oficiálních zdrojů je zastaralá“.
- Skript nyní ukládá aktuální kalendářní rok dynamicky místo pevné hodnoty 2026.
- Kontrola nadále detekuje změny obsahu oficiálních stránek; automaticky neověřuje právní správnost jednotlivých hodnot a sama nemění výpočetní parametry kalkulačky.
- Omezení: GitHub Actions může plánované spuštění zpozdit; pro tuto variantu se při návštěvě stránky zobrazuje poslední uložený stav, nová kontrola se nespouští synchronně při otevření webu.
