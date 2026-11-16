"""Build the static site from data/sightings.tsv: index.html, one page per post
under posts/, and sightings.json for indexers.

    python tools/build.py
"""
import csv
import html
import json
import re
from collections import OrderedDict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://centuryarcade.org/gridspotting/"

CATEGORIES = {
    "real": "Real grids from real sources",
    "prop": "Real grids turned into props",
    "stock": "Grids from stock-image sources",
    "created": "Grids created for productions",
}

CSS = """
:root { --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6860; --rule:#dedbd2; --accent:#9b2c1f; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161614; --fg:#ecebe6; --muted:#a29f96; --rule:#33322e; --accent:#e0806f; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
  font: 17px/1.55 Georgia, "Times New Roman", serif; }
main, header, footer { max-width: 760px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 32px; border-bottom: 1px solid var(--rule); padding-bottom: 16px; }
header .site { font: 600 14px/1 system-ui, sans-serif; letter-spacing: .08em;
  text-transform: uppercase; color: var(--accent); text-decoration: none; }
h1 { font-size: 30px; line-height: 1.2; margin: 12px 0 4px; }
h2 { font-size: 22px; margin: 36px 0 8px; }
a { color: var(--accent); }
.meta, .note, footer { color: var(--muted); font-size: 15px; }
.kicker { font: 600 12px/1 system-ui, sans-serif; letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); }
figure { margin: 20px 0; }
figure img { width: 100%; height: auto; display: block; border: 1px solid var(--rule); }
.match { border-left: 3px solid var(--accent); padding: 4px 0 4px 14px; margin: 16px 0; }
ul.posts { list-style: none; padding: 0; }
ul.posts li { padding: 16px 0; border-bottom: 1px solid var(--rule); display: flex; gap: 16px; }
ul.posts img { width: 140px; height: 90px; object-fit: cover; flex: none; border: 1px solid var(--rule); }
ul.posts a.t { font-size: 19px; text-decoration: none; }
footer { padding: 32px 16px 48px; }
@media (max-width: 480px) { ul.posts img { width: 96px; height: 64px; } }
"""


def fmt_date(s):
    if not s:
        return ""
    d = date.fromisoformat(s)
    return f"{d:%b}. {d.day}, {d.year}".replace("May.", "May").replace("Jun.", "June").replace("Jul.", "July")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def sighting_id(r):
    if r["publication"]:
        return f"{slug(r['publication'])}-{r['pub_date']}"
    return slug(r["work"])


def page(title, body, depth):
    up = "../" * depth
    e = html.escape
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="stylesheet" href="{up}style.css">
</head><body>
<header><a class="site" href="{up}index.html">Gridspotting</a></header>
<main>{body}</main>
<footer>Grid spottings by Ben Zimmer, from his talk &ldquo;Adventures in Gridspotting,&rdquo;
Crossword Con, New York, Apr. 10, 2026. This is a placeholder put together from the talk
slides; the write-ups are still to come.</footer>
</body></html>
"""


def main():
    rows = list(csv.DictReader(open(ROOT / "data/sightings.tsv", encoding="utf8"), delimiter="\t"))
    posts = OrderedDict()
    for r in rows:
        posts.setdefault(r["post"], []).append(r)

    (ROOT / "posts").mkdir(exist_ok=True)
    (ROOT / "style.css").write_text(CSS.lstrip(), encoding="utf8")
    e = html.escape
    index_items, records = [], []

    for key, rs in posts.items():
        first = rs[0]
        body = [f'<p class="kicker">{e(CATEGORIES[first["category"]])}</p>',
                f"<h1>{e(first['title'])}</h1>"]
        seen = set()
        for r in rs:
            sid = sighting_id(r)
            on = r["work"] + (f", {r['episode']}" if r["episode"] else "")
            aired = f" ({fmt_date(r['air_date'])})" if r["air_date"] else ""
            body.append(f'<section id="{sid}">')
            if len(rs) > 1 and first["category"] == "stock":
                body.append(f"<h2>{e(on)}{e(aired)}</h2>")
            else:
                body.append(f'<p class="meta">Spotted in <i>{e(on)}</i>{e(aired)}</p>')
            if r["publication"]:
                by = f" by {e(r['constructor'])}" if r["constructor"] else ""
                t = f" &ldquo;{e(r['puzzle_title'])}&rdquo;" if r["puzzle_title"] else ""
                body.append(f'<div class="match">Crossword{t}{by}, <b>{e(r["publication"])}</b>, '
                            f'{e(fmt_date(r["pub_date"]))}</div>')
            if r["note"]:
                body.append(f'<p class="note">{e(r["note"])}</p>')
            for img in r["images"].split():
                if img in seen:
                    continue
                seen.add(img)
                body.append(f'<figure><img src="../images/{img}" loading="lazy" alt=""></figure>')
            body.append("</section>")
            records.append({
                "id": sid, "url": f"{BASE}posts/{key}.html#{sid}",
                **{k: r[k] for k in ("category", "work", "episode", "air_date", "publication",
                                     "pub_date", "constructor", "puzzle_title") if r[k]},
            })
        (ROOT / "posts" / f"{key}.html").write_text(page(first["title"], "\n".join(body), 1), encoding="utf8")

        matches = "; ".join(f"{r['publication']}, {fmt_date(r['pub_date'])}" for r in rs if r["publication"])
        thumb = first["images"].split()[0]
        index_items.append(
            f'<li><img src="images/{thumb}" alt="" loading="lazy"><div>'
            f'<a class="t" href="posts/{key}.html">{e(first["title"])}</a>'
            f'<div class="meta">{e(CATEGORIES[first["category"]])}'
            f'{" &middot; " + e(matches) if matches else ""}</div></div></li>')

    intro = ("<h1>Gridspotting</h1><p>Crosswords seen on screen, in movies, TV and ads, "
             "traced back to the puzzles they came from.</p>")
    (ROOT / "index.html").write_text(
        page("Gridspotting", intro + '<ul class="posts">' + "\n".join(index_items) + "</ul>", 0),
        encoding="utf8")
    (ROOT / "sightings.json").write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n", encoding="utf8")
    print(f"{len(posts)} posts, {len(records)} sightings")


if __name__ == "__main__":
    main()
