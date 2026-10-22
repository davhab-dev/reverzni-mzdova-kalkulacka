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
