"""Static checks over site/: titles, descriptions, headings, schema, links, answer blocks."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser
SITE = Path(__file__).resolve().parent.parent / "site"
probs, titles, descs = [], {}, {}
files = sorted(SITE.rglob("*.html"))
urls = {"/" + str(f.relative_to(SITE)).replace("index.html", "") for f in files}
static = {"/" + str(f.relative_to(SITE)) for f in SITE.rglob("*") if f.is_file()}
for f in files:
    h = f.read_text()
    u = "/" + str(f.relative_to(SITE)).replace("index.html", "")
    t = re.search(r"<title>(.*?)</title>", h).group(1)
    d = re.search(r'<meta name="description" content="(.*?)">', h).group(1)
    titles.setdefault(t, []).append(u); descs.setdefault(d, []).append(u)
    TRUST = {"/404.html", "/about/", "/disclosures/", "/privacy/", "/terms/"}
    if u not in TRUST:
        if not 25 <= len(t) <= 70: probs.append(f"{u}: title length {len(t)}")
        if not 70 <= len(d) <= 170: probs.append(f"{u}: description length {len(d)}")
    if u != "/404.html":
        if 'id="answer"' not in h: probs.append(f"{u}: no #answer block")
    hs = [int(x) for x in re.findall(r"<h([1-6])[\s>]", h)]
    if hs.count(1) != 1: probs.append(f"{u}: {hs.count(1)} h1")
    for a, b in zip(hs, hs[1:]):
        if b > a + 1: probs.append(f"{u}: heading skip h{a}->h{b}")
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: json.loads(blob)
        except Exception as ex: probs.append(f"{u}: bad JSON-LD {ex}")
    for href in re.findall(r'href="(/[^"#?]*)', h):
        if href not in urls and href not in static and href.rstrip("/") + "/" not in urls:
            probs.append(f"{u}: broken link {href}")
    ids = re.findall(r'\sid="([^"]+)"', h)
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: probs.append(f"{u}: duplicate ids {dup}")
for k, v in list(titles.items()) + list(descs.items()):
    if len(v) > 1: probs.append(f"duplicate title/description on {v}")
sm = (SITE / "sitemap.xml").read_text()
for u in urls:
    if u not in ("/404.html",) and f"<loc>" in sm and u not in sm: probs.append(f"not in sitemap: {u}")
print(f"{len(files)} html files checked")
print("\n".join(probs) or "validate: PASS")
sys.exit(1 if probs else 0)
