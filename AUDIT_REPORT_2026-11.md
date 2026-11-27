# Audit kalkulačky – 27. 11. 2026

## Zjištění

### Opraveno v této větvi
- Omezena vstupní částka na 100 000 000 Kč; extrémní konečné hodnoty už nemohou přivést zpětný výpočet do nekonečné smyčky.
- Zpětný výpočet odmítá neplatný nebo nepodporovaný cíl.
- Kontrola zdrojů nepovolí stav „verified“ po změně kalendářního roku, dokud nebude sada parametrů explicitně aktualizována.
- Stavový panel odmítá nekonzistentní stav „verified“ s chybami nebo neúspěšnými kontrolami a považuje budoucí čas kontroly za neplatný.
- Přidány automatické regresní testy pro výpočty, daňové zvýhodnění na děti, hranici vyšší sazby, zpětný výpočet a bezpečnostní limity.
- Regresní testy se spouštějí při změně kalkulačky nebo kontrolního skriptu.

### Zjištěná omezení, která vyžadují další rozšíření
- Kalkulačka je orientační model standardního zaměstnání. Nezohledňuje automaticky všechny výjimky, poměrné měsíce, souběžné příjmy ani individuální situace.
- Zdravotní pojištění: výpočet neřeší doplatek do minimálního vyměřovacího základu ani výjimky z minima. U nízké mzdy může být čistá mzda nadhodnocena.
- Sociální pojištění: kalkulačka nepracuje s ročním maximálním vyměřovacím základem a dosavadním součtem příjmů v daném roce. U vysokých příjmů proto nemusí odpovídat skutečné mzdové účtárně.
- ZTP/P u dětí se zadává jako počet a předpokládá se, že se týká dětí s nejvyšším pořadím. Pro přesné rodinné situace je potřeba zadávat každé dítě samostatně.
- Kontrola oficiálních zdrojů používá textové vzory. Je to bezpečnější než automatické přepisování sazeb, ale nenahrazuje ruční právní kontrolu při změně předpisů.
- Produkční kopie na hlavním webu a stavový soubor v tomto repozitáři jsou samostatné. Tato větev nezajišťuje automatickou synchronizaci obou repozitářů; pro úplné nasazení je třeba promítnout opravy do `davhab-dev.github.io/mzda/` a vyřešit synchronizaci `status.json`.

## Ověření

Regresní testy jsou součástí GitHub Actions. Jejich aktuální výsledek bude uveden v kontrolách pull requestu. Po sloučení je nutné ověřit i nasazenou kopii na `davhab.com/mzda/` v prohlížeči.
