"""Eurocup komandų sekimas nacionaliniuose čempionatuose (Flashscore).
Paleidimas: python scraper.py
Selektoriai ir URL yra viršuje - jei Flashscore pakeis puslapio struktūrą, taisyk čia.
"""
import json, re, time, hashlib, pathlib
from collections import Counter
from playwright.sync_api import sync_playwright
from build_site import build

BASE = "https://www.flashscore.com"
EUROCUP = BASE + "/basketball/europe/eurocup/"
OUT = pathlib.Path("site")
LOGOS = OUT / "logos"
DELAY = 2.5  # sekundės tarp užklausų (gerbiame svetainę)

# Jei automatinis lygos nustatymas suklysta, įrašyk ranka: "Komandos pavadinimas": "/basketball/lithuania/lkl/"
LEAGUE_OVERRIDES = {}

JS_MATCHES = """()=>{const out=[];let cur=null;
document.querySelectorAll('.event__title, .event__match').forEach(el=>{
 if(el.classList.contains('event__title')){
  const a=el.querySelector('a');
  cur={name:(el.querySelector('.event__title--name')||{}).innerText||'',
       country:(el.querySelector('.event__title--type')||{}).innerText||'',
       href:a?a.getAttribute('href'):''};
 } else {
  const q=s=>{const e=el.querySelector(s);return e?e.innerText.trim():''};
  out.push({comp:cur,home:q('.event__homeParticipant'),away:q('.event__awayParticipant'),
            hs:q('.event__score--home'),as:q('.event__score--away'),time:q('.event__time')});
 }});
return out;}"""

JS_STANDINGS = """()=>[...document.querySelectorAll('.ui-table__row')].map(r=>{
 const a=r.querySelector('a.tableCellParticipant__name');
 const img=r.querySelector('img');
 return {name:a?a.innerText.trim():'',href:a?a.getAttribute('href'):'',
         rank:(r.querySelector('.tableCellRank')||{}).innerText||'',
         logo:img?img.src:'',
         cells:[...r.querySelectorAll('.table__cell--value')].map(c=>c.innerText.trim())};
}).filter(x=>x.name)"""


def open_page(page, url):
    time.sleep(DELAY)
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    try:
        page.click("#onetrust-accept-btn-handler", timeout=2500)
    except Exception:
        pass
    page.wait_for_timeout(1500)


def save_logo(page, url):
    if not url or url.startswith("data:"):
        return ""
    ext = pathlib.Path(url.split("?")[0]).suffix or ".png"
    name = hashlib.md5(url.encode()).hexdigest()[:12] + ext
    path = LOGOS / name
    if not path.exists():
        try:
            path.write_bytes(page.request.get(url).body())
        except Exception:
            return ""
    return "logos/" + name


def page_logo(page):
    """Puslapio (turnyro) logotipas iš antraštės."""
    for sel in ["img.heading__logo", ".heading img", "img[class*=logo]"]:
        el = page.query_selector(sel)
        if el:
            return el.get_attribute("src") or ""
    return ""


def get_matches(page, url):
    open_page(page, url)
    try:
        page.wait_for_selector(".event__match", timeout=8000)
    except Exception:
        return []
    return page.evaluate(JS_MATCHES)


def team_result(m, team):
    mine_home = m["home"].lower() == team.lower()
    try:
        a, b = (int(m["hs"]), int(m["as"]))
    except ValueError:
        return None
    me, opp = (a, b) if mine_home else (b, a)
    return {"wl": "W" if me > opp else "L", "score": f"{a}:{b}",
            "opponent": m["away"] if mine_home else m["home"],
            "venue": "H" if mine_home else "A"}


def main():
    OUT.mkdir(exist_ok=True)
    LOGOS.mkdir(exist_ok=True)
    league_cache = {}
    data = {"updated": time.strftime("%Y-%m-%d %H:%M"), "eurocup_logo": "", "teams": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(locale="en-US").new_page()

        open_page(page, EUROCUP + "standings/")
        data["eurocup_logo"] = save_logo(page, page_logo(page))
        try:
            page.wait_for_selector(".ui-table__row", timeout=10000)
        except Exception:
            pass
        teams = page.evaluate(JS_STANDINGS)
        print(f"Eurocup komandų rasta: {len(teams)}")

        for t in teams:
            entry = {"name": t["name"], "logo": save_logo(page, t["logo"]),
                     "league": None, "league_logo": "", "rank": None,
                     "record": "", "last5": [], "next": None, "note": ""}
            try:
                url = BASE + t["href"]
                matches = get_matches(page, url + "results/")
                domestic = [m for m in matches if m["comp"] and m["comp"]["country"]
                            and not m["comp"]["country"].upper().startswith("EUROPE")
                            and m["comp"]["href"]]
                if t["name"] in LEAGUE_OVERRIDES:
                    league_href = LEAGUE_OVERRIDES[t["name"]]
                    league_name = league_href.strip("/").split("/")[-1].upper()
                elif domestic:
                    c = Counter((m["comp"]["href"], m["comp"]["name"]) for m in domestic)
                    (league_href, league_name), _ = c.most_common(1)[0]
                else:
                    entry["note"] = "Nacionalinė lyga nerasta"
                    data["teams"].append(entry)
                    continue
                entry["league"] = league_name

                res = [team_result(m, t["name"]) for m in domestic
                       if m["comp"]["href"] == league_href]
                entry["last5"] = [r for r in res if r][:5]

                fx = [m for m in get_matches(page, url + "fixtures/") if m["time"]]
                if fx:
                    m = fx[0]
                    home = m["home"].lower() == t["name"].lower()
                    entry["next"] = {"date": m["time"],
                                     "opponent": m["away"] if home else m["home"]}

                key = league_href
                if key not in league_cache:
                    open_page(page, BASE + league_href.rstrip("/") + "/standings/")
                    logo = save_logo(page, page_logo(page))
                    try:
                        page.wait_for_selector(".ui-table__row", timeout=8000)
                    except Exception:
                        pass
                    league_cache[key] = (page.evaluate(JS_STANDINGS), logo)
                rows, entry["league_logo"] = league_cache[key]
                row = next((r for r in rows if r["href"] == t["href"]), None)
                if row:
                    entry["rank"] = int(re.sub(r"\D", "", row["rank"]) or 0) or None
                    c = row["cells"]
                    # Paprastai: [rungt., laim., pralaim., ...]
                    entry["record"] = f"{c[1]}-{c[2]}" if len(c) > 2 else ""
                else:
                    entry["note"] = "Komanda lygos lentelėje nerasta"
            except Exception as e:
                entry["note"] = f"Klaida: {type(e).__name__}"
            print(entry["name"], "->", entry["league"], entry["rank"], entry["note"])
            data["teams"].append(entry)

        browser.close()

    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    build(str(OUT))
    print("Paruošta: site/index.html")


if __name__ == "__main__":
    main()
