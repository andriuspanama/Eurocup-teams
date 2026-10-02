# Eurocup nacionaliniuose čempionatuose

Surenka Eurocup komandas iš Flashscore, nustato kiekvienos nacionalinę lygą ir sugeneruoja paprastą `site/index.html`.

## Diegimas
```
pip install -r requirements.txt
playwright install chromium
```

## Paleidimas / duomenų atnaujinimas
```
python scraper.py
```
Po to atidaryk `site/index.html` (veikia be serverio). Atnaujinti galima kada nori pakartotinai paleidus `scraper.py`
(pvz., kartą per kelias valandas; nedaryk dažniau).

## Kaip veikia
- Eurocup komandos imamos iš turnyro lentelės.
- Lyga nustatoma iš komandos rezultatų puslapio (dažniausia ne-Europos varžybų lyga).
- Jei lyga nustatyta blogai, įrašyk ją į `LEAGUE_OVERRIDES` faile `scraper.py`.
- Logotipai atsisiunčiami vieną kartą į `site/logos/`.

## Apribojimai
- Nepatikrinta su gyvais duomenimis: Flashscore keičia HTML klases. Jei kas nors tuščia, pataisyk selektorius `scraper.py` viršuje.
- Laimėjimų–pralaimėjimų stulpelių eilė lentelėje gali skirtis tarp lygų.
- Flashscore neturi viešo API ir gali riboti automatinį rinkimą; naudok tik asmeniniam naudojimui.
- Rūšiavimo pagal šalį nėra: komandos sugrupuotos pagal lygą ir surikiuotos pagal vietą.
