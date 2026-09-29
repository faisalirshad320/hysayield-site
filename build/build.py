"""Static site generator for the HYSA calculator site.

Run: python3 build/build.py   → writes site/

Every number rendered at build time comes from build/reference.py, which is
cross-checked against the shipped JavaScript engine by build/parity.js.
"""
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "build"))
from clusters import (CLUSTERS, LINKS, NAV_LABEL, GLOSSARY, AI_CRAWLERS,
                      ANSWER_AMOUNTS, ANSWER_APYS, ANSWER_HORIZONS)
import reference as R

# The only line to change when the domain is registered.
URL = "https://www.hysayield.com"
NAME = "HYSA Yield"
EMAIL = "hello@" + URL.split("//www.")[-1].split("//")[-1]
TAGLINE = "A high-yield savings calculator that shows its working"
TODAY = dt.date.today().isoformat()
PARITY_N = "6,474"  # overwritten from the live cross-check at build time
YEAR = dt.date.today().year
e = html.escape

CSS = """
figure.chart{margin:1rem 0}figure.chart svg{width:100%;height:auto;display:block}figure.chart figcaption{font-size:.85rem;opacity:.8;margin-top:.3rem}
:root{--ink:#10241c;--muted:#4b6158;--bg:#f4f8f5;--card:#fff;--line:#d7e3dc;--accent:#0f6b4f;
--accent-ink:#fff;--warn:#fff6e0;--warn-ink:#5a4300;--pos:#0f6b4f;--neg:#a63a22;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--ink:#e6efea;--muted:#9fb3aa;
--bg:#0b1613;--card:#132420;--line:#24403a;--accent:#63c79e;--accent-ink:#06120e;--warn:#3a2f10;
--warn-ink:#f6dd9a;--pos:#63c79e;--neg:#ec8b72;color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
a{color:var(--accent)}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.wrap{max-width:780px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:56px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.brand svg{width:22px;height:22px}
nav.main a{color:var(--muted);text-decoration:none;margin-left:14px;font-size:15px;display:inline-block;padding:10px 0}
nav.main a:hover{color:var(--ink)}
main{padding:26px 0 48px}
h1{font-size:clamp(28px,5.5vw,40px);line-height:1.12;letter-spacing:-.02em;margin:0 0 10px}
h2{font-size:23px;letter-spacing:-.01em;margin:38px 0 10px}h3{font-size:18px;margin:24px 0 6px}
.lede{color:var(--muted);font-size:18px;margin:0 0 20px;max-width:36em}
.answer{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
border-radius:0 12px 12px 0;padding:14px 16px;margin:0 0 22px}
.answer p{margin:0}.answer p+p{margin-top:8px}
.tool{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
.fields{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.f{display:flex;flex-direction:column;gap:5px;min-width:0}
.f.wide{grid-column:1/-1}
label{font-weight:600;font-size:15px}
.hint{font-size:13px;color:var(--muted)}
input,select{font:inherit;font-size:17px;padding:11px 12px;border:1px solid var(--line);border-radius:10px;
background:var(--bg);color:var(--ink);min-height:48px;width:100%;min-width:0}
input[type=number]{font-variant-numeric:tabular-nums}
.adv{margin:14px 0 0;border-top:1px solid var(--line);padding-top:10px}
.adv summary{font-weight:600;cursor:pointer;min-height:24px;font-size:15px}
.adv .fields{margin-top:12px}
.out{margin-top:18px;border-top:1px solid var(--line);padding-top:16px}
.big{font-size:clamp(34px,8vw,52px);font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums;margin:0;line-height:1.05}
.biglab{margin:2px 0 0;color:var(--muted);font-size:15px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0 0}
.stat{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.stat b{display:block;font-size:21px;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.stat span{font-size:13px;color:var(--muted)}
.verdict{margin:16px 0 0;padding:12px 14px;border-radius:10px;background:var(--bg);border:1px solid var(--line);font-weight:600}
.chart{margin:16px 0 0}
.chart svg{width:100%;height:auto;display:block}
.acts{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 0}
button{font:inherit;cursor:pointer}
.go{background:var(--accent);color:var(--accent-ink);border:0;border-radius:10px;padding:0 20px;font-weight:700;min-height:48px}
.ghost{background:none;border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:11px 14px;min-height:44px}
.err{color:var(--neg);font-size:14px;margin:8px 0 0;min-height:1.2em}
table{border-collapse:collapse;width:100%;font-size:15px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right}
th{font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
.fact{font-size:20px;line-height:1.4;border-left:4px solid var(--accent);padding:4px 0 4px 14px;margin:16px 0}
details.q{border-bottom:1px solid var(--line);padding:12px 0}
details.q summary{font-weight:600;cursor:pointer;min-height:24px}details.q p{margin:8px 0 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:16px 0}
.cards a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--ink)}
.cards a:hover{border-color:var(--accent)}.cards b{display:block}.cards span{font-size:14px;color:var(--muted)}
dl.gloss dt{font-weight:700;margin:18px 0 4px}dl.gloss dd{margin:0;color:var(--muted)}
.related{margin:44px 0 0;border-top:1px solid var(--line);padding-top:18px}
.related h2{margin:0 0 10px;font-size:18px}
.related ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:8px 16px}
.related li{margin:0}.related a{text-decoration:none}.related a:hover{text-decoration:underline}
.disc{background:var(--warn);color:var(--warn-ink);border-radius:10px;padding:10px 14px;font-size:14px;margin:22px 0 0}
.crumb{font-size:14px;color:var(--muted);margin:0 0 10px}.crumb a{color:var(--muted)}
footer{border-top:1px solid var(--line);padding:24px 0 40px;font-size:14px;color:var(--muted)}
footer a{color:var(--muted)}footer p{margin:6px 0}
code{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:.92em}
.formula{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:14px 0;overflow-x:auto;font-variant-numeric:tabular-nums}
@media (max-width:560px){.fields{grid-template-columns:1fr}[data-tool=ef] .fields,[data-tool=ladder] .fields,[data-tool=simple] .fields{grid-template-columns:1fr 1fr}[data-tool=ef] .hint{display:none}[data-tool=ef] .fields{align-items:end}.related ul{grid-template-columns:1fr}
nav.main a{margin-left:10px}}
"""

LOGO = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M3 20h18"/><path d="M5 20V12"/>'
        '<path d="M10 20V8"/><path d="M15 20V5"/><path d="M20 20V3"/></svg>')

DISCLAIMER = ('<p class="disc"><b>Not financial advice.</b> This is a calculator, not a recommendation. '
              'Savings rates are variable and change without notice, tax treatment depends on your own '
              'situation, and the figures here are projections from the numbers you enter. '
              '<a href="/disclosures/">How this site makes money and what it is not</a>.</p>')


def money(x, dp=0):
    return "$" + f"{x:,.{dp}f}"


def pct(x, dp=2):
    return f"{x * 100:.{dp}f}%"


# --- page shell -------------------------------------------------------------

def answer_block(paras):
    if isinstance(paras, str):
        paras = [paras]
    return '<div class="answer" id="answer">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>"


def related_html(path):
    out = [p for p in LINKS.get(path, []) if p != path]
    if not out:
        return ""
    items = "".join(f'<li><a href="{p}">{e(NAV_LABEL.get(p, p))}</a></li>' for p in out)
    return ('<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related</h2>'
            f"<ul>{items}</ul></nav>")


def page(path, title, desc, body, schema=None, crumbs=None, related=True, scripts=""):
    canon = URL + path
    if related:
        body += related_html(path)
    ld = [
        {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": URL,
         "logo": URL + "/icon-512.png"},
        {"@context": "https://schema.org", "@type": "WebPage", "@id": canon + "#page",
         "url": canon, "name": title, "description": desc, "inLanguage": "en-US",
         "dateModified": TODAY,
         "isPartOf": {"@type": "WebSite", "name": NAME, "url": URL},
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#answer", "h1"]}},
    ]
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                        "item": URL + u} for i, (n, u) in enumerate(crumbs)]})
    ld += schema or []
    crumb_html = ""
    if crumbs:
        crumb_html = '<p class="crumb">' + " / ".join(
            f'<a href="{u}">{e(n)}</a>' if i < len(crumbs) - 1 else e(n)
            for i, (n, u) in enumerate(crumbs)) + "</p>"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0f6b4f">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{URL}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/json" href="/api/summary.json" title="Machine-readable summary">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<style>{CSS.strip()}</style>
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="/">{LOGO}{NAME}</a>
<nav class="main" aria-label="Main"><a href="/">Calculator</a><a href="/calculators/">Tools</a><a href="/learn/">Learn</a><a href="/rates/">Rates</a></nav></div></header>
<main class="wrap">{crumb_html}{body}</main>
<footer><div class="wrap">
<p><a href="/calculators/">Calculators</a> · <a href="/answers/">Worked examples</a> · <a href="/rates/">Rates data</a> · <a href="/glossary/">Glossary</a> · <a href="/methodology/">Methodology</a> · <a href="/llms.txt">llms.txt</a></p>
<p><a href="/about/">About</a> · <a href="/disclosures/">Disclosures</a> · <a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a></p>
<p>Calculations run entirely in your browser. Nothing you type is sent anywhere or stored.</p>
<p>© {YEAR} {NAME}. Not financial advice.</p></div></footer>
{scripts}
</body>
</html>
"""
    out = SITE / "index.html" if path == "/" else SITE / path.strip("/") / "index.html"
    if path.endswith(".html"):
        out = SITE / path.strip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return path


TOOL_JS = '<script src="/assets/calc.js" defer></script><script src="/assets/app.js" defer></script>'


def strip_tags(s):
    """FAQ answers carry links for readers; schema wants plain text."""
    return html.unescape(re.sub("<[^>]+>", "", s)).strip()


def faq_schema(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}


def faq_html(pairs):
    return "".join(f'<details class="q"><summary>{e(q)}</summary><p>{a}</p></details>'
                   for q, a in pairs)


# --- the primary tool -------------------------------------------------------

CALC_FORM = """
<section class="tool" data-tool="main" aria-label="High-yield savings calculator">
<div class="fields">
  <div class="f"><label for="principal">Starting balance</label>
    <input id="principal" type="number" inputmode="decimal" min="0" step="100" value="10000" autocomplete="off"></div>
  <div class="f"><label for="apy">APY</label>
    <input id="apy" type="number" inputmode="decimal" min="0" max="25" step="0.01" value="4.50" autocomplete="off">
    <span class="hint">The rate your bank advertises, as a percentage.</span></div>
  <div class="f"><label for="deposit">Monthly deposit</label>
    <input id="deposit" type="number" inputmode="decimal" min="0" step="25" value="0" autocomplete="off"></div>
  <div class="f"><label for="years">Years</label>
    <input id="years" type="number" inputmode="decimal" min="0.08" max="50" step="0.5" value="5" autocomplete="off"></div>
  <div class="f wide"><label for="compounding">Compounding</label>
    <select id="compounding">
      <option value="daily" selected>Daily (most common)</option>
      <option value="monthly">Monthly</option>
      <option value="quarterly">Quarterly</option>
      <option value="annually">Annually</option>
    </select>
    <span class="hint">Once APY is quoted, frequency barely moves the result — see <a href="/learn/how-hysa-compounding-works/">why</a>.</span></div>
</div>
<details class="adv"><summary>Tax and inflation</summary>
<div class="fields">
  <div class="f"><label for="fed">Federal tax rate</label>
    <input id="fed" type="number" inputmode="decimal" min="0" max="60" step="1" value="0" autocomplete="off">
    <span class="hint">Your marginal bracket, as a percentage.</span></div>
  <div class="f"><label for="state">State tax rate</label>
    <input id="state" type="number" inputmode="decimal" min="0" max="20" step="0.1" value="0" autocomplete="off"></div>
  <div class="f wide"><label for="inflation">Inflation</label>
    <input id="inflation" type="number" inputmode="decimal" min="0" max="20" step="0.1" value="0" autocomplete="off">
    <span class="hint">Set this to see what the balance is worth in today's money.</span></div>
</div></details>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
<div class="acts">
  <button class="ghost" id="csv" type="button">Download schedule (CSV)</button>
  <button class="ghost" id="share" type="button">Copy link to these numbers</button>
</div>
</section>
"""

HOME_FAQ = [
    ("How do I calculate interest on a savings account?",
     "Multiply the balance by the APY for a full year: $10,000 × 4.50% = $450. For part of a year, use "
     "balance × ((1 + APY)<sup>months ÷ 12</sup> − 1). With regular deposits it gets fiddly, which is what the "
     "calculator above is for. For simple (non-compounding) interest, use the "
     '<a href="/calculators/simple-interest/">simple interest calculator</a>.'),
    ("How much does $10,000 earn in a high-yield savings account?",
     'At 4.50% APY, $10,000 left alone earns <b>$450</b> in the first year and grows to '
     '<b>$12,462</b> after five years. Change the APY above to match your bank — and see the '
     '<a href="/answers/10000/">full table for $10,000</a> at other rates.'),
    ("Does compounding daily beat compounding monthly?",
     "Barely. Once a bank quotes APY, the compounding frequency is already inside that number, so "
     "two accounts at the same APY pay the same regardless of how often they compound. Frequency "
     "only matters when a bank quotes a plain interest rate instead."),
    ("Do I pay tax on high-yield savings interest?",
     'In the US, yes — savings interest is taxed as ordinary income in the year it is credited, and '
     'your bank issues a Form 1099-INT once you earn $10 or more. Enter your brackets under "Tax and '
     'inflation" to see the after-tax figure. <a href="/learn/hysa-interest-tax/">More on the tax treatment</a>.'),
    ("Is a CD better than a high-yield savings account?",
     'A CD locks your rate and your money; a HYSA keeps both flexible. Which wins depends on where '
     'rates go and whether you might need the cash early. The '
     '<a href="/calculators/cd-vs-hysa/">CD vs HYSA calculator</a> puts numbers on it, including the '
     'early-withdrawal penalty.'),
    ("Is my money safe?",
     "A high-yield savings account at an FDIC-insured US bank is covered to $250,000 per depositor, "
     "per bank, per ownership category, exactly like a branch account. What is not guaranteed is the "
     "rate: every HYSA rate is variable and can drop at any time."),
    ("Do you store what I type?",
     "No. Every calculation runs in your browser. Nothing is sent to a server, there is no account, "
     "and there are no analytics or advertising cookies on the site today."),
]


def home():
    r1 = R.project(10000, 0.045, "daily", 0, 12)
    r5 = R.project(10000, 0.045, "daily", 0, 60)
    ans = answer_block([
        f"At <b>4.50% APY</b>, <b>$10,000</b> earns <b>{money(r1['interest'], 2)}</b> in the first year and "
        f"reaches <b>{money(r5['finalBalance'])}</b> after five years, before tax.",
        "This calculator also shows the after-tax interest, the value in today's dollars, and a "
        "month-by-month schedule you can download. It is free, needs no sign-up, and runs entirely in your browser.",
    ])
    schema = [
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": "HYSA Calculator", "url": URL + "/", "applicationCategory": "FinanceApplication",
         "operatingSystem": "Any", "browserRequirements": "Requires JavaScript",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "description": "Free high-yield savings calculator with after-tax and inflation-adjusted results."},
        faq_schema([(q, strip_tags(a)) for q, a in HOME_FAQ]),
        {"@context": "https://schema.org", "@type": "HowTo",
         "name": "How to work out what a high-yield savings account will earn",
         "totalTime": "PT1M",
         "step": [
             {"@type": "HowToStep", "position": 1, "name": "Enter your balance and APY",
              "text": "Type your current balance and the APY your bank advertises. Use APY, not the plain interest rate.",
              "url": URL + "/#answer"},
             {"@type": "HowToStep", "position": 2, "name": "Add a monthly deposit and a time horizon",
              "text": "Enter what you add each month and how many years you plan to leave the money.",
              "url": URL + "/#answer"},
             {"@type": "HowToStep", "position": 3, "name": "Add your tax brackets",
              "text": "Open Tax and inflation and enter your federal and state marginal rates to see the after-tax interest.",
              "url": URL + "/learn/hysa-interest-tax/"},
             {"@type": "HowToStep", "position": 4, "name": "Check the schedule",
              "text": "Open the month-by-month table to see exactly when interest is credited, and download it as CSV.",
              "url": URL + "/methodology/"}]},
    ]
    body = f"""
<h1>HYSA Calculator</h1>
<p class="lede">What your high-yield savings actually earns — after tax, after inflation, with the maths shown.</p>
{CALC_FORM}
{ans}
{DISCLAIMER}

<h2>What most savings calculators get wrong</h2>
<p class="fact">A 5% APY must return exactly 5% over a year — whatever the compounding frequency. Several calculators that rank for this search treat APY as a plain interest rate and compound it again, overstating the result.</p>
<p>APY already includes compounding. That is the whole point of the number: it is the figure US banks are required to quote so that accounts can be compared like for like. Feeding an APY into a compound-interest formula as though it were a nominal rate double-counts, and the error grows with the balance and the term.</p>
<p>This calculator derives the periodic rate <em>from</em> the APY, so a 5% APY returns 5.00% in a year on daily, monthly, quarterly or annual compounding. That property is tested on every build, along with {PARITY_N} other checks against an independently written implementation. <a href="/methodology/">See the method and the test results</a>.</p>

<h2>What this one does that the others don't</h2>
<ul>
<li><b>After-tax interest.</b> Savings interest is ordinary income. Enter your brackets and see the number you actually keep.</li>
<li><b>Inflation-adjusted value.</b> 4.5% with 3% inflation is about 1.5% in purchasing power.</li>
<li><b>A real schedule.</b> Month by month, downloadable as CSV, so you can check it rather than trust it.</li>
<li><b>Nothing hidden.</b> No sign-up, no bank lead-capture form, no "see your personalised rate" interstitial. The formula is published.</li>
</ul>

<h2>Questions</h2>
{faq_html(HOME_FAQ)}
"""
    return page("/", "HYSA Calculator: What Your High-Yield Savings Really Earns",
                "Free high-yield savings calculator. See interest, after-tax return and inflation-adjusted value for any APY, with a month-by-month schedule you can download.",
                body, schema, scripts=TOOL_JS)


# --- secondary calculators --------------------------------------------------

def calculators_hub():
    tools = [
        ("/", "HYSA calculator", "Interest, after-tax return and inflation-adjusted value for any balance and APY."),
        ("/calculators/how-much-to-earn/", "How much do I need?", "Work backwards from the monthly income you want to the balance it takes."),
        ("/calculators/cd-vs-hysa/", "CD vs HYSA", "Compare a locked CD rate against a floating savings rate, including the early-withdrawal penalty."),
        ("/calculators/savings-goal/", "Savings goal", "How long a target takes at a given deposit and rate."),
        ("/calculators/withdrawal/", "Withdrawal", "How long a balance lasts while you draw a fixed amount each month."),
        ("/calculators/apy-converter/", "APY and rate converter", "Turn a quoted interest rate into APY and back, at any compounding frequency."),
        ("/calculators/cd-calculator/", "CD calculator", "What a CD pays at maturity, its early-withdrawal penalty and the month it breaks even."),
        ("/calculators/cd-ladder/", "CD ladder", "Split a sum across CD terms and see the blended rate and when each rung matures."),
        ("/calculators/emergency-fund/", "Emergency fund", "How much to keep for emergencies, and how long it takes to get there."),
        ("/calculators/simple-interest/", "Simple interest", "I = P × r × t, side by side with compound interest on the same numbers."),
    ]
    cards = "".join(f'<a href="{u}"><b>{e(t)}</b><span>{e(d)}</span></a>' for u, t, d in tools)
    ans = answer_block(
        "Ten savings calculators, all free, all running in your browser with nothing stored. They share "
        "one engine, so the same balance and APY give the same answer wherever you enter it.")
    body = f"""
<h1>Savings calculators</h1>
<p class="lede">One engine, ten questions. Pick the one that matches what you are actually trying to work out.</p>
{ans}
<div class="cards">{cards}</div>
<h2>Why they agree with each other</h2>
<p>Every tool on this site calls the same published function. A balance projected here gives the same figure as the same balance worked backwards from a monthly income target, because it is the same code doing both. The engine is cross-checked on each build against a separately written implementation — {PARITY_N} comparisons, and none disagrees by more than a trillionth. <a href="/methodology/">The method, and the tests</a>.</p>
{DISCLAIMER}
"""
    return page("/calculators/", "Savings Calculators: HYSA, CD, APY and Goal Tools",
                "Ten free savings calculators — HYSA interest, CD, CD ladder, CD vs HYSA, emergency fund, simple interest, savings goal, withdrawal and APY conversion.",
                body, crumbs=[("Home", "/"), ("Calculators", "/calculators/")])


def reverse_calc():
    rows = []
    for target in (100, 250, 500, 1000, 2500, 5000):
        cells = "".join(f"<td class='n'>{money(R.balance_for_monthly_income(target, a))}</td>"
                        for a in (0.03, 0.04, 0.045, 0.05))
        rows.append(f"<tr><td>{money(target)}</td>{cells}</tr>")
    need = R.balance_for_monthly_income(1000, 0.045)
    ans = answer_block([
        f"To earn <b>$1,000 a month</b> in interest at <b>4.50% APY</b>, you need about "
        f"<b>{money(need)}</b> in the account. That is before tax — savings interest is ordinary "
        f"income, so at a combined 29% rate you would need roughly "
        f"{money(R.balance_for_monthly_income(1000, 0.045, 0.24, 0.05, after_tax=True))} to keep $1,000.",
        "Change the target, the rate and your tax brackets below. The arithmetic is simple and the "
        "answer is uncomfortable: interest income needs a large balance, which is exactly why it is "
        "worth knowing the number before planning around it.",
    ])
    body = f"""
<h1>How much do I need to earn $1,000 a month?</h1>
<p class="lede">Working backwards from the income you want to the balance it takes.</p>
<section class="tool" data-tool="reverse" aria-label="Reverse savings calculator">
<div class="fields">
  <div class="f"><label for="target">Monthly interest wanted</label>
    <input id="target" type="number" inputmode="decimal" min="1" step="50" value="1000" autocomplete="off"></div>
  <div class="f"><label for="apy">APY</label>
    <input id="apy" type="number" inputmode="decimal" min="0.01" max="25" step="0.01" value="4.50" autocomplete="off"></div>
  <div class="f"><label for="fed">Federal tax rate</label>
    <input id="fed" type="number" inputmode="decimal" min="0" max="60" step="1" value="0" autocomplete="off"></div>
  <div class="f"><label for="state">State tax rate</label>
    <input id="state" type="number" inputmode="decimal" min="0" max="20" step="0.1" value="0" autocomplete="off"></div>
</div>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
</section>
{ans}
{DISCLAIMER}

<h2>The balance behind each income, before tax</h2>
<div class="tw"><table><thead><tr><th>Monthly interest</th><th class="n">at 3.00%</th><th class="n">at 4.00%</th><th class="n">at 4.50%</th><th class="n">at 5.00%</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p>Read down a column and the relationship is linear: twice the income needs twice the balance. Read across a row and the rate matters less than people expect — going from 4.00% to 5.00% cuts the balance needed by a fifth, not by half.</p>

<h2>Three things this table hides</h2>
<ul>
<li><b>Tax.</b> The figures above are gross. Interest is taxed as ordinary income in the year it is paid, so the balance needed to <em>keep</em> a given amount is higher — enter your brackets in the calculator to see by how much.</li>
<li><b>The rate is variable.</b> Every HYSA rate can be cut without notice. A balance sized for $1,000 a month at 4.50% produces $667 a month if the rate falls to 3.00%.</li>
<li><b>Inflation.</b> Interest that exactly matches inflation leaves you level, not ahead.</li>
</ul>
<p>For what a balance you already have will earn, use the <a href="/">main calculator</a> or the <a href="/answers/">worked examples</a>.</p>
"""
    qs = [("How much do I need in savings to make $1,000 a month?",
           strip_tags(f"About {money(need)} at 4.50% APY, before tax. At a combined 29% tax rate you would need "
                      f"roughly {money(R.balance_for_monthly_income(1000, 0.045, 0.24, 0.05, after_tax=True))} to keep $1,000 a month.")),
          ("How much interest does $100,000 earn per month?",
           strip_tags(f"At 4.50% APY, about {money(100000 * ((1.045) ** (1/12) - 1), 2)} a month before tax.")),
          ("Is living off savings interest realistic?",
           "It takes a large balance and the rate is not guaranteed. Savings interest is best treated as a "
           "supplement or a cushion rather than a salary, because the rate can be cut at any time and "
           "inflation erodes what it buys.")]
    return page("/calculators/how-much-to-earn/",
                "How Much Do I Need to Earn $1,000 a Month in Interest?",
                f"To earn $1,000 a month at 4.50% APY you need about {money(need)}. Work out the balance for any income target, rate and tax bracket.",
                body, [faq_schema(qs)],
                crumbs=[("Home", "/"), ("Calculators", "/calculators/"), ("How much do I need", "/calculators/how-much-to-earn/")],
                scripts=TOOL_JS)


def cd_calc():
    c = R.compare_cd(25000, 0.045, 0.047, 24, penalty_months=6)
    ans = answer_block([
        "A CD locks your rate and your money. A high-yield savings account keeps both flexible. Which "
        "wins comes down to two things: whether savings rates fall during the term, and whether you "
        "might need the cash before it ends.",
        f"On $25,000 over 2 years, a 4.70% CD returns <b>{money(c['cdEnd'] - 25000)}</b> against "
        f"<b>{money(c['hysaEnd'] - 25000)}</b> from a savings account holding 4.50% — a difference of "
        f"{money(abs(c['difference']))}. Break that CD early with a 6-month interest penalty and you give up "
        f"{money(c['cdEarlyPenalty'])}, which is more than the advantage. Put your own numbers in below.",
    ])
    body = f"""
<h1>CD vs high-yield savings</h1>
<p class="lede">The trade is rate certainty against access. Here is what each side is actually worth.</p>
<section class="tool" data-tool="cd" aria-label="CD versus HYSA calculator">
<div class="fields">
  <div class="f"><label for="principal">Amount</label>
    <input id="principal" type="number" inputmode="decimal" min="0" step="1000" value="25000" autocomplete="off"></div>
  <div class="f"><label for="months">Term (months)</label>
    <input id="months" type="number" inputmode="numeric" min="1" max="120" step="1" value="24" autocomplete="off"></div>
  <div class="f"><label for="cdapy">CD APY</label>
    <input id="cdapy" type="number" inputmode="decimal" min="0" max="25" step="0.01" value="4.70" autocomplete="off"></div>
  <div class="f"><label for="apy">Savings APY now</label>
    <input id="apy" type="number" inputmode="decimal" min="0" max="25" step="0.01" value="4.50" autocomplete="off"></div>
  <div class="f"><label for="drift">Savings rate change per year</label>
    <input id="drift" type="number" inputmode="decimal" min="-10" max="10" step="0.05" value="-0.50" autocomplete="off">
    <span class="hint">Negative if you expect rates to fall.</span></div>
  <div class="f"><label for="penalty">Early-withdrawal penalty</label>
    <input id="penalty" type="number" inputmode="decimal" min="0" max="24" step="1" value="6" autocomplete="off">
    <span class="hint">Months of interest, as your bank quotes it.</span></div>
</div>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
</section>
{ans}
{DISCLAIMER}

<h2>What the break-even rate tells you</h2>
<p>The calculator gives a <b>break-even APY</b>: the flat savings rate that would have matched the CD over the same term. If you think savings rates will average above it, the savings account wins; below it, the CD does. It turns a guess about the future into one number you can actually have an opinion about.</p>

<h2>When each one makes sense</h2>
<h3>A CD is the better fit when</h3>
<ul>
<li>You are confident you will not need the money before the term ends.</li>
<li>Rates look more likely to fall than rise, and you want to lock today's.</li>
<li>The money has a date attached — a deposit, a tax bill, a planned purchase — that matches the term.</li>
</ul>
<h3>A high-yield savings account is the better fit when</h3>
<ul>
<li>It is your emergency fund. Access is the whole point, and a penalty defeats it.</li>
<li>The CD premium is small. A 0.20% gap on $25,000 over two years is about $100 — thin payment for locking up the money.</li>
<li>You would be tempted to break the CD. The penalty can exceed the interest earned so far, leaving you with less than you deposited.</li>
</ul>

<h2>A note on CD ladders</h2>
<p>Splitting the money across CDs maturing at different dates gives you part of the rate lock and part of the access. It is a reasonable middle path, and it is also more admin than most people sustain. If you would not actually roll each rung on time, the simpler account usually wins in practice.</p>
"""
    qs = [("Is a CD better than a high-yield savings account?",
           "It depends on whether savings rates fall during the term and whether you might need the money "
           "early. A CD locks the rate; a HYSA keeps access. The calculator gives a break-even savings rate "
           "so you can judge which side you are on."),
          ("What happens if I break a CD early?",
           "You pay an early-withdrawal penalty, usually quoted as a number of months of interest — commonly "
           "3, 6 or 12. On a short-held CD the penalty can be larger than the interest earned, so you can "
           "get back less than you put in."),
          ("Do CDs pay more than savings accounts?",
           "Often slightly, but not always, and the gap is usually small. When savings rates are expected to "
           "fall, CD rates tend to sit above them; when rates are expected to rise, the opposite.")]
    return page("/calculators/cd-vs-hysa/", "CD vs HYSA Calculator: Which Actually Pays More?",
                "Compare a fixed CD rate against a floating high-yield savings rate, including the early-withdrawal penalty, and get the break-even savings rate.",
                body, [faq_schema(qs)],
                crumbs=[("Home", "/"), ("Calculators", "/calculators/"), ("CD vs HYSA", "/calculators/cd-vs-hysa/")],
                scripts=TOOL_JS)


def goal_calc():
    ans = answer_block([
        "Put in a target, what you have now, what you can add each month and the rate: this returns the "
        "date you get there, and how much of it came from interest rather than from you.",
        "For most goals under five years, deposits do nearly all the work. On a $20,000 goal from $5,000 "
        "at $400 a month and 4.50% APY, it takes 34 months and interest contributes about 8% of the total. That is not an "
        "argument against a good rate — it is an argument against waiting for one before starting.",
    ])
    body = f"""
<h1>Savings goal calculator</h1>
<p class="lede">How long a target takes, and how much of it the interest actually does.</p>
<section class="tool" data-tool="goal" aria-label="Savings goal calculator">
<div class="fields">
  <div class="f"><label for="goal">Goal</label>
    <input id="goal" type="number" inputmode="decimal" min="1" step="1000" value="20000" autocomplete="off"></div>
  <div class="f"><label for="principal">Starting balance</label>
    <input id="principal" type="number" inputmode="decimal" min="0" step="500" value="5000" autocomplete="off"></div>
  <div class="f"><label for="deposit">Monthly deposit</label>
    <input id="deposit" type="number" inputmode="decimal" min="0" step="50" value="400" autocomplete="off"></div>
  <div class="f"><label for="apy">APY</label>
    <input id="apy" type="number" inputmode="decimal" min="0" max="25" step="0.01" value="4.50" autocomplete="off"></div>
</div>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
</section>
{ans}
{DISCLAIMER}
<h2>What moves the date</h2>
<ul>
<li><b>The monthly deposit,</b> by a wide margin, on any horizon under about a decade.</li>
<li><b>Starting sooner.</b> A month of deposits is worth more than a small rate improvement on a small balance.</li>
<li><b>The rate,</b> which matters more the larger the balance and the longer the term — and which you do not control.</li>
</ul>
<p>If the answer comes back as "never", the deposit is zero and the rate alone cannot reach the goal.</p>
"""
    return page("/calculators/savings-goal/", "Savings Goal Calculator: How Long Will It Take?",
                "Work out when you will hit a savings target from your balance, monthly deposit and APY — and how much of it comes from interest.",
                body, crumbs=[("Home", "/"), ("Calculators", "/calculators/"), ("Savings goal", "/calculators/savings-goal/")],
                scripts=TOOL_JS)


def withdrawal_calc():
    ans = answer_block([
        "How long a balance lasts while you take a fixed amount out each month, with interest still "
        "accruing on what is left.",
        "There is a threshold worth knowing: if the monthly withdrawal is smaller than the interest the "
        "balance earns, it never runs out. At 4.50% APY that crossover is about $367 a month per "
        "$100,000. Above it, the balance drains — slowly at first, then faster.",
    ])
    body = f"""
<h1>Savings withdrawal calculator</h1>
<p class="lede">How long the money lasts, and the point at which it stops running out at all.</p>
<section class="tool" data-tool="withdraw" aria-label="Savings withdrawal calculator">
<div class="fields">
  <div class="f"><label for="principal">Starting balance</label>
    <input id="principal" type="number" inputmode="decimal" min="0" step="1000" value="100000" autocomplete="off"></div>
  <div class="f"><label for="withdrawal">Monthly withdrawal</label>
    <input id="withdrawal" type="number" inputmode="decimal" min="1" step="50" value="1000" autocomplete="off"></div>
  <div class="f"><label for="apy">APY</label>
    <input id="apy" type="number" inputmode="decimal" min="0" max="25" step="0.01" value="4.50" autocomplete="off"></div>
  <div class="f"><label for="compounding">Compounding</label>
    <select id="compounding"><option value="daily" selected>Daily</option><option value="monthly">Monthly</option>
    <option value="quarterly">Quarterly</option><option value="annually">Annually</option></select></div>
</div>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
</section>
{ans}
{DISCLAIMER}
<h2>What this does not model</h2>
<ul>
<li><b>Tax on the interest,</b> which is due each year whether or not you withdraw it. Use the <a href="/">main calculator</a> for the after-tax figure.</li>
<li><b>Inflation,</b> which raises what you need to withdraw over time. A fixed $1,000 a month buys less every year.</li>
<li><b>Rate changes.</b> The rate is held flat here; in reality it is variable.</li>
</ul>
<p>Treat the result as an upper bound on how long the money lasts, not a plan.</p>
"""
    return page("/calculators/withdrawal/", "Savings Withdrawal Calculator: How Long Will My Savings Last?",
                "How long a savings balance lasts at a fixed monthly withdrawal, with interest still accruing — and the point at which it never runs out.",
                body, crumbs=[("Home", "/"), ("Calculators", "/calculators/"), ("Withdrawal", "/calculators/withdrawal/")],
                scripts=TOOL_JS)


def apy_converter():
    rows = "".join(
        f"<tr><td>{pct(nom)}</td>" + "".join(
            f"<td class='n'>{pct((1 + nom / n) ** n - 1)}</td>"
            for n in (365, 12, 4, 1)) + "</tr>"
        for nom in (0.02, 0.03, 0.04, 0.0425, 0.045, 0.05, 0.06))
    ans = answer_block([
        "A quoted <b>interest rate</b> and an <b>APY</b> are not the same number. APY includes compounding; "
        "the plain rate does not. A 4.40% rate compounded daily is 4.50% APY.",
        "Convert either way below. This matters when one bank advertises APY and another advertises a rate — "
        "comparing them directly makes the second look better than it is.",
    ])
    body = f"""
<h1>APY and interest rate converter</h1>
<p class="lede">Turn a quoted rate into APY, or an APY back into the rate behind it.</p>
<section class="tool" data-tool="convert" aria-label="APY converter">
<div class="fields">
  <div class="f"><label for="rate">Interest rate (nominal)</label>
    <input id="rate" type="number" inputmode="decimal" min="0" max="50" step="0.01" value="4.40" autocomplete="off"></div>
  <div class="f"><label for="apyin">APY</label>
    <input id="apyin" type="number" inputmode="decimal" min="0" max="50" step="0.01" value="4.50" autocomplete="off"></div>
  <div class="f wide"><label for="compounding">Compounding</label>
    <select id="compounding"><option value="daily" selected>Daily</option><option value="monthly">Monthly</option>
    <option value="quarterly">Quarterly</option><option value="annually">Annually</option></select>
    <span class="hint">Edit either field — the other follows.</span></div>
</div>
<p class="err" id="err" role="status" aria-live="polite"></p>
<div class="out" id="out" aria-live="polite"></div>
</section>
{ans}
{DISCLAIMER}

<h2>Nominal rate to APY, at a glance</h2>
<div class="tw"><table><thead><tr><th>Interest rate</th><th class="n">Daily</th><th class="n">Monthly</th><th class="n">Quarterly</th><th class="n">Annually</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>Two things fall out of this table. Compounding adds very little — the whole daily-versus-annual spread is under a tenth of a percentage point at these rates. And the gap widens as the rate rises, which is why the distinction matters more for credit cards than for savings.</p>
<p>The formula, and why it is written this way, is on <a href="/learn/apy-formula/">the APY formula page</a>.</p>
"""
    qs = [("What is the difference between APY and interest rate?",
           "The interest rate is the headline number before compounding; APY is what you actually earn over a "
           "year once compounding is counted. A 4.40% rate compounded daily is 4.50% APY."),
          ("How do I convert an interest rate to APY?",
           "APY = (1 + rate/n)^n − 1, where n is the number of compounding periods in a year — 365 for daily, "
           "12 for monthly.")]
    return page("/calculators/apy-converter/", "APY & Effective Interest Rate Calculator (Rate to APY)",
                "Convert a quoted interest rate to APY and back at daily, monthly, quarterly or annual compounding, with the formula and a conversion table.",
                body, [faq_schema(qs)],
                crumbs=[("Home", "/"), ("Calculators", "/calculators/"), ("APY converter", "/calculators/apy-converter/")],
                scripts=TOOL_JS)


# --- learn: the informational clusters --------------------------------------

def learn_page(path, title, desc, h1, lede, ans, body_html, qs, crumb):
    body = f"<h1>{h1}</h1>\n<p class=\"lede\">{lede}</p>\n{answer_block(ans)}\n{body_html}\n"
    if qs:
        body += f"<h2>Questions</h2>\n{faq_html(qs)}\n"
    body += DISCLAIMER
    schema = [{"@context": "https://schema.org", "@type": "Article", "headline": h1,
               "dateModified": TODAY, "author": {"@type": "Organization", "name": NAME, "url": URL + "/about/"},
               "publisher": {"@type": "Organization", "name": NAME}}]
    if qs:
        schema.append(faq_schema([(q, strip_tags(a)) for q, a in qs]))
    return page(path, title, desc, body, schema,
                crumbs=[("Home", "/"), ("Learn", "/learn/"), (crumb, path)])


def learn_what_is_apy():
    r = R.project(10000, 0.045, "daily", 0, 12)
    return learn_page(
        "/learn/what-is-apy/", "What Is APY? Annual Percentage Yield Explained",
        "APY is what a deposit actually earns in a year once compounding is counted. What it means, how it differs from an interest rate, and how to use it.",
        "What is APY?",
        "The one number that tells you what a savings account actually pays.",
        ["<b>APY (annual percentage yield)</b> is what a deposit earns in a year once compounding is counted. "
         f"If an account pays 4.50% APY, $10,000 left in it for a year becomes {money(r['finalBalance'], 2)} — "
         "exactly 4.50% more, whatever the compounding schedule.",
         "US banks are required to quote APY on deposit accounts so that savers can compare them directly. "
         "It is the right number to compare between banks; a plain interest rate is not."],
        f"""
<h2>What APY stands for</h2>
<p>Annual percentage yield. <em>Yield</em> is the return; <em>annual</em> means it is expressed per year; <em>percentage</em> means it is a share of the balance. The phrase exists because "interest rate" was ambiguous — it could mean the rate before or after compounding. APY is always after.</p>

<h2>Why APY exists</h2>
<p>Before APY was standardised, two banks could advertise the same rate and pay different amounts, because one compounded daily and the other annually. The US Truth in Savings Act (1991) and its implementing rule, Regulation DD, fixed that by requiring deposit accounts to disclose APY, calculated the same way everywhere. Comparing APYs is therefore comparing like with like.</p>

<h2>APY versus the interest rate</h2>
<p>The interest rate is the headline number before compounding. APY includes it. At 4.40% compounded daily, the APY is 4.50%. The gap is small at savings rates and grows as rates rise, which is why it matters much more on credit cards. Convert either way with the <a href="/calculators/apy-converter/">APY converter</a>, or read <a href="/learn/apy-vs-interest-rate/">APY vs interest rate</a> in full.</p>

<h2>How to use APY</h2>
<ul>
<li><b>Compare accounts on APY alone.</b> Ignore how often they compound — APY already accounts for it.</li>
<li><b>Remember it is variable.</b> A HYSA's APY is today's rate, not a promise. It can be cut the next day.</li>
<li><b>Check the conditions.</b> Some accounts pay the headline APY only above a minimum balance, or only on balances below a cap, or only with a monthly deposit.</li>
<li><b>Use it in the calculator as-is.</b> Enter the APY your bank shows into the <a href="/">HYSA calculator</a>; it converts internally so the answer matches a real statement.</li>
</ul>

<h2>APY vs dividend rate (credit unions)</h2>
<p>Credit unions are owned by their members, so they call the interest they pay a <em>dividend</em>. The <b>dividend rate</b> is the credit-union equivalent of a nominal interest rate: the rate before compounding. The APY — sometimes written APY or "annual percentage yield" on a credit-union rate sheet — includes compounding, exactly as at a bank. A 4.40% dividend rate compounded monthly is a 4.49% APY. Compare credit unions and banks on APY, never dividend rate against APY.</p>

<h2>The mistake to avoid</h2>
<p class="fact">Do not put an APY into a compound-interest formula as though it were a nominal rate.</p>
<p>It double-counts compounding. The error is small on small balances and grows with the term. On $100,000 at 5% for ten years, treating APY as a daily-compounded nominal rate overstates the result by about $2,000. Several online calculators make exactly this mistake.</p>
""",
        [("What does APY mean?", "Annual percentage yield: what a deposit earns in a year including compounding."),
         ("What does APY stand for?", "Annual percentage yield."),
         ("Is a higher APY always better?",
          "For comparable accounts, yes — but check the conditions. A headline APY may apply only above a minimum "
          "balance, below a cap, or with a monthly deposit, and every savings APY is variable."),
         ("What is APY on a savings account?",
          "The percentage your balance grows in a year, including interest on interest. At 4.50% APY, $10,000 becomes $10,450 after 12 months with no deposits or withdrawals."),
         ("What is the difference between APY and dividend rate?",
          "A dividend rate is what credit unions call the rate before compounding; APY is the yield after compounding. The APY is always equal to or higher than the dividend rate."),
         ("Is APY the same as interest rate?",
          "No. The interest rate is before compounding; APY is after. At savings-account rates the two differ by a "
          "few hundredths of a percentage point.")],
        "What is APY")


def learn_apy_formula():
    return learn_page(
        "/learn/apy-formula/", "APY Formula: How Annual Percentage Yield Is Calculated",
        "The APY formula, APY = (1 + r/n)^n − 1, with a worked example, the reverse formula, and why a calculator should work from APY rather than to it.",
        "The APY formula",
        "How APY is calculated, how to reverse it, and a worked example.",
        ["<b>APY = (1 + r/n)<sup>n</sup> − 1</b>, where <em>r</em> is the nominal annual interest rate as a "
         "decimal and <em>n</em> is the number of times interest compounds in a year — 365 for daily, 12 for monthly.",
         "At 4.40% compounded daily: (1 + 0.044/365)<sup>365</sup> − 1 = 0.04498, or <b>4.50% APY</b>."],
        """
<h2>The formula</h2>
<div class="formula">APY = (1 + r ÷ n)<sup>n</sup> − 1</div>
<ul>
<li><b>r</b> — the nominal annual rate, as a decimal (4.40% → 0.044)</li>
<li><b>n</b> — compounding periods per year: 365 daily, 12 monthly, 4 quarterly, 1 annually</li>
</ul>

<h2>Worked example</h2>
<p>A bank quotes 4.40%, compounded daily.</p>
<ol>
<li>Periodic rate: 0.044 ÷ 365 = 0.00012055</li>
<li>Grow for a year: (1.00012055)<sup>365</sup> = 1.04498</li>
<li>Subtract one: 1.04498 − 1 = 0.04498</li>
<li>APY: <b>4.50%</b> (rounded)</li>
</ol>

<h2>Going the other way</h2>
<p>From an APY back to the periodic rate, which is what a calculator actually needs:</p>
<div class="formula">periodic rate = (1 + APY)<sup>1/n</sup> − 1</div>
<p>This is the form this site's <a href="/">calculator</a> uses. Starting from the APY the bank quotes, rather than from a nominal rate, is what guarantees that a 4.50% APY returns exactly 4.50% in a year — the property that defines APY in the first place. <a href="/methodology/">The full method</a>.</p>

<h2>Continuous compounding</h2>
<p>As compounding becomes infinitely frequent, the formula approaches APY = e<sup>r</sup> − 1. At 4.40% that is 4.4982% — two ten-thousandths of a point above daily compounding's 4.4980%. Beyond daily, frequency stops mattering in practice.</p>
""",
        [("What is the APY formula?", "APY = (1 + r/n)^n − 1, where r is the nominal annual rate as a decimal and n is the number of compounding periods per year."),
         ("How do I calculate APY from an interest rate?", "Divide the rate by the compounding periods, add one, raise to the power of the periods, subtract one. At 4.40% daily that gives 4.50% APY.")],
        "APY formula")


def learn_apy_vs_rate():
    rows = "".join(f"<tr><td>{pct(nom)}</td><td class='n'>{pct((1 + nom / 365) ** 365 - 1, 3)}</td>"
                   f"<td class='n'>{((1 + nom / 365) ** 365 - 1 - nom) * 10000:.1f}</td></tr>"
                   for nom in (0.01, 0.03, 0.045, 0.06, 0.10, 0.20))
    return learn_page(
        "/learn/apy-vs-interest-rate/", "APY vs Interest Rate: What's the Difference?",
        "The interest rate is before compounding; APY is after. How far apart they are, why it matters for comparing accounts, and a conversion table.",
        "APY vs interest rate",
        "Same account, two numbers. Here is which one to compare, and why.",
        ["The <b>interest rate</b> is the headline rate before compounding. <b>APY</b> is what you actually earn "
         "in a year once compounding is counted. At 4.40% compounded daily, the APY is 4.50%.",
         "Compare savings accounts on APY. If one bank shows a rate and another an APY, convert first — otherwise "
         "you are comparing different things."],
        f"""
<h2>How far apart they are</h2>
<div class="tw"><table><thead><tr><th>Interest rate</th><th class="n">APY (daily)</th><th class="n">Gap, basis points</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>At savings rates the gap is a few basis points — a basis point is a hundredth of a percentage point. At credit-card rates it is over two percentage points, which is why the distinction matters far more when you borrow.</p>

<h2>Which to use when</h2>
<ul>
<li><b>Comparing savings accounts:</b> APY. It is standardised and already includes compounding.</li>
<li><b>Entering into a calculator:</b> whichever the calculator asks for, and check which that is. This site's asks for APY, because that is what banks show.</li>
<li><b>Comparing loans:</b> APR, which is a different measure again — see <a href="/learn/apr-vs-apy/">APR vs APY</a>.</li>
</ul>
<p>Convert any rate with the <a href="/calculators/apy-converter/">APY converter</a>.</p>
""",
        [("Is APY or interest rate more accurate?", "APY, for what you will actually earn — it includes compounding. The interest rate understates the return slightly."),
         ("Why is APY higher than the interest rate?", "Because APY counts interest earned on interest. The more often interest compounds, the larger the gap, though at savings rates it stays small.")],
        "APY vs interest rate")


def learn_apr_vs_apy():
    return learn_page(
        "/learn/apr-vs-apy/", "APR vs APY: The Difference Explained",
        "APR is the cost of borrowing; APY is the return on saving. Why they are calculated differently and why the same rate gives two different numbers.",
        "APR vs APY",
        "One is what you pay, the other is what you earn — and they are not calculated the same way.",
        ["<b>APR</b> (annual percentage rate) is the yearly cost of borrowing, used for loans and credit cards. "
         "<b>APY</b> (annual percentage yield) is the yearly return on a deposit. APR ignores compounding; APY includes it.",
         "On the same underlying rate, APY is always the higher number. That makes APY flattering on savings and "
         "APR flattering on debt — which is worth remembering when you read either."],
        """
<h2>Side by side</h2>
<div class="tw"><table><thead><tr><th></th><th>APR</th><th>APY</th></tr></thead><tbody>
<tr><td>Used for</td><td>Loans, credit cards, mortgages</td><td>Savings, CDs, money market accounts</td></tr>
<tr><td>Includes compounding</td><td>No</td><td>Yes</td></tr>
<tr><td>Includes fees</td><td>Some, depending on the product</td><td>No</td></tr>
<tr><td>Who it flatters</td><td>The lender — it understates the true cost</td><td>The bank — it shows the highest honest number</td></tr>
<tr><td>US rule</td><td>Truth in Lending Act, Regulation Z</td><td>Truth in Savings Act, Regulation DD</td></tr>
</tbody></table></div>

<h2>Why the same rate gives two numbers</h2>
<p>A credit card at 24% APR compounding daily costs about 27.1% a year in practice — the APY equivalent. The card issuer quotes 24% because the rules for loans say to. A savings account at 4.40% compounding daily pays 4.50% APY, and the bank quotes 4.50% because the rules for deposits say to. Each rule happens to show the consumer-facing side in its better light.</p>

<h2>The practical upshot</h2>
<ul>
<li>Compare savings on <b>APY</b>, loans on <b>APR</b>, and never one against the other.</li>
<li>To see what debt really costs, convert its APR to an effective annual rate using the <a href="/calculators/apy-converter/">converter</a>.</li>
</ul>
""",
        [("What is the difference between APR and APY?", "APR is the cost of borrowing without compounding; APY is the return on saving with compounding. APR is for loans, APY for deposits."),
         ("Is APR or APY higher?", "On the same underlying rate, APY is higher, because it includes compounding and APR does not.")],
        "APR vs APY")


def learn_what_is_hysa():
    return learn_page(
        "/learn/what-is-a-hysa/", "What Is a High-Yield Savings Account? How HYSAs Work",
        "A high-yield savings account is an ordinary FDIC-insured savings account that pays a much higher rate, usually from an online bank. How it works and its limits.",
        "What is a high-yield savings account?",
        "An ordinary savings account at a better rate — and the handful of things that make it different.",
        ["A <b>high-yield savings account (HYSA)</b> is a savings account paying a much higher rate than a typical "
         "branch account — often ten times or more — usually because it is run by an online bank without branch costs. The FDIC national average savings rate is "
         f"{NAT['savings']:.2f}% ({NAT_ASOF}); that average is the \"normal\" a HYSA is high relative to.",
         "It is still a bank deposit: FDIC-insured to $250,000 per depositor, per bank, per ownership category. The "
         "catch is that the rate is variable and can be cut at any time, and transfers out take a business day or two."],
        """
<h2>How it works</h2>
<ol>
<li>You open the account online and link it to your checking account.</li>
<li>You move money in by transfer. Interest accrues on the balance, usually daily, and is credited monthly.</li>
<li>You move money out by transfer back to checking, typically arriving in one to three business days.</li>
</ol>

<h2>Why the rate is higher</h2>
<p>Online banks carry no branch network, so their costs per dollar deposited are lower, and they compete for deposits on rate. Branch banks rely on convenience and existing relationships instead. The account type is the same; the business model is different.</p>

<h2>What a HYSA is good for</h2>
<ul>
<li><b>An emergency fund,</b> where access matters more than squeezing out the last basis point.</li>
<li><b>Short-term goals</b> with no fixed date — a deposit, a car, a trip.</li>
<li><b>Cash waiting to be invested,</b> earning something in the meantime.</li>
</ul>

<h2>What it is not good for</h2>
<ul>
<li><b>Long-term growth.</b> After tax and inflation, a HYSA roughly holds value; it does not grow it much. Set tax and inflation in the <a href="/">calculator</a> to see this for your numbers.</li>
<li><b>Everyday spending.</b> Transfers take days, and some accounts cap withdrawals per month.</li>
<li><b>Locking a rate.</b> For that you need a CD — see <a href="/calculators/cd-vs-hysa/">CD vs HYSA</a>.</li>
</ul>

<h2>Before you open one</h2>
<ul>
<li>Confirm the bank is FDIC-insured, or NCUA-insured for a credit union.</li>
<li>Check for a minimum balance, a balance cap on the headline rate, or monthly fees.</li>
<li>Check how many withdrawals a month are allowed and how long transfers take.</li>
<li>Compare on APY, not on a plain rate — see <a href="/learn/what-is-apy/">what APY means</a>.</li>
</ul>
""",
        [("How does a high-yield savings account work?", "You deposit money by transfer, it earns interest at a variable rate (usually accrued daily and paid monthly), and you withdraw by transfer back to checking, typically within one to three business days."),
         ("Are high-yield savings accounts safe?", "At an FDIC-insured bank, deposits are covered to $250,000 per depositor, per bank, per ownership category. The rate itself is not guaranteed."),
         ("Can you lose money in a high-yield savings account?", "Not the deposit itself at an insured bank, within the limits. After inflation and tax, though, the purchasing power can fall.")],
        "What is a HYSA")


def learn_money_market():
    return learn_page(
        "/learn/hysa-vs-money-market/", "HYSA vs Money Market Account: Which Is Better?",
        "High-yield savings vs money market accounts: rates, access, minimums and insurance compared — and why the difference is access, not yield.",
        "High-yield savings vs money market account",
        "They pay similar rates. The real difference is how you get your money out.",
        ["A <b>money market account</b> and a <b>high-yield savings account</b> usually pay comparable rates and are "
         "both FDIC-insured bank deposits. The difference is access: a money market account typically adds checks "
         "or a debit card, often in exchange for a higher minimum balance.",
         "Do not confuse a money market <em>account</em> (a bank deposit) with a money market <em>fund</em> (an "
         "investment, not FDIC-insured). They share a name and not much else."],
        """
<h2>Side by side</h2>
<div class="tw"><table><thead><tr><th></th><th>High-yield savings</th><th>Money market account</th></tr></thead><tbody>
<tr><td>Rate</td><td>Variable, competitive</td><td>Variable, broadly similar</td></tr>
<tr><td>Access</td><td>Transfer to checking</td><td>Often checks and/or a debit card</td></tr>
<tr><td>Minimum balance</td><td>Often none</td><td>Often higher</td></tr>
<tr><td>Insurance</td><td>FDIC / NCUA</td><td>FDIC / NCUA</td></tr>
<tr><td>Best for</td><td>Parking cash you rarely touch</td><td>Cash you want to spend from occasionally</td></tr>
</tbody></table></div>

<h2>How to choose</h2>
<ul>
<li>Pick the account with the higher <b>APY</b> once conditions are equal — see <a href="/learn/what-is-apy/">what APY means</a>.</li>
<li>If you want to pay a large bill directly from savings, a money market account's checks may justify a slightly lower rate.</li>
<li>If you will never spend from it directly, the extra access is worth nothing and the simpler account wins.</li>
</ul>

<p>How the account itself works — rates, fees, check-writing and limits — is covered in <a href="/learn/how-money-market-accounts-work/">how money market accounts work</a>.</p>

<h2>Money market funds are different</h2>
<p>A money market <em>fund</em> is a mutual fund holding short-term debt, bought through a brokerage. It is not a bank deposit and is not FDIC-insured, although historically it has been very stable. It can pay more or less than a savings account. If a brokerage offers "money market" as a cash option, it is usually the fund.</p>
""",
        [("Is a money market account better than a high-yield savings account?", "Neither is better on yield alone — rates are usually close. A money market account adds checks or a debit card, often with a higher minimum. Choose on access."),
         ("Is a money market account FDIC insured?", "A money market account at a bank is, to the standard limits. A money market fund at a brokerage is not.")],
        "HYSA vs money market")


def learn_compounding():
    rows = "".join(
        f"<tr><td>{c.capitalize()}</td><td class='n'>{money(R.project(100000, 0.05, c, 0, 12)['finalBalance'], 2)}</td></tr>"
        for c in ("daily", "monthly", "quarterly", "annually"))
    return learn_page(
        "/learn/how-hysa-compounding-works/", "How Compound Interest Works in a Savings Account",
        "How compounding works in a high-yield savings account, why daily vs monthly barely matters once you have the APY, and what actually drives growth.",
        "How compounding works in a savings account",
        "Interest on interest — and why the compounding schedule matters far less than people think.",
        ["<b>Compounding</b> means interest is added to the balance and then earns interest itself. Most US "
         "high-yield savings accounts accrue interest daily and credit it monthly.",
         "Once a bank quotes APY, the compounding frequency is already built into it. Two accounts at 5.00% APY pay "
         "exactly the same over a year, whether one compounds daily and the other annually."],
        f"""
<h2>The proof, in dollars</h2>
<p>$100,000 at 5.00% APY for one year, at each compounding frequency:</p>
<div class="tw"><table><thead><tr><th>Compounding</th><th class="n">After 1 year</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Identical — because APY is defined as the result after a year. This is the check this site's engine runs on every build. A calculator that shows different numbers here is treating APY as a plain rate.</p>

<h2>Where frequency does matter</h2>
<p>If a bank quotes a plain <em>interest rate</em> rather than an APY, compounding frequency changes the outcome — daily beats annual, slightly. That is exactly what APY was invented to remove. Convert with the <a href="/calculators/apy-converter/">APY converter</a>.</p>

<h2>What actually drives growth</h2>
<ol>
<li><b>Deposits,</b> on any horizon under about ten years.</li>
<li><b>Time,</b> because compounding's effect grows the longer money stays in.</li>
<li><b>The rate,</b> which you do not control and which can change.</li>
<li><b>Compounding frequency,</b> a distant last once APY is known.</li>
</ol>

<h2>Accrued versus credited</h2>
<p>Interest usually <em>accrues</em> daily — it is calculated each day on that day's balance — but is <em>credited</em> once a month. It only starts earning interest of its own once it is credited. APY accounts for this, which is one more reason to compare on APY and not on the schedule.</p>
""",
        [("Does daily compounding make a big difference?", "Not once you know the APY — two accounts at the same APY pay the same regardless of frequency. It only matters when comparing plain interest rates."),
         ("How often do high-yield savings accounts compound?", "Most US high-yield savings accounts accrue interest daily and credit it monthly. Check your account's disclosure.")],
        "How compounding works")


def learn_tax():
    r = R.project(25000, 0.045, "daily", 0, 12, fed_rate=0.22, state_rate=0.05)
    return learn_page(
        "/learn/hysa-interest-tax/", "Is High-Yield Savings Interest Taxable? How It's Taxed",
        "Yes. US savings interest is taxed as ordinary income in the year it is credited, reported on Form 1099-INT. What that does to your real return.",
        "Is high-yield savings interest taxable?",
        "Yes — and it changes what the account actually earns you.",
        ["<b>Yes.</b> In the US, interest from a high-yield savings account is taxed as <b>ordinary income</b> in the "
         "year it is credited, at your federal marginal rate and usually your state rate too. Your bank issues a "
         "<b>Form 1099-INT</b> once you earn $10 or more in a year; the interest is taxable even below that.",
         f"On $25,000 at 4.50% APY, a year's interest is {money(r['interest'], 2)}. At a 22% federal and 5% state "
         f"rate, {money(r['tax'], 2)} goes in tax, leaving <b>{money(r['afterTaxInterest'], 2)}</b> — an effective "
         f"{pct(r['afterTaxInterest'] / 25000)} return."],
        """
<h2>How it is taxed</h2>
<ul>
<li><b>Ordinary income,</b> not capital gains. It is added to your wages and taxed at your marginal bracket.</li>
<li><b>In the year it is credited,</b> whether or not you withdraw it. Leaving interest in the account does not defer the tax.</li>
<li><b>State tax too,</b> in most states. A few have no income tax.</li>
<li><b>Reported on Form 1099-INT,</b> which banks issue at $10 of interest or more. Below $10 it is still taxable income.</li>
</ul>

<h2>What that does to the return</h2>
<p>Tax turns the headline APY into something smaller. The after-tax yield is roughly APY × (1 − your combined rate). At 4.50% APY:</p>
<div class="tw"><table><thead><tr><th>Combined tax rate</th><th class="n">After-tax yield</th></tr></thead><tbody>
<tr><td>12%</td><td class="n">3.96%</td></tr>
<tr><td>22%</td><td class="n">3.51%</td></tr>
<tr><td>27% (22% + 5% state)</td><td class="n">3.29%</td></tr>
<tr><td>37%</td><td class="n">2.84%</td></tr>
</tbody></table></div>
<p>Take inflation off that as well and the real return can be close to zero. Enter your own brackets and inflation under "Tax and inflation" in the <a href="/">calculator</a> to see it for your numbers.</p>

<h2>Worth knowing</h2>
<ul>
<li><b>Treasury bills and I bonds</b> are exempt from state and local income tax, which can make a slightly lower yield better after tax in high-tax states.</li>
<li><b>Tax-advantaged accounts</b> such as an IRA can hold cash too, deferring or removing the tax, with their own rules on access.</li>
</ul>
<p>This page describes the general US treatment. Your situation may differ; a tax professional can advise on it.</p>
""",
        [("Do you pay taxes on a high-yield savings account?", "Yes. The interest is taxed as ordinary income at your federal and usually state rate, in the year it is credited, whether or not you withdraw it."),
         ("Do I get a 1099 for my savings account?", "Your bank issues Form 1099-INT if you earn $10 or more of interest in the year. Interest below $10 is still taxable."),
         ("Is savings interest taxed as capital gains?", "No. It is ordinary income, taxed at your marginal rate, which is usually higher than the long-term capital-gains rate.")],
        "Tax on interest")


def learn_hub():
    items = [(u, NAV_LABEL[u]) for u in NAV_LABEL if u.startswith("/learn/") and u != "/learn/"]
    blurbs = {
        "/learn/what-is-apy/": "The one number that tells you what a savings account pays.",
        "/learn/apy-formula/": "How APY is calculated, and how to reverse it.",
        "/learn/apy-vs-interest-rate/": "Same account, two numbers — which to compare.",
        "/learn/apr-vs-apy/": "What you pay versus what you earn.",
        "/learn/what-is-a-hysa/": "An ordinary savings account at a better rate, and its limits.",
        "/learn/hysa-vs-money-market/": "Similar rates; the difference is access.",
        "/learn/how-hysa-compounding-works/": "Why the compounding schedule barely matters.",
        "/learn/hysa-interest-tax/": "How savings interest is taxed, and what that costs you.",
        "/learn/how-money-market-accounts-work/": "Rates, fees, checks and limits on a money market account.",
        "/learn/checking-vs-savings/": "One is for spending, one for keeping.",
        "/learn/hysa-pros-and-cons/": "What you gain, what you give up, and the real risks.",
        "/learn/can-you-withdraw-from-a-hysa/": "Yes — plus timing, limits and the Regulation D rule.",
        "/learn/hysa-vs-investing/": "Savings vs a brokerage account, Roth IRA or 401(k).",
        "/learn/how-much-to-keep-in-a-hysa/": "Emergency fund, near-term goals, and the FDIC limit.",
    }
    cards = "".join(f'<a href="{u}"><b>{e(t)}</b><span>{e(blurbs.get(u, ""))}</span></a>' for u, t in items)
    ans = answer_block("Plain-English guides to APY, high-yield savings accounts, compounding and tax — each linked to a "
                       "calculator so you can check the claim with your own numbers.")
    body = f"""
<h1>Learn</h1>
<p class="lede">What the numbers mean before you trust them.</p>
{ans}
<div class="cards">{cards}</div>
<p>Terms used across these guides are defined in the <a href="/glossary/">glossary</a>.</p>
"""
    return page("/learn/", "High-Yield Savings Guides: APY, Compounding and Tax",
                "Guides to APY, high-yield savings accounts, money market accounts, checking vs savings, withdrawals, compounding, tax and HYSA vs investing.",
                body, crumbs=[("Home", "/"), ("Learn", "/learn/")])


# --- worked examples: "how much does $X earn?" ------------------------------

def answer_page(amount):
    path = f"/answers/{amount}/"
    head = []
    for label, months in ANSWER_HORIZONS:
        head.append(f"<th class='n'>{label}</th>")
    rows = []
    for apy in ANSWER_APYS:
        cells = "".join(f"<td class='n'>{money(R.project(amount, apy, 'daily', 0, m)['interest'])}</td>"
                        for _, m in ANSWER_HORIZONS)
        rows.append(f"<tr><td>{pct(apy)}</td>{cells}</tr>")
    one = R.project(amount, 0.045, "daily", 0, 12)
    five = R.project(amount, 0.045, "daily", 0, 60)
    month1 = R.project(amount, 0.045, "daily", 0, 1)
    taxed = R.project(amount, 0.045, "daily", 0, 12, fed_rate=0.22, state_rate=0.05)
    per_month = amount * ((1.045) ** (1 / 12) - 1)
    a = money(amount)
    ans = answer_block([
        f"At <b>4.50% APY</b>, <b>{a}</b> earns about <b>{money(per_month, 2)} a month</b> and "
        f"<b>{money(one['interest'], 2)} in the first year</b>. Left alone for five years it grows to "
        f"<b>{money(five['finalBalance'])}</b>.",
        f"After a 22% federal and 5% state tax rate, the first year's interest drops to "
        f"{money(taxed['afterTaxInterest'], 2)}. The table below covers other rates and horizons; for your exact "
        f"numbers use the <a href=\"/?p={amount}\">calculator</a>.",
    ])
    body = f"""
<h1>How much does {a} earn in a high-yield savings account?</h1>
<p class="lede">Interest on {a} at common APYs, from one month to ten years.</p>
{ans}
<h2>Interest earned on {a}, before tax</h2>
<div class="tw"><table><thead><tr><th>APY</th>{"".join(head)}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p>Daily compounding, no further deposits, no withdrawals. Because the figures use APY, they are the same under monthly compounding — see <a href="/learn/how-hysa-compounding-works/">why</a>.</p>

<h2>Reading the table</h2>
<ul>
<li><b>Across a row,</b> interest grows slightly faster than linearly — that curve is compounding.</li>
<li><b>Down a column,</b> doubling the APY roughly doubles the interest. The rate matters more than the compounding schedule by a wide margin.</li>
<li><b>The 0.50% row</b> is roughly what a standard branch savings account pays. The gap to the rows below it is the case for a high-yield account.</li>
</ul>

<h2>What the table leaves out</h2>
<ul>
<li><b>Tax,</b> charged as ordinary income each year — see <a href="/learn/hysa-interest-tax/">how savings interest is taxed</a>.</li>
<li><b>Rate changes.</b> Every HYSA rate is variable; the five- and ten-year columns assume a flat rate that will not happen in practice.</li>
<li><b>Inflation,</b> which is what separates a nominal return from a real one.</li>
</ul>
{DISCLAIMER}
"""
    others = [x for x in ANSWER_AMOUNTS if x != amount]
    body += ('<nav class="related" aria-label="Other amounts"><h2>Other amounts</h2><ul>' +
             "".join(f'<li><a href="/answers/{x}/">How much does {money(x)} earn?</a></li>' for x in others) +
             "</ul></nav>")
    qs = [(f"How much interest will {a} earn in a year?",
           f"About {money(one['interest'], 2)} at 4.50% APY, before tax."),
          (f"How much does {a} earn per month in a high-yield savings account?",
           f"About {money(per_month, 2)} a month at 4.50% APY, before tax."),
          (f"How much will {a} be worth in 5 years in a HYSA?",
           f"About {money(five['finalBalance'])} at a steady 4.50% APY with no further deposits. Real rates vary.")]
    schema = [faq_schema(qs)]
    return page(path, f"How Much Does {a} Earn in a High-Yield Savings Account?",
                f"At 4.50% APY, {a} earns about {money(per_month, 2)} a month and {money(one['interest'], 0)} a year. Full table of interest at 0.5% to 5% APY, from 1 month to 10 years.",
                body, schema, crumbs=[("Home", "/"), ("Worked examples", "/answers/"), (a, path)], related=False)


def answers_hub():
    cards = "".join(
        f'<a href="/answers/{x}/"><b>{money(x)}</b><span>{money(R.project(x, 0.045, "daily", 0, 12)["interest"])} a year at 4.50% APY</span></a>'
        for x in ANSWER_AMOUNTS)
    ans = answer_block(
        "Worked examples for the balances people most often ask about. At 4.50% APY, each $10,000 earns "
        f"roughly {money(R.project(10000, 0.045, 'daily', 0, 12)['interest'])} a year before tax. Pick an amount "
        "for the full table across rates and time horizons.")
    body = f"""
<h1>How much will my savings earn?</h1>
<p class="lede">Worked examples at common balances, rates and time horizons.</p>
{ans}
<div class="cards">{cards}</div>
<p>For a balance that isn't listed, or to add monthly deposits, tax or inflation, use the <a href="/">calculator</a>.</p>
{DISCLAIMER}
"""
    return page("/answers/", "How Much Will My Savings Earn? Worked Examples",
                "How much $1,000, $5,000, $10,000, $25,000, $50,000, $100,000 and $250,000 earn in a high-yield savings account at common APYs.",
                body, crumbs=[("Home", "/"), ("Worked examples", "/answers/")])


# --- trust pages -------------------------------------------------------------

def glossary():
    def anchor(t):
        return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    dl = "".join(f'<dt id="{anchor(t)}">{e(t)}</dt><dd>{e(d)}</dd>' for t, d in GLOSSARY)
    ans = answer_block(
        "Plain-English definitions of the savings terms used on this site and in bank disclosures: APY, interest "
        "rate, APR, compounding, money market accounts, CDs, early-withdrawal penalties, FDIC insurance, real "
        "return and Form 1099-INT.")
    body = f"""
<h1>Savings glossary</h1>
<p class="lede">The words banks use, defined once and without the marketing.</p>
{ans}
<dl class="gloss">{dl}</dl>
"""
    schema = [{"@context": "https://schema.org", "@type": "DefinedTermSet",
               "name": "Savings and APY glossary", "url": URL + "/glossary/",
               "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d,
                                   "inDefinedTermSet": URL + "/glossary/"} for t, d in GLOSSARY]}]
    return page("/glossary/", "Savings Glossary: APY, APR, CDs and Compounding Defined",
                "APY, interest rate, APR, compounding, money market accounts, CDs, early-withdrawal penalties, FDIC insurance and more, in plain English.",
                body, schema, crumbs=[("Home", "/"), ("Glossary", "/glossary/")])


def methodology(parity_note):
    body = f"""
<h1>How the calculators work</h1>
<p class="lede">Every formula, every assumption, and the tests the engine has to pass before it ships.</p>
{answer_block([
    "All calculations start from the <b>APY</b> your bank quotes and derive the periodic rate from it, so that a "
    "given APY returns exactly that APY over a year at any compounding frequency. Monthly deposits are added at the "
    "end of each month. Tax is applied to interest only. Everything runs in your browser.",
    f"The shipped JavaScript engine is checked on every build against an independently written Python "
    f"implementation: {parity_note}."])}

<h2>The core formula</h2>
<p>From the APY, the rate for each compounding period is:</p>
<div class="formula">r = (1 + APY)<sup>1/n</sup> − 1</div>
<p>where <em>n</em> is 365 for daily, 12 for monthly, 4 for quarterly and 1 for annual compounding. Each month, the balance is compounded by however many whole periods fall inside that month — 30 or 31 for daily compounding, carried forward so a year always contains exactly 365 — and then the month's deposit is added.</p>

<h2>Why start from APY</h2>
<p>US banks must quote APY on deposit accounts under the Truth in Savings Act and Regulation DD. APY is defined as the return over a year <em>including</em> compounding. A calculator that feeds an APY into a compound-interest formula as if it were a nominal rate compounds it a second time and overstates the result. Starting from APY avoids that by construction.</p>

<h2>Assumptions</h2>
<ul>
<li><b>Deposits</b> are made at the end of each month (an ordinary annuity), which matches a standing transfer.</li>
<li><b>The rate is held flat</b> for the whole term, except in the CD comparison, where you can set a yearly drift.</li>
<li><b>Tax</b> = interest × (federal rate + state rate), capped at 95%. It is a simple marginal-rate estimate; it ignores deductions, credits and brackets changing over time.</li>
<li><b>Real value</b> = final balance ÷ (1 + inflation)<sup>years</sup>.</li>
<li><b>CD early-withdrawal penalty</b> = months of penalty × one month's interest on the principal at the CD's APY.</li>
<li><b>Reverse solver:</b> balance = monthly target ÷ ((1 + APY)<sup>1/12</sup> − 1), grossed up by 1 ÷ (1 − tax rate) for after-tax targets.</li>
</ul>

<h2>How it is tested</h2>
<ol>
<li><b>Hand-checked cases.</b> Pure compound interest, a zero-rate annuity, a closed-form annuity, tax on interest only, the reverse solver, inflation, and a CD tie at equal rates.</li>
<li><b>APY invariance.</b> 5.00% APY must return exactly $10,500 on $10,000 over one year at every compounding frequency.</li>
<li><b>Independent cross-check.</b> The shipped JavaScript iterates month by month. A separate Python implementation computes the same outputs with different code. Both run over a grid of 960 input combinations — balances from $0 to $250,000, APYs from 0% to 18.75%, all four compounding frequencies, deposits from $0 to $1,500, and terms from 1 month to 30 years.</li>
<li><b>Consistency.</b> The month-by-month schedule must sum to the total, and the savings-goal solver must return the <em>first</em> month the goal is reached.</li>
</ol>
<p>The engine is published at <a href="/assets/calc.js">/assets/calc.js</a> for anyone to read.</p>

<h2>What the calculators do not do</h2>
<ul>
<li>They do not know current bank rates. Enter the APY your bank shows you.</li>
<li>They do not model rate changes, fees, minimum-balance tiers or promotional rates that expire.</li>
<li>They do not give tax advice. The tax estimate is a marginal-rate approximation.</li>
<li>They do not recommend any bank or product.</li>
</ul>

<h2>Corrections</h2>
<p>If you find a figure that is wrong, email <a href="mailto:{EMAIL}">{EMAIL}</a> with the inputs you used. Confirmed errors are fixed and noted here.</p>
<p>Last updated {TODAY}.</p>
{DISCLAIMER}
"""
    schema = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "How the calculators work",
               "dateModified": TODAY, "author": {"@type": "Organization", "name": NAME}}]
    return page("/methodology/", "Methodology: How the HYSA Calculator Works and Is Tested",
                "The formulas behind the HYSA calculator, every assumption, and the independent cross-check it passes on every build.",
                body, schema, crumbs=[("Home", "/"), ("Methodology", "/methodology/")])


def static_pages():
    page("/about/", f"About {NAME}", f"Who makes {NAME}, how it is funded, and how to reach us.", f"""
<h1>About</h1>
{answer_block(f"<b>{NAME}</b> is a free, independent set of high-yield savings calculators built by <b>Omnia Ventures</b>. It is not a bank, a broker or a financial adviser, carries no ads or affiliate links today, and runs every calculation in your browser.")}
<p>{NAME} is a free set of savings calculators, built and maintained by <b>Omnia Ventures</b>. It is independent: not a bank, not a broker, not affiliated with any financial institution, and not a financial adviser.</p>
<h2>Why it exists</h2>
<p>When we looked at what ranked for "HYSA calculator", the top result was a bank's calculator for a different product entirely, and most of the others were either bank lead-capture pages or generic calculators that treat APY as a plain interest rate and overstate the result. None showed the after-tax number, which for most savers is the one that matters.</p>
<p>So this site does one thing carefully: the arithmetic. The formulas are published, the engine is open to read, and it is checked against an independent implementation every time it is built. <a href="/methodology/">The method and the tests</a>.</p>
<h2>What we are not</h2>
<p>We are not financial advisers and nothing here is advice. The calculators project numbers you enter; they do not know your circumstances, current bank rates, or your tax position. For decisions that matter, speak to a qualified professional.</p>
<h2 id="contact">Contact and corrections</h2>
<p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>. If a figure is wrong, send the inputs you used and we will check, fix and note it.</p>
""", crumbs=[("Home", "/"), ("About", "/about/")])

    page("/disclosures/", "Disclosures", f"How {NAME} is funded, what it is not, and how its figures should be read.", f"""
<h1>Disclosures</h1>
{answer_block(f"Nothing on {NAME} is financial advice. The calculators project the figures you enter; they do not know live bank rates, recommend no products, and are funded by no bank. Savings rates are variable, so real results will differ.")}
<p>Last updated {TODAY}.</p>
<h2>Not financial advice</h2>
<p>{NAME} provides calculators and general educational information. It does not provide financial, investment, tax or legal advice, and it does not know your circumstances. Figures are projections from the inputs you enter and are not guarantees of any return.</p>
<h2>Rates change</h2>
<p>High-yield savings rates are variable and can change at any time without notice. The calculators hold a rate flat unless you say otherwise; real accounts do not.</p>
<h2>How the site is funded</h2>
<p>The site is currently free and carries no advertising and no affiliate links. If that changes, this page will say so first, and paid placements will never affect a calculation.</p>
<h2>No recommendations</h2>
<p>We do not recommend, rank or endorse any bank, account or financial product.</p>
<h2>Tax</h2>
<p>Tax figures are a simple marginal-rate estimate for US federal and state income tax. They ignore deductions, credits and changes in your bracket. Consult a tax professional for your situation.</p>
""", crumbs=[("Home", "/"), ("Disclosures", "/disclosures/")])

    page("/privacy/", "Privacy Policy", f"{NAME} collects nothing about you. Every calculation runs in your browser.", f"""
<h1>Privacy</h1>
{answer_block(f"{NAME} collects nothing you type. Every calculation runs in your browser; no balance, rate or tax figure is sent to a server, there are no accounts, and no analytics or advertising cookies are used.")}
<p>Last updated {TODAY}.</p>
<ul>
<li><b>Nothing you type leaves your device.</b> Every calculation runs in your browser. No balance, rate or tax figure is sent to a server.</li>
<li><b>No accounts.</b> We never ask for your name, email or financial details.</li>
<li><b>Shared links</b> put your inputs into the page address so you can send them to someone. Anyone with that link can see those numbers; nothing is stored on our side.</li>
<li><b>No analytics or advertising cookies</b> are used today. If that changes, this page will be updated first and consent requested where the law requires it.</li>
<li><b>Server logs.</b> Our host keeps standard web server logs (IP address, page requested, time) for security and operations.</li>
</ul>
<p>Questions: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
""", crumbs=[("Home", "/"), ("Privacy", "/privacy/")])

    page("/terms/", "Terms of Use", f"Terms for using {NAME}: the figures are projections, not advice or guarantees.", f"""
<h1>Terms of use</h1>
{answer_block("Results are projections from the figures you enter, not advice or a guarantee of any return. Always confirm rates and terms with your bank.")}
<p>Last updated {TODAY}.</p>
<p>{NAME} provides calculators and general information for personal, educational use. Results are projections based on the figures you enter and the assumptions described on the <a href="/methodology/">methodology page</a>. They are not financial, tax or legal advice and are not a guarantee of any return.</p>
<p>We work to keep the calculations correct and test them on every build, but we make no warranty that the site is error-free, and we are not liable for decisions made using it. Always confirm rates and terms directly with your bank.</p>
""", crumbs=[("Home", "/"), ("Terms", "/terms/")])

    page("/404.html", "Page not found", "This page does not exist.", """
<h1>Page not found</h1><p>Try the <a href="/">HYSA calculator</a> or the <a href="/calculators/">other calculators</a>.</p>""",
         related=False)


# --- machine-readable layer --------------------------------------------------

def robots():
    lines = ["# Everything is open to search and AI crawlers.",
             "User-agent: *", "Allow: /", ""]
    lines.append("# Named AI and answer-engine crawlers, allowed explicitly so there is no ambiguity.")
    for bot in AI_CRAWLERS:
        lines += [f"User-agent: {bot}", "Allow: /", ""]
    lines += [f"Sitemap: {URL}/sitemap.xml",
              f"# Plain-text site summary for language models: {URL}/llms.txt",
              f"# Machine-readable figures: {URL}/api/summary.json", ""]
    (SITE / "robots.txt").write_text("\n".join(lines))


def worked_examples():
    """A fixed set of reference results, identical in llms.txt and the JSON API."""
    out = []
    for amt in (10000, 50000, 100000):
        r1 = R.project(amt, 0.045, "daily", 0, 12)
        r5 = R.project(amt, 0.045, "daily", 0, 60)
        out.append({"balance": amt, "apy": 0.045, "compounding": "daily",
                    "interest_1y": round(r1["interest"], 2),
                    "interest_per_month": round(amt * ((1.045) ** (1 / 12) - 1), 2),
                    "balance_5y": round(r5["finalBalance"], 2)})
    return out


def llms_txt(pages, parity_note):
    ex = worked_examples()
    need = R.balance_for_monthly_income(1000, 0.045)
    body = f"""# {NAME}

> Free high-yield savings (HYSA) calculators. They compute interest, after-tax interest and
> inflation-adjusted value for any balance, APY, monthly deposit and term, plus CD vs HYSA,
> CD, CD ladder, emergency fund, simple interest, savings goal, withdrawal and APY-conversion
> tools, plus a chart of the national savings rate against the fed funds rate. Built by Omnia Ventures. Independent:
> not a bank, not a broker, not a financial adviser. Nothing on the site is financial advice.

## What this site is and is not

- It is a calculator. It does not know individual banks' rates, and it does not recommend banks
  or products. The user enters the APY their bank quotes. It publishes FDIC national-average
  rates as a benchmark (see "National average rates" below and /rates/).
- All calculations run client-side in the browser. No inputs are sent to a server or stored.

## Method (why these numbers can be trusted)

- The periodic rate is derived FROM the APY: r = (1 + APY)^(1/n) - 1. So a given APY returns
  exactly that APY over one year at any compounding frequency. Calculators that feed APY into
  a compound-interest formula as a nominal rate double-count compounding and overstate results.
- Monthly deposits are added at the end of each month (ordinary annuity).
- Tax = interest x (federal + state marginal rate). Real value = balance / (1 + inflation)^years.
- Verification: {parity_note}.

## Reference results (4.50% APY, daily compounding, no deposits, before tax)

{chr(10).join(f"- ${x['balance']:,}: about ${x['interest_per_month']:,.2f} a month; ${x['interest_1y']:,.2f} in the first year; ${x['balance_5y']:,.2f} after 5 years." for x in ex)}
- To earn $1,000 a month in interest at 4.50% APY: about ${need:,.0f}, before tax.

## Key facts

- APY (annual percentage yield) is the return over a year including compounding. It is what
  US banks must quote on deposit accounts under the Truth in Savings Act (Regulation DD).
- APR is the cost of borrowing and excludes compounding; APY is the return on deposits and
  includes it. On the same underlying rate, APY is always the higher number.
- US savings interest is taxed as ordinary income in the year it is credited, reported on
  Form 1099-INT once it reaches $10 in a year.
- High-yield savings accounts at FDIC-insured banks are covered to $250,000 per depositor,
  per bank, per ownership category. Their rates are variable.

## National average rates (FDIC, as of {NAT_ASOF})

- Savings {NAT['savings']:.2f}%; interest checking {NAT['interest_checking']:.2f}%; money market {NAT['money_market']:.2f}%.
- CDs: 3-month {NAT['cd_3m']:.2f}%, 6-month {NAT['cd_6m']:.2f}%, 12-month {NAT['cd_12m']:.2f}%, 24-month {NAT['cd_24m']:.2f}%, 60-month {NAT['cd_60m']:.2f}%.
- From {_mon(PEAK_FROM)} to {_mon(PEAK_TO)} the effective fed funds rate was {PEAK_FF:.2f}% while the national
  savings rate peaked at {PEAK_SAV:.2f}%: about {PASS_THROUGH * 100:.0f}% pass-through. Monthly series (FRED SNDR,
  FEDFUNDS) as CSV: {URL}/data/savings-rate-vs-fed-funds.csv
- Regulation D's six-per-month limit on savings withdrawals was removed by the Federal Reserve on
  April 24, 2020; banks may still impose their own limits.

## Attribution

If you quote these figures, please cite {NAME} ({URL}) and link to the page used.

## Pages

{chr(10).join(f"- [{NAV_LABEL.get(p, p)}]({URL}{p})" for p in pages if p in NAV_LABEL)}
{chr(10).join(f"- [How much does ${a:,} earn in a HYSA]({URL}/answers/{a}/)" for a in ANSWER_AMOUNTS)}
- [Machine-readable summary]({URL}/api/summary.json)
- [Calculation engine source]({URL}/assets/calc.js)
"""
    (SITE / "llms.txt").write_text(body, encoding="utf-8")


def api_summary(parity_note):
    (SITE / "api").mkdir(parents=True, exist_ok=True)
    data = {
        "name": NAME, "url": URL, "updated": TODAY, "publisher": "Omnia Ventures",
        "what_it_is": "Free high-yield savings calculators; all computation is client-side.",
        "what_it_is_not": "Not financial advice; does not know individual bank rates; recommends no products.",
        "method": {
            "periodic_rate": "(1 + APY)^(1/n) - 1",
            "deposits": "end of each month (ordinary annuity)",
            "tax": "interest * (federal_rate + state_rate), capped at 0.95",
            "real_value": "balance / (1 + inflation)^years",
            "apy_invariance": "a given APY returns exactly that APY over 12 months at any compounding frequency",
            "verification": parity_note,
        },
        "reference_results": worked_examples(),
        "balance_for_1000_per_month_at_4_5_apy": round(R.balance_for_monthly_income(1000, 0.045), 2),
        "answer_pages": [f"{URL}/answers/{a}/" for a in ANSWER_AMOUNTS],
        "national_average_rates_percent": {"source": FDIC["source"], "as_of": FDIC["as_of"], **NAT},
        "savings_vs_fed_funds": {"peak_fed_funds": PEAK_FF, "peak_window": [PEAK_FROM, PEAK_TO],
                                 "peak_national_savings": PEAK_SAV, "pass_through": round(PASS_THROUGH, 3),
                                 "csv": f"{URL}/data/savings-rate-vs-fed-funds.csv"},
        "engine_source": f"{URL}/assets/calc.js",
    }
    (SITE / "api" / "summary.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def htaccess():
    host = URL.split("//")[1]
    bare = host.replace("www.", "")
    (SITE / ".htaccess").write_text(f"""# {NAME} — Apache (Cloudways). Nginx serves static files directly, so headers
# here apply only when Apache handles the request.
Options -Indexes
ErrorDocument 404 /404.html
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{{HTTP_HOST}} ^{bare.replace('.', chr(92) + '.')}$ [NC]
RewriteRule ^ https://{host}%{{REQUEST_URI}} [L,R=301]
</IfModule>
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml text/plain
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 10 minutes"
ExpiresByType application/javascript "access plus 7 days"
ExpiresByType application/json "access plus 1 day"
ExpiresByType image/png "access plus 30 days"
ExpiresByType image/svg+xml "access plus 30 days"
</IfModule>
<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "geolocation=(), camera=(), microphone=()"
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
<FilesMatch "^(summary\\.json|calc\\.js|llms\\.txt)$">
Header set Access-Control-Allow-Origin "*"
</FilesMatch>
</IfModule>
""")


def icons():
    (SITE / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0f6b4f"/>'
        '<g fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"><path d="M7 25h18"/><path d="M9 25v-6"/>'
        '<path d="M14 25v-9"/><path d="M19 25v-12"/><path d="M24 25V9"/></g></svg>')
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL missing: skipped PNG icons")
        return

    def bars(size, pad):
        im = Image.new("RGB", (size, size), "#0f6b4f")
        d = ImageDraw.Draw(im)
        w = size - 2 * pad
        base = size - pad
        lw = max(3, size // 14)
        d.line([(pad, base), (size - pad, base)], fill="white", width=lw)
        for i, h in enumerate((0.30, 0.45, 0.60, 0.80)):
            x = pad + w * (0.14 + i * 0.24)
            d.line([(x, base), (x, base - w * h)], fill="white", width=lw)
        return im

    bars(512, 96).save(SITE / "icon-512.png", optimize=True)
    bars(180, 34).save(SITE / "apple-touch-icon.png", optimize=True)

    og = Image.new("RGB", (1200, 630), "#0f6b4f")
    d = ImageDraw.Draw(og)
    try:
        big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 76)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except OSError:
        big = small = ImageFont.load_default()
    d.text((80, 190), "HYSA Calculator", font=big, fill="white")
    d.text((80, 300), "What your savings really earn —", font=small, fill="#cfe9dd")
    d.text((80, 350), "after tax, after inflation, maths shown.", font=small, fill="#cfe9dd")
    for i, h in enumerate((90, 140, 190, 250)):
        x = 900 + i * 60
        d.rectangle([x, 470 - h, x + 36, 470], fill="#63c79e")
    og.save(SITE / "og.png", optimize=True)


def sitemap(paths):
    def prio(p):
        if p == "/":
            return "1.0"
        if p.startswith("/calculators/") or p.startswith("/learn/"):
            return "0.8"
        if p in ("/about/", "/privacy/", "/terms/", "/disclosures/"):
            return "0.3"
        return "0.6"
    urls = "".join(f"<url><loc>{URL}{p}</loc><lastmod>{TODAY}</lastmod><priority>{prio(p)}</priority></url>"
                   for p in paths)
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')


def parity_summary():
    """Run the cross-check and return a one-line result for the method pages."""
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "build/reference.py")], check=True,
                   capture_output=True, cwd=ROOT)
    res = subprocess.run(["node", str(ROOT / "build/parity.js")], capture_output=True, text=True, cwd=ROOT)
    if res.returncode != 0:
        print(res.stdout, res.stderr)
        raise SystemExit("parity FAILED — refusing to build a site on a broken engine")
    worst = re.search(r"worst relative difference: ([0-9.e+-]+)", res.stdout).group(1)
    n = re.search(r"sweep: (\d+) comparisons over (\d+) cases", res.stdout)
    return (f"{int(n.group(1)):,} comparisons over {int(n.group(2)):,} input combinations agree "
            f"to within {float(worst):.0e} relative error, and every property test passes")


# ============================================================================
# Low-fruit expansion (see data/lowfruits.json for the shortlist and SERP notes)
# ============================================================================
import csv as _csv

DATA = ROOT / "data"
FDIC = json.loads((DATA / "fdic_national_rates_2026-09.json").read_text())
NAT = FDIC["rates"]
NAT_ASOF = dt.date.fromisoformat(FDIC["as_of"]).strftime("%B %-d, %Y")
SNDR = [(r["date"], float(r["savings_national_rate"])) for r in _csv.DictReader(open(DATA / "rates_sndr.csv"))]
FEDF = [(r["date"], float(r["effective_fed_funds"])) for r in _csv.DictReader(open(DATA / "rates_fedfunds.csv"))]
FDIC_LINK = '<a href="https://www.fdic.gov/national-rates-and-rate-caps" rel="noopener">FDIC national rates</a>'


def _peak():
    f = dict(FEDF); s = dict(SNDR)
    top = max(f.values())
    window = sorted(d for d, v in f.items() if v == top)
    sav = max(s[d] for d in window if d in s)
    return top, window[0], window[-1], sav, sav / top


PEAK_FF, PEAK_FROM, PEAK_TO, PEAK_SAV, PASS_THROUGH = _peak()


def _mon(d):
    return dt.date.fromisoformat(d).strftime("%B %Y")


NAT_SCRIPT = f"<script>window.HYSA_NAT={json.dumps(NAT, separators=(',', ':'))};</script>"


def tool_page(path, title, desc, h1, lede, tool_html, ans, body_after, qs, crumb, extra_schema=None, scripts=TOOL_JS):
    body = f"<h1>{h1}</h1>\n<p class=\"lede\">{lede}</p>\n{tool_html}\n{answer_block(ans)}\n{DISCLAIMER}\n{body_after}\n"
    schema = list(extra_schema or [])
    if qs:
        body += f"<h2>Questions</h2>\n{faq_html(qs)}\n"
        schema.append(faq_schema([(q, strip_tags(a)) for q, a in qs]))
    return page(path, title, desc, body, schema,
                crumbs=[("Home", "/"), ("Calculators", "/calculators/"), (crumb, path)], scripts=scripts)


def webapp(name, path, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": URL + path,
            "applicationCategory": "FinanceApplication", "operatingSystem": "Any",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "description": desc}


def field(fid, label, value, hint="", step="1", mn="0", mx="", wide=False, mode="decimal"):
    return (f'<div class="f{" wide" if wide else ""}"><label for="{fid}">{label}</label>'
            f'<input id="{fid}" type="number" inputmode="{mode}" min="{mn}"{f" max={chr(34)}{mx}{chr(34)}" if mx else ""} '
            f'step="{step}" value="{value}" autocomplete="off">'
            + (f'<span class="hint">{hint}</span>' if hint else "") + "</div>")


def tool_shell(kind, label, fields_html, adv_html=""):
    adv = f'<details class="adv"><summary>Tax</summary><div class="fields">{adv_html}</div></details>' if adv_html else ""
    return (f'<section class="tool" data-tool="{kind}" aria-label="{label}"><div class="fields">{fields_html}</div>{adv}'
            '<p class="err" id="err" role="status" aria-live="polite"></p><div class="out" id="out" aria-live="polite"></div></section>')


COMP_SELECT = ('<div class="f"><label for="compounding">Compounding</label><select id="compounding">'
               '<option value="daily" selected>Daily</option><option value="monthly">Monthly</option>'
               '<option value="quarterly">Quarterly</option><option value="annually">Annually</option></select></div>')


# --- Tier 1: CD calculator (cluster ~19,350/mo) -----------------------------

def cd_calculator():
    c10 = R.cd(10000, 0.042, 12, 3)
    nat_rows = "".join(
        f"<tr><td>{m} month{'s' if m > 1 else ''}</td><td class='n'>{NAT[f'cd_{m}m']:.2f}%</td>"
        f"<td class='n'>{money(10000 * ((1 + NAT[f'cd_{m}m'] / 100) ** (m / 12) - 1), 2)}</td></tr>"
        for m in (1, 3, 6, 12, 24, 36, 48, 60))
    tool = tool_shell("cdcalc", "CD calculator",
        field("principal", "Deposit", 10000, step="500") +
        field("apy", "CD APY", "4.20", "The APY your bank quotes for this CD.", step="0.01", mx="25") +
        field("months", "Term (months)", 12, step="1", mn="1", mx="120", mode="numeric") +
        COMP_SELECT +
        field("penalty", "Early-withdrawal penalty", 3, "Months of interest, as your bank quotes it.", mx="36", wide=True),
        field("fed", "Federal tax rate", 0, "Marginal bracket, %.", mx="60") + field("state", "State tax rate", 0, step="0.1", mx="20"))
    return tool_page(
        "/calculators/cd-calculator/", "CD Calculator: CD Rates, APY and Early-Withdrawal Penalty",
        "Free CD calculator: see what a certificate of deposit earns at maturity at any APY and term, the early-withdrawal penalty, and the month it breaks even.",
        "CD calculator",
        "What a certificate of deposit pays at maturity — and what it costs to get out early.",
        tool,
        [f"A <b>$10,000</b> CD at <b>4.20% APY</b> for 12 months earns <b>{money(c10['interest'], 2)}</b>, returning "
         f"{money(c10['maturity'], 2)} at maturity. With a common 3-month interest penalty, breaking it before month "
         f"{c10['breakEvenMonth']} returns less than you deposited.",
         f"For comparison, the FDIC national average for a 12-month CD is <b>{NAT['cd_12m']:.2f}%</b> ({NAT_ASOF}). "
         "The calculator shows how your rate compares for whatever term you enter."],
        f"""
<h2>How CD interest is calculated</h2>
<p>A CD's APY already includes compounding, so the value at maturity is simply:</p>
<div class="formula">maturity value = deposit × (1 + APY)<sup>months ÷ 12</sup></div>
<p>For a 6-month CD, that is deposit × (1 + APY)<sup>0.5</sup> — half a year of growth, not half the APY added on. Banks quote APY for this reason; see <a href="/learn/what-is-apy/">what APY means</a>.</p>

<h2>The early-withdrawal penalty, in numbers</h2>
<p>Most US banks charge a penalty of a set number of months of interest if you close a CD before it matures: commonly 3 months on terms under a year, 6 months on 1–2 years, and 12 months or more on longer terms. It is charged on the principal whether or not that much interest has been earned yet — which is why breaking a CD early can return less than you put in.</p>
<p>The <b>break-even month</b> in the calculator is the first month at which interest earned covers the penalty. Before it, you lose principal; after it, you keep some interest.</p>

<h2>National average CD rates by term</h2>
<p>These are the FDIC's deposit-weighted national averages across US banks and credit unions — a benchmark for "normal", not the best available. Online banks routinely pay several times more.</p>
<div class="tw"><table><thead><tr><th>Term</th><th class="n">National APY</th><th class="n">Interest on $10,000</th></tr></thead><tbody>{nat_rows}</tbody></table></div>
<p class="hint">Source: {FDIC_LINK}, as of {NAT_ASOF}. Averages the $10,000 and $100,000 product tiers.</p>
<p>Notice the curve: the national average peaks at 12 months and <em>falls</em> for longer terms. Banks pay less to lock money for five years than for one, because they expect rates to fall. When that happens, a short CD or a <a href="/">high-yield savings account</a> often beats a long CD — the <a href="/calculators/cd-vs-hysa/">CD vs HYSA calculator</a> puts a number on it.</p>
""",
        [("How much does a $10,000 CD make in a year?",
          f"At 4.20% APY, a 12-month $10,000 CD earns {money(c10['interest'], 2)}. At the FDIC national average of "
          f"{NAT['cd_12m']:.2f}%, it earns about {money(10000 * NAT['cd_12m'] / 100, 2)}."),
         ("How do you calculate CD interest?",
          "Multiply the deposit by (1 + APY) raised to the power of the term in years, then subtract the deposit. "
          "For $10,000 at 4.20% APY over 12 months: 10,000 × 1.042 − 10,000 = $420."),
         ("Is 4% a good CD rate?",
          f"Compared with the FDIC national average for a 12-month CD ({NAT['cd_12m']:.2f}% as of {NAT_ASOF}), yes — well above it. "
          "Whether it is good for you depends on how long you can lock the money away and what a high-yield savings account pays."),
         ("What happens if I withdraw from a CD early?",
          "You pay an early-withdrawal penalty, usually quoted as months of interest. If it is larger than the interest "
          "earned so far, you get back less than you deposited. The calculator shows the month it breaks even."),
         ("Is CD interest taxable?",
          "Yes. US CD interest is taxed as ordinary income in the year it is credited, even if you don't withdraw it, and "
          "is reported on Form 1099-INT.")],
        "CD calculator",
        [webapp("CD Calculator", "/calculators/cd-calculator/",
                "Certificate of deposit calculator with early-withdrawal penalty, break-even month and national-average comparison.")],
        scripts=NAT_SCRIPT + TOOL_JS)


# --- Tier 1: emergency fund calculator (cluster ~7,700/mo) ------------------

def emergency_fund_calc():
    ef = R.emergency_fund([1600, 500, 250, 350, 200, 150, 150], 6, 4000, 400, 0.04)
    tool = tool_shell("ef", "Emergency fund calculator",
        field("housing", "Rent or mortgage", 1600, step="50") +
        field("food", "Groceries", 500, step="25") +
        field("utilities", "Utilities and phone", 250, step="25") +
        field("transport", "Transport", 350, step="25") +
        field("insurance", "Insurance and medical", 200, step="25") +
        field("debt", "Minimum debt payments", 150, step="25") +
        field("other", "Other essentials", 150, "Childcare, prescriptions — only what you couldn't cut.", step="25", wide=True) +
        field("cover", "Months of cover", 6, "3 is a floor; see the guide below.", step="1", mn="1", mx="24") +
        field("current", "Saved so far", 4000, step="100") +
        field("contribution", "Monthly contribution", 400, step="25") +
        field("apy", "Savings APY", "4.00", "Where the fund will sit.", step="0.01", mx="25"))
    return tool_page(
        "/calculators/emergency-fund/", "Emergency Fund Calculator: How Much Should You Have?",
        "Free emergency fund calculator: work out 3, 6 or 12 months of essential costs, how far you are from it, when you'll get there, and what it earns in savings.",
        "Emergency fund calculator",
        "How much you need, how far away you are, and when you'll get there.",
        tool,
        ["An emergency fund should cover <b>3 to 6 months of essential expenses</b> — the costs you'd still have to pay if "
         "your income stopped — and more if your income is irregular or you support others. It isn't a percentage of salary; "
         "it's your essential monthly spending times the months of cover you need.",
         f"On essential costs of {money(sum([1600, 500, 250, 350, 200, 150, 150]))}/month, six months is "
         f"<b>{money(ef['target'])}</b>. From {money(4000)} saved and {money(400)} a month at 4% APY, you'd reach it in "
         f"{ef['monthsToTarget']} months — and the finished fund would earn about {money(ef['yearlyInterestAtTarget'])} a year."],
        f"""
<h2>How many months of cover you need</h2>
<div class="tw"><table><thead><tr><th>Months</th><th>Usually right when…</th></tr></thead><tbody>
<tr><td>3</td><td>Two steady incomes, no dependents, skills that are quick to re-hire</td></tr>
<tr><td>6</td><td>One income, or dependents, or a mortgage — the most common recommendation</td></tr>
<tr><td>9–12</td><td>Self-employed, commission-based, seasonal work, a single income supporting a family, or a specialised job that takes longer to replace</td></tr>
<tr><td>12+</td><td>Near retirement, chronic health costs, or a small business owner whose household and business cash overlap</td></tr>
</tbody></table></div>

<h2>What counts as an essential expense</h2>
<p>Only what you would still pay if your income stopped tomorrow: housing, food, utilities, transport to look for work, insurance, minimum debt payments and genuine necessities. Leave out subscriptions, eating out, travel and extra debt payments — you'd cut those first. Using your full spending overstates the target and makes it feel unreachable.</p>

<h2>Where to keep it</h2>
<ul>
<li><b>A high-yield savings account</b> is the standard answer: FDIC-insured, available within a day or two, and earning interest. At the FDIC national average savings rate of {NAT['savings']:.2f}% ({NAT_ASOF}), a {money(ef['target'])} fund earns about {money(ef['target'] * NAT['savings'] / 100)} a year; at 4% it earns {money(ef['yearlyInterestAtTarget'])}.</li>
<li><b>Not a CD,</b> unless it's a small slice in a <a href="/calculators/cd-ladder/">ladder</a> — the early-withdrawal penalty defeats the purpose.</li>
<li><b>Not a brokerage account.</b> Emergencies and market falls tend to arrive together, and you'd be forced to sell low.</li>
<li><b>A HELOC is a backup, not a fund.</b> Banks can freeze or cut home-equity lines in a downturn — exactly when you'd reach for one — and it's borrowing, not savings.</li>
</ul>

<h2>Building it</h2>
<ol>
<li>Aim first for one month of essentials — it covers most car repairs and medical bills.</li>
<li>Automate a transfer on payday into a separate savings account, so it isn't mixed with spending money.</li>
<li>Send windfalls — tax refunds, bonuses — straight to it until you reach the target.</li>
<li>Refill it after you use it before going back to other goals.</li>
</ol>

<h2>Rental property owners</h2>
<p>Keep a separate reserve per property, typically 3–6 months of its costs (mortgage, taxes, insurance, maintenance), plus a capital-expenditure fund for roofs, boilers and appliances. Vacancies and repairs don't wait for your personal fund to recover.</p>
""",
        [("How much should I have in my emergency fund?",
          "Three to six months of essential expenses for most people; nine to twelve if your income is irregular, you're "
          "self-employed, or you're the only earner supporting a family."),
         ("Is $10,000 too much for an emergency fund?",
          "Only if it's more than about six to twelve months of your essential costs. For someone spending $3,000 a month on "
          "essentials, $10,000 is just over three months — reasonable, not excessive."),
         ("Is $50,000 too much for an emergency fund?",
          "It depends on your costs. At $4,000 a month in essentials it's about a year — sensible if your income is irregular, "
          "more than most salaried people need. Money above your target could go to higher-returning goals."),
         ("Where should I keep my emergency fund?",
          "In a separate, FDIC-insured high-yield savings account: safe, reachable in a day or two, and earning interest. Not a "
          "CD (penalty) and not investments (market risk)."),
         ("Can a HELOC be my emergency fund?",
          "It can be a backup, but not the fund itself. Lenders can freeze or reduce home-equity lines during downturns, and "
          "it's debt you'd have to repay with interest.")],
        "Emergency fund",
        [webapp("Emergency Fund Calculator", "/calculators/emergency-fund/",
                "Works out an emergency fund target from essential monthly costs, the gap to it, and the time to reach it at a savings APY.")])


# --- Tier 1: simple interest calculator (24,000/mo) --------------------------

def simple_interest_calc():
    tool = tool_shell("simple", "Simple interest calculator",
        field("principal", "Principal", 10000, step="100") +
        field("rate", "Annual interest rate", 5, "%", step="0.01", mx="100") +
        field("time", "Time", 3, step="0.5") +
        '<div class="f"><label for="unit">Unit</label><select id="unit"><option value="years" selected>Years</option>'
        '<option value="months">Months</option><option value="days">Days</option></select></div>')
    rows = "".join(
        f"<tr><td>{y}</td><td class='n'>{money(R.simple_interest(10000, 0.05, y), 2)}</td>"
        f"<td class='n'>{money(10000 * (1.05 ** y - 1), 2)}</td>"
        f"<td class='n'>{money(10000 * (1.05 ** y - 1) - R.simple_interest(10000, 0.05, y), 2)}</td></tr>"
        for y in (1, 3, 5, 10, 20, 30))
    return tool_page(
        "/calculators/simple-interest/", "Simple Interest Calculator: I = P × r × t",
        "Free simple interest calculator using I = P × r × t, in years, months or days — with the compound-interest figure beside it so you can see the difference.",
        "Simple interest calculator",
        "I = P × r × t, worked out for you — with the compound figure alongside.",
        tool,
        ["<b>Simple interest = principal × rate × time</b> (I = P × r × t). On $1,000 at 5% for 3 years that is "
         "1,000 × 0.05 × 3 = <b>$150</b>. Interest is paid only on the original amount, never on earlier interest.",
         "Savings accounts and CDs pay <em>compound</em> interest instead, which earns interest on interest. The calculator "
         "shows both, so you can see how much compounding adds."],
        f"""
<h2>The formula</h2>
<div class="formula">I = P × r × t &nbsp;&nbsp;&nbsp; A = P + I = P(1 + rt)</div>
<ul>
<li><b>P</b> — principal, the starting amount</li>
<li><b>r</b> — annual rate as a decimal (5% → 0.05)</li>
<li><b>t</b> — time in years (18 months → 1.5; 90 days → 90 ÷ 365)</li>
</ul>

<h2>Simple vs compound, on $10,000 at 5%</h2>
<div class="tw"><table><thead><tr><th>Years</th><th class="n">Simple</th><th class="n">Compound (yearly)</th><th class="n">Compounding adds</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Over one year they're identical. After that the gap widens every year — by year 30, compound interest earns more than double. That growing gap is why the rate on long-term savings matters so much, and why debt that compounds gets expensive.</p>

<h2>Where simple interest is actually used</h2>
<ul>
<li><b>Many auto loans and some personal loans</b> — interest accrues on the outstanding principal only.</li>
<li><b>Treasury bills</b> and some short-term notes, quoted on a simple or discount basis.</li>
<li><b>Per-diem interest</b> on a loan payoff or a late payment.</li>
<li><b>Not savings accounts or CDs,</b> which compound — use the <a href="/">HYSA calculator</a> or <a href="/calculators/cd-calculator/">CD calculator</a> for those.</li>
</ul>
""",
        [("How do you calculate simple interest?",
          "Multiply the principal by the annual rate (as a decimal) by the time in years: I = P × r × t. $1,000 at 5% for 3 years is $150."),
         ("What is 4% interest on $10,000?",
          "$400 a year in simple interest. Compounded yearly for several years it grows faster: $1,698.59 over 4 years versus $1,600 simple."),
         ("What is the difference between simple and compound interest?",
          "Simple interest is paid only on the original principal. Compound interest is also paid on interest already earned, so "
          "it grows faster the longer the money stays in."),
         ("How do you calculate simple interest for months or days?",
          "Convert time to years first: divide months by 12 or days by 365, then apply I = P × r × t.")],
        "Simple interest",
        [webapp("Simple Interest Calculator", "/calculators/simple-interest/",
                "Simple interest calculator (I = P × r × t) with a compound-interest comparison.")])


# --- Tier 3: CD ladder builder ------------------------------------------------

def cd_ladder_calc():
    L = R.ladder(20000, [(12, 0.04), (24, 0.039), (36, 0.038), (48, 0.037), (60, 0.036)])
    tool = tool_shell("ladder", "CD ladder calculator",
        field("total", "Total to invest", 20000, step="1000") +
        field("rungs", "Number of rungs", 5, step="1", mn="2", mx="10", mode="numeric") +
        field("step", "Months between rungs", 12, "12 for a classic 1–5 year ladder; 3 for a short ladder.", step="1", mn="1", mx="24", mode="numeric") +
        field("apy", "APY of the shortest rung", "4.00", step="0.01", mx="25") +
        field("slope", "APY change per rung", "-0.10", "Negative if longer CDs pay less, as they currently do on average.", step="0.05", mn="-2", mx="2", wide=True))
    return tool_page(
        "/calculators/cd-ladder/", "CD Ladder Calculator: Build a CD Ladder",
        "Free CD ladder calculator: split money across CDs that mature in turn, see each rung's interest, the blended APY and how often cash comes free.",
        "CD ladder calculator",
        "Split money across CDs that mature in turn, so some is always about to come free.",
        tool,
        ["A <b>CD ladder</b> splits one sum across several CDs with staggered terms — say 1, 2, 3, 4 and 5 years. One rung "
         "matures each year; you reinvest it at the long end. You get regular access and a blend of short- and long-term rates.",
         f"$20,000 across five rungs from 1 to 5 years, at 4.00% falling 0.10 points per rung, earns "
         f"<b>{money(L['totalInterest'])}</b> on the first cycle at a blended {pct(L['blendedApy'])} APY."],
        f"""
<h2>How a ladder works</h2>
<ol>
<li>Divide the total into equal rungs — five rungs of $4,000 in the example.</li>
<li>Buy CDs of staggered terms: 1, 2, 3, 4 and 5 years.</li>
<li>When the 1-year CD matures, reinvest it in a new 5-year CD. Next year, do the same with the next rung.</li>
<li>After one cycle every rung is a 5-year CD, but one still matures each year.</li>
</ol>

<h2>When a ladder helps — and when it doesn't</h2>
<ul>
<li><b>It helps</b> when long CDs pay clearly more than short ones: you collect the long rate while keeping yearly access.</li>
<li><b>It helps</b> if you're unsure where rates are going — you're never all-in at one moment's rate.</li>
<li><b>It helps less right now.</b> On the FDIC national averages ({NAT_ASOF}) a 12-month CD pays {NAT['cd_12m']:.2f}% and a 60-month CD only {NAT['cd_60m']:.2f}% — longer rungs pay <em>less</em>. With an inverted curve like that, a ladder mostly buys rate certainty, not extra yield.</li>
<li><b>It isn't an emergency fund.</b> Access is scheduled, not on demand — keep your <a href="/calculators/emergency-fund/">emergency fund</a> in savings.</li>
<li><b>It takes admin.</b> If you won't actually roll each rung on time, a single <a href="/">high-yield savings account</a> usually wins in practice.</li>
</ul>
""",
        [("How do you build a CD ladder?",
          "Split your money into equal parts and buy CDs with staggered terms (for example 1 to 5 years). As each one matures, "
          "reinvest it in a CD at the longest term, so one rung comes due every year."),
         ("Is a CD ladder a good idea?",
          "It's a reasonable way to balance access and rate when long CDs pay more than short ones. When longer CDs pay less, as "
          "the national averages currently show, a ladder mainly buys rate certainty rather than extra interest."),
         ("What is a short-term CD ladder?",
          "A ladder with rungs a few months apart — for example 3, 6, 9 and 12 months — giving access every quarter.")],
        "CD ladder",
        [webapp("CD Ladder Calculator", "/calculators/cd-ladder/",
                "Builds a CD ladder and shows each rung's maturity, interest and the blended APY.")])


# --- Tier 2: /rates/ — original, citable data asset --------------------------

def _rates_chart():
    """Static SVG of the national savings rate against the fed funds rate."""
    s = dict(SNDR); f = dict(FEDF)
    dates = sorted(set(s) | set(f))
    W, H, L, R_, T, B = 720, 300, 44, 12, 14, 34
    ymax = 6.0
    x = lambda i: L + (W - L - R_) * i / (len(dates) - 1)
    y = lambda v: T + (H - T - B) * (1 - v / ymax)
    def line(src):
        return " ".join(f"{x(i):.1f},{y(src[d]):.1f}" for i, d in enumerate(dates) if d in src)
    grid = "".join(f'<line x1="{L}" x2="{W - R_}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="g"/>'
                   f'<text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v:.0f}%</text>' for v in range(0, 7))
    years = "".join(f'<text x="{x(i):.1f}" y="{H - 12}" text-anchor="middle">{d[:4]}</text>'
                    for i, d in enumerate(dates) if d.endswith("-01-01"))
    return (f'<figure class="chart"><svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="ct cd">'
            f'<title id="ct">National savings rate vs federal funds rate, {_mon(dates[0])} to {_mon(dates[-1])}</title>'
            f'<desc id="cd">The fed funds rate rose from near zero in 2022 to {PEAK_FF:.2f}% and stayed there from '
            f'{_mon(PEAK_FROM)} to {_mon(PEAK_TO)}. The national average savings rate peaked at only {PEAK_SAV:.2f}%.</desc>'
            '<style>text{font:11px system-ui,sans-serif;fill:currentColor;opacity:.75}.g{stroke:currentColor;opacity:.12}'
            '.ff{fill:none;stroke:#b4531f;stroke-width:2.2}.sv{fill:none;stroke:#1f6f5c;stroke-width:2.8}</style>'
            f'{grid}{years}<polyline class="ff" points="{line(f)}"/><polyline class="sv" points="{line(s)}"/></svg>'
            '<figcaption><span style="color:#b4531f">■</span> Effective federal funds rate &nbsp; '
            '<span style="color:#1f6f5c">■</span> National average savings rate (FDIC)</figcaption></figure>')


def rates_page():
    s = dict(SNDR); f = dict(FEDF)
    last_s, last_f = SNDR[-1], FEDF[-1]
    now_pass = last_s[1] / last_f[1]
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    rows = ["date,savings_national_rate,effective_fed_funds"] + [
        f"{d},{s.get(d, '')},{f.get(d, '')}" for d in sorted(set(s) | set(f))]
    (SITE / "data" / "savings-rate-vs-fed-funds.csv").write_text("\n".join(rows) + "\n")
    snap = [d for d in sorted(s) if d.endswith("-01-01")] + [last_s[0]]
    snap_rows = "".join(f"<tr><td>{_mon(d)}</td><td class='n'>{s[d]:.2f}%</td>"
                        f"<td class='n'>{(f'{f[d]:.2f}%' if d in f else '—')}</td></tr>" for d in snap)
    label = {"savings": "Savings", "interest_checking": "Interest checking", "money_market": "Money market",
             **{f"cd_{m}m": f"{m}-month CD" for m in (1, 3, 6, 12, 24, 36, 48, 60)}}
    nat_rows = "".join(f"<tr><td>{label[k]}</td><td class='n'>{v:.2f}%</td><td class='n'>{money(10000 * v / 100, 2)}</td></tr>"
                       for k, v in NAT.items())
    ans = [f"The <b>national average savings account rate is {NAT['savings']:.2f}% APY</b> (FDIC, {NAT_ASOF}). "
           f"On $10,000 that is {money(100 * NAT['savings'], 2)} a year. Money market accounts average "
           f"{NAT['money_market']:.2f}% and 12-month CDs {NAT['cd_12m']:.2f}%.",
           f"That average barely follows the Fed. From {_mon(PEAK_FROM)} to {_mon(PEAK_TO)} the fed funds rate sat at "
           f"{PEAK_FF:.2f}%, yet the national savings rate peaked at {PEAK_SAV:.2f}% — about {PASS_THROUGH * 100:.0f}% "
           "of the Fed's rate reached the average saver. High-yield accounts are the exception, not the norm."]
    body = f"""<h1>Savings account interest rates: the national average, charted</h1>
<p class="lede">What US banks actually pay on savings, money market accounts and CDs — and how little of the Fed's rate reaches savers.</p>
{answer_block(ans)}
<h2>Savings rate vs the Fed, {_mon(SNDR[0][0])} to {_mon(last_s[0])}</h2>
{_rates_chart()}
<p>The Federal Reserve raised its policy rate from near zero in March 2022 to {PEAK_FF:.2f}% by mid-2023. Banks passed almost none of it to ordinary savings accounts: the national average rose from {SNDR[0][1]:.2f}% to {PEAK_SAV:.2f}%. As of {_mon(last_s[0])} it is {last_s[1]:.2f}% against a fed funds rate of {last_f[1]:.2f}% ({_mon(last_f[0])}) — a pass-through of about {now_pass * 100:.0f}%.</p>
<p class="fact">The gap is the reason high-yield savings accounts exist: an online bank paying close to the Fed's rate is paying roughly ten times the average.</p>
<div class="tw"><table><thead><tr><th>Month</th><th class="n">National savings rate</th><th class="n">Effective fed funds</th></tr></thead><tbody>{snap_rows}</tbody></table></div>
<p><a href="/data/savings-rate-vs-fed-funds.csv" download>Download the full monthly series (CSV)</a> · Sources: FDIC national savings rate via <a href="https://fred.stlouisfed.org/series/SNDR" rel="noopener">FRED SNDR</a>; <a href="https://fred.stlouisfed.org/series/FEDFUNDS" rel="noopener">FRED FEDFUNDS</a>. The FDIC's current methodology begins in April 2021, so the series starts there rather than splicing two methods together.</p>

<h2>Current national average rates by account type</h2>
<div class="tw"><table><thead><tr><th>Account</th><th class="n">National APY</th><th class="n">A year on $10,000</th></tr></thead><tbody>{nat_rows}</tbody></table></div>
<p class="hint">Source: {FDIC_LINK}, as of {NAT_ASOF}. Deposit-weighted across insured banks and credit unions; savings and checking at the $2,500 tier, money market and CDs averaging the $10,000 and $100,000 tiers.</p>

<h2>How to read these numbers</h2>
<ul>
<li><b>They are averages, not offers.</b> They include large branch banks paying close to zero. What you can get is usually much higher; enter it in the <a href="/">HYSA calculator</a>.</li>
<li><b>The CD curve is inverted.</b> 12-month CDs pay more than 5-year CDs, which signals that banks expect rates to fall. See the <a href="/calculators/cd-calculator/">CD calculator</a>.</li>
<li><b>Savings rates are variable.</b> A HYSA rate can be cut the day after the Fed cuts; a CD rate is fixed for the term.</li>
</ul>
<p>This page is regenerated from the source files on each build; the "as of" date above is the date of the data, not of the page.</p>
{DISCLAIMER}
"""
    qs = [("What is the average interest rate on a savings account?",
           f"{NAT['savings']:.2f}% APY, the FDIC national average as of {NAT_ASOF}. High-yield savings accounts at online banks commonly pay several times that."),
          ("What is a good interest rate for a savings account?",
           "Anything well above the national average is good relative to the market. The practical test is whether it beats inflation after tax; the calculator's tax and inflation fields show that."),
          ("Why are savings rates so low when the Fed rate is high?",
           f"Banks set savings rates themselves and most have kept them low: when the fed funds rate was {PEAK_FF:.2f}%, the average savings account paid at most {PEAK_SAV:.2f}%. Online banks compete harder for deposits, which is why their rates track the Fed more closely."),
          ("Will savings rates go down?",
           "Savings rates are variable and tend to follow the Fed's policy rate down when it cuts. No one can promise the timing; a CD locks today's rate if you want certainty.")]
    body += f"<h2>Questions</h2>\n{faq_html(qs)}\n"
    dataset = {"@context": "https://schema.org", "@type": "Dataset",
               "name": "US national average savings rate vs effective federal funds rate (monthly)",
               "description": "Monthly FDIC national average savings rate and effective federal funds rate, "
                              f"{_mon(SNDR[0][0])} to {_mon(last_s[0])}, with the FDIC's current national rates by product.",
               "url": URL + "/rates/", "temporalCoverage": f"{SNDR[0][0][:7]}/{last_s[0][:7]}",
               "spatialCoverage": "United States", "isAccessibleForFree": True,
               "license": "https://creativecommons.org/licenses/by/4.0/",
               "creator": {"@type": "Organization", "name": NAME, "url": URL},
               "isBasedOn": ["https://fred.stlouisfed.org/series/SNDR", "https://fred.stlouisfed.org/series/FEDFUNDS",
                             "https://www.fdic.gov/national-rates-and-rate-caps"],
               "distribution": {"@type": "DataDownload", "encodingFormat": "text/csv",
                                "contentUrl": URL + "/data/savings-rate-vs-fed-funds.csv"}}
    return page("/rates/", "Savings Account Interest Rates Chart: National Average vs the Fed",
                f"The national average savings rate is {NAT['savings']:.2f}% ({NAT_ASOF}). Chart of savings rates vs the fed funds rate since 2021, plus money market and CD averages.",
                body, [dataset, faq_schema([(q, strip_tags(a)) for q, a in qs])],
                crumbs=[("Home", "/"), ("Rates", "/rates/")])


# --- Tier 2: learn pages ------------------------------------------------------

def learn_how_mma_works():
    mm = NAT["money_market"] / 100
    return learn_page(
        "/learn/how-money-market-accounts-work/", "How Does a Money Market Account Work? Rates, Fees, Limits",
        f"A money market account is an insured bank deposit with savings-style interest and checking features. Typical rate: {NAT['money_market']:.2f}% APY. Fees and limits.",
        "How does a money market account work?",
        "A savings account with a chequebook attached — and the rate, fees and limits that come with it.",
        ["A <b>money market account (MMA)</b> is a bank or credit-union deposit account that pays interest like a "
         "savings account and usually adds some checking features — checks, a debit card, or both. It is FDIC- or "
         "NCUA-insured to $250,000 per depositor, per institution, per ownership category.",
         f"The <b>typical money market rate is {NAT['money_market']:.2f}% APY</b>, the FDIC national average as of "
         f"{NAT_ASOF} — higher than the {NAT['savings']:.2f}% average savings account, but far below what "
         "high-yield money market accounts at online banks pay."],
        f"""
<h2>How it works, step by step</h2>
<ol>
<li><b>You deposit money</b> — often with a higher opening minimum than a savings account.</li>
<li><b>It earns a variable rate.</b> Interest usually compounds daily and is credited monthly. Many banks use tiers: a higher APY on larger balances.</li>
<li><b>You can spend from it directly</b> with checks or a debit card, or transfer to checking. That access is the main difference from a savings account.</li>
<li><b>The bank may limit withdrawals.</b> The federal six-a-month limit was removed in 2020, but a bank may still set its own and charge for extra transactions. See <a href="/learn/can-you-withdraw-from-a-hysa/">withdrawal rules</a>.</li>
</ol>

<h2>Typical money market account interest rate</h2>
<div class="tw"><table><thead><tr><th>Account</th><th class="n">National average APY</th><th class="n">A year on $10,000</th></tr></thead><tbody>
<tr><td>Interest checking</td><td class="n">{NAT['interest_checking']:.2f}%</td><td class="n">{money(100 * NAT['interest_checking'], 2)}</td></tr>
<tr><td>Savings</td><td class="n">{NAT['savings']:.2f}%</td><td class="n">{money(100 * NAT['savings'], 2)}</td></tr>
<tr><td>Money market</td><td class="n">{NAT['money_market']:.2f}%</td><td class="n">{money(100 * NAT['money_market'], 2)}</td></tr>
<tr><td>12-month CD</td><td class="n">{NAT['cd_12m']:.2f}%</td><td class="n">{money(100 * NAT['cd_12m'], 2)}</td></tr>
</tbody></table></div>
<p class="hint">Source: {FDIC_LINK}, as of {NAT_ASOF}. Averages include large branch banks; see the full <a href="/rates/">rates chart</a>.</p>

<h2>What is a high-yield money market account?</h2>
<p>The same product at a bank — usually online — that pays well above the national average. "High-yield" is marketing, not a legal category: compare the APY, the minimum balance needed to earn it, and the fees.</p>

<h2>Money market account fees</h2>
<ul>
<li><b>Monthly maintenance fee</b>, often waived above a minimum daily balance. On a small balance a fee can wipe out the interest.</li>
<li><b>Excess-transaction fee</b> if the bank still limits withdrawals.</li>
<li><b>Check and debit-card fees</b> at some banks — ordering checks, out-of-network ATMs.</li>
</ul>
<p>Read the fee schedule before the rate: a $10 monthly fee costs $120 a year, which is more than {money(10000 * mm, 0)} of interest on $10,000 at the national average.</p>

<h2>Money market checking</h2>
<p>Some banks sell a "money market checking" account — really a checking account that pays a money-market-style rate. Useful if you keep a large everyday balance; compare it with a <a href="/learn/checking-vs-savings/">checking and a separate savings account</a>.</p>

<h2>Account, not fund</h2>
<p>A money market <em>fund</em> is an investment sold by brokerages. It is not a bank deposit and not FDIC-insured. If your brokerage calls its cash option "money market", it is almost certainly the fund. <a href="/learn/hysa-vs-money-market/">HYSA vs money market</a> compares the account with a high-yield savings account.</p>
""",
        [("How much will $10,000 make in a money market account?",
          f"At the national average of {NAT['money_market']:.2f}% APY, about {money(10000 * mm, 2)} in a year. At 4.00% APY it is $400. "
          "Enter your bank's rate in the <a href=\"/\">calculator</a> to see any balance and term."),
         ("What is the typical interest rate for a money market account?",
          f"{NAT['money_market']:.2f}% APY, the FDIC national average as of {NAT_ASOF}. High-yield money market accounts pay several times that."),
         ("Can you lose money in a money market account?",
          "Not from the account itself, up to the FDIC or NCUA limit — it is a bank deposit. You can lose value to fees or inflation. A money market fund is different and is not insured."),
         ("Is interest on a money market account taxable?",
          "Yes, as ordinary income in the year it is credited, reported on Form 1099-INT. See <a href=\"/learn/hysa-interest-tax/\">how savings interest is taxed</a>.")],
        "How money market accounts work")


def learn_checking_vs_savings():
    return learn_page(
        "/learn/checking-vs-savings/", "Checking vs Savings Account: The Main Differences",
        "The main differences between a checking and a savings account: what each is for, interest rates, access, limits and fees — with FDIC national average rates.",
        "Checking vs savings: the main differences",
        "One is for spending, one is for keeping. Here is what actually separates them.",
        ["A <b>checking account</b> is for spending: debit card, checks, bill pay and unlimited transactions, "
         f"usually with little or no interest (the national average for interest checking is {NAT['interest_checking']:.2f}%).",
         f"A <b>savings account</b> is for money you are keeping: it pays interest ({NAT['savings']:.2f}% on average, "
         "far more at a high-yield account) but is less convenient to spend from. Most people need both."],
        f"""
<h2>Side by side</h2>
<div class="tw"><table><thead><tr><th></th><th>Checking</th><th>Savings</th></tr></thead><tbody>
<tr><td>Purpose</td><td>Everyday spending and bills</td><td>Emergency fund, goals</td></tr>
<tr><td>National average rate</td><td>{NAT['interest_checking']:.2f}% (interest checking)</td><td>{NAT['savings']:.2f}%</td></tr>
<tr><td>Debit card and checks</td><td>Yes</td><td>Usually not</td></tr>
<tr><td>Transactions</td><td>Unlimited</td><td>Some banks limit withdrawals</td></tr>
<tr><td>Insurance</td><td>FDIC / NCUA to $250,000</td><td>FDIC / NCUA to $250,000</td></tr>
</tbody></table></div>
<p class="hint">Rates: {FDIC_LINK}, as of {NAT_ASOF}.</p>

<h2>What is a traditional savings account?</h2>
<p>The standard savings account at a branch bank. It is convenient — same bank, same app, instant transfers — but pays around the national average of {NAT['savings']:.2f}%: {money(100 * NAT['savings'], 2)} a year on $10,000. A <a href="/learn/what-is-a-hysa/">high-yield savings account</a> is the same product with a higher rate, usually at an online bank, at the cost of one-to-three-day transfers.</p>

<h2>How much to keep in each</h2>
<ul>
<li><b>Checking:</b> a month or so of spending plus a buffer against overdrafts. Anything more earns next to nothing.</li>
<li><b>Savings:</b> your emergency fund and near-term goals. The <a href="/calculators/emergency-fund/">emergency fund calculator</a> sizes it; <a href="/learn/how-much-to-keep-in-a-hysa/">how much to keep in a HYSA</a> covers the rest.</li>
</ul>

<h2>Where a money market account fits</h2>
<p>Between the two: savings-style interest with some checking features. <a href="/learn/how-money-market-accounts-work/">How money market accounts work</a>.</p>
""",
        [("What are the main differences between a checking and savings account?",
          "Checking is built for spending — debit card, checks, unlimited transactions, little interest. Savings is built for keeping — it pays interest but is less convenient to spend from, and some banks limit withdrawals."),
         ("Should I keep my money in checking or savings?",
          "Keep what you will spend this month in checking and the rest in savings, where it earns interest. Both are insured to the same limits."),
         ("Can I have a checking and savings account at different banks?",
          "Yes. Many people keep checking at a branch bank and savings at an online bank for the higher rate, and link the two for transfers.")],
        "Checking vs savings")


def learn_hysa_pros_cons():
    tax, infl, apy = 0.24, 0.03, 0.04
    after = apy * (1 - tax)
    real = (1 + after) / (1 + infl) - 1
    return learn_page(
        "/learn/hysa-pros-and-cons/", "High-Yield Savings Account Pros and Cons (and Real Risks)",
        "The advantages and disadvantages of a high-yield savings account: rate, safety and access against variable rates, tax, inflation and transfer delays.",
        "High-yield savings accounts: pros, cons and risks",
        "What you get, what you give up, and the risks that are real versus the ones that are not.",
        ["<b>Pros:</b> a much higher rate than a traditional savings account, FDIC insurance to $250,000, and access "
         "to your money within a few days with no penalty.",
         "<b>Cons:</b> the rate is variable, interest is taxed as ordinary income, inflation can erase most of the "
         "real return, and transfers out are slower than at your main bank."],
        f"""
<h2>Advantages</h2>
<ul>
<li><b>Rate.</b> The national average savings rate is {NAT['savings']:.2f}% ({NAT_ASOF}); high-yield accounts pay many times that.</li>
<li><b>Safety.</b> A deposit at an FDIC-insured bank is covered to $250,000 per depositor, per bank, per ownership category. No market risk: the balance cannot fall.</li>
<li><b>Access.</b> Unlike a <a href="/calculators/cd-calculator/">CD</a>, there is no penalty for taking money out.</li>
<li><b>Simplicity.</b> Usually no minimum and no monthly fee.</li>
</ul>

<h2>Disadvantages</h2>
<ul>
<li><b>Variable rate.</b> The bank can cut it at any time, and usually does when the Fed cuts. A CD locks a rate; a HYSA does not.</li>
<li><b>Tax.</b> Interest is taxed as ordinary income each year, even if you leave it in the account.</li>
<li><b>Inflation.</b> After tax, the real return can be close to zero (see below).</li>
<li><b>Slower access.</b> Transfers to your checking account usually take one to three business days; most HYSAs have no debit card or branch.</li>
<li><b>Possible withdrawal limits.</b> Some banks still cap withdrawals per month. <a href="/learn/can-you-withdraw-from-a-hysa/">What the rules are</a>.</li>
<li><b>Teaser and tiered rates.</b> A headline APY may be a promotion, or only apply to part of the balance.</li>
</ul>

<h2>The disadvantage in numbers</h2>
<p>At {pct(apy)} APY, a 24% federal bracket leaves {pct(after)} after tax. With 3% inflation, the real, after-tax return is about <b>{pct(real)}</b> a year. A HYSA protects your money from falling in value; it is not built to grow it. Try your own figures in the <a href="/">calculator</a>'s tax and inflation fields.</p>

<h2>High-yield savings account risks, honestly</h2>
<ul>
<li><b>The bank failing</b> — covered by FDIC insurance up to the limit. Check the bank on the FDIC's BankFind tool.</li>
<li><b>Balances above $250,000</b> at one bank in one ownership category are not covered. Split across banks or ownership categories.</li>
<li><b>Fintech apps.</b> If an app holds your money at a partner bank, FDIC insurance covers the partner bank failing, not the app company failing. Know which bank actually holds the deposit.</li>
<li><b>Opportunity cost.</b> Money you will not need for many years has historically done better invested — see <a href="/learn/hysa-vs-investing/">HYSA vs investing</a>.</li>
</ul>
""",
        [("What are the disadvantages of a high-yield savings account?",
          "A variable rate that can be cut at any time, interest taxed as ordinary income, a real return that inflation can erase, and transfers that take one to three business days."),
         ("Is there any risk with a high-yield savings account?",
          "Very little to the balance itself if the bank is FDIC-insured and you stay under $250,000 per bank per ownership category. The real risks are the rate falling and inflation."),
         ("Is a high-yield savings account worth it?",
          f"For cash you need to keep safe and reachable, usually yes: the national average savings account pays {NAT['savings']:.2f}%, so moving an emergency fund to a high-yield account typically multiplies the interest many times over.")],
        "HYSA pros and cons")


def learn_can_withdraw():
    return learn_page(
        "/learn/can-you-withdraw-from-a-hysa/", "Can You Withdraw From a High-Yield Savings Account?",
        "Yes — you can withdraw from a high-yield savings account at any time without penalty. How transfers work, how long they take, and the Regulation D six-per-month rule.",
        "Can you withdraw money from a high-yield savings account?",
        "Yes, whenever you like. What to expect on timing, limits and fees.",
        ["<b>Yes.</b> You can take money out of a high-yield savings account at any time, and you keep the interest "
         "already earned. There is no early-withdrawal penalty — that applies to CDs, not savings accounts.",
         "Withdrawals usually go by transfer to a linked checking account and arrive in one to three business days. "
         "Some banks still limit the number of withdrawals per month, even though the federal six-per-month rule was "
         "removed in 2020."],
        """
<h2>How to take money out</h2>
<ol>
<li><b>Transfer to your linked checking account</b> — the standard route. Initiate it in the app; money typically arrives in one to three business days, sometimes the next day.</li>
<li><b>Wire transfer</b> — same day at many banks, usually for a fee.</li>
<li><b>ATM card or check</b> — only if your bank offers one on the savings account. Most online HYSAs do not.</li>
</ol>
<p>Plan for the delay: keep a month of spending in checking so an emergency does not wait on a transfer.</p>

<h2>The six-withdrawals-a-month rule (Regulation D)</h2>
<p>Until 2020, the Federal Reserve's Regulation D limited "convenient" transfers and withdrawals from savings accounts — online, phone, card and similar — to six a month. On <b>April 24, 2020</b>, the Federal Reserve Board removed that limit with an interim final rule (<a href="https://www.federalreserve.gov/newsevents/pressreleases/bcreg20200424a.htm" rel="noopener">Federal Reserve announcement</a>).</p>
<p>The rule change <em>allows</em> banks to drop the limit; it does not <em>require</em> them to. Some banks still cap savings withdrawals at six a month and charge an excess-transaction fee, or convert an account that is repeatedly over the limit to checking. Your account agreement says which applies.</p>

<h2>Other limits to check</h2>
<ul>
<li><b>Daily or monthly transfer caps</b> on how much you can move out electronically.</li>
<li><b>Minimum balance</b> to keep earning the headline APY or to avoid a fee.</li>
<li><b>Holds on new deposits</b> — money just transferred in may not be withdrawable for a few days.</li>
</ul>

<h2>What withdrawing does to your interest</h2>
<p>Interest stops accruing on the amount you take out, and that is all. How long a balance lasts under regular withdrawals is what the <a href="/calculators/withdrawal/">withdrawal calculator</a> works out.</p>
""",
        [("Can you withdraw from a HYSA at any time?",
          "Yes. There is no penalty, and you keep interest already earned. Some banks limit how many withdrawals you can make each month."),
         ("How many times can you withdraw from a high-yield savings account?",
          "There is no federal limit since April 2020, when the Federal Reserve removed Regulation D's six-per-month cap. Your bank may still set its own limit; check the account agreement."),
         ("How long does it take to withdraw from a high-yield savings account?",
          "Usually one to three business days by transfer to a linked checking account. A wire can be same-day, usually for a fee."),
         ("Do you lose interest if you withdraw from a HYSA?",
          "No. Interest already credited is yours. You simply stop earning on the amount you withdraw.")],
        "Can you withdraw from a HYSA")


def learn_hysa_vs_investing():
    r5 = R.project(10000, 0.04, "daily", 0, 60)
    return learn_page(
        "/learn/hysa-vs-investing/", "HYSA vs Brokerage Account, Roth IRA or 401(k): Where Should Money Go?",
        "High-yield savings vs a brokerage account, Roth IRA, 401(k) or money market fund: safety, access, tax and time horizon compared, without the sales pitch.",
        "High-yield savings vs investing",
        "Not a contest: they do different jobs. The question is which job your money has.",
        ["A <b>high-yield savings account</b> is for money you need safe and reachable — an emergency fund, or a goal "
         "within a few years. A <b>brokerage account, Roth IRA or 401(k)</b> is for money you will not need for many years "
         "and can leave through market falls.",
         f"The trade: $10,000 at 4.00% APY becomes {money(r5['finalBalance'], 2)} in five years, guaranteed as long as the rate "
         "holds. Invested, it may become much more or temporarily less — and you cannot know which in advance."],
        """
<h2>At a glance</h2>
<div class="tw"><table><thead><tr><th></th><th>HYSA</th><th>Brokerage account</th><th>Roth IRA</th><th>401(k)</th></tr></thead><tbody>
<tr><td>Can the balance fall?</td><td>No</td><td>Yes, if invested</td><td>Yes, if invested</td><td>Yes, if invested</td></tr>
<tr><td>Protection</td><td>FDIC to $250,000</td><td>SIPC (broker failure, not losses)</td><td>Depends on holdings</td><td>Depends on holdings</td></tr>
<tr><td>Access</td><td>Any time</td><td>Any time (sell first)</td><td>Contributions any time; earnings restricted</td><td>Restricted before 59½</td></tr>
<tr><td>Tax</td><td>Interest taxed yearly</td><td>Taxed on dividends and gains</td><td>Qualified withdrawals tax-free</td><td>Tax-deferred (or Roth)</td></tr>
<tr><td>Job</td><td>Emergencies, short-term goals</td><td>Long-term, flexible</td><td>Retirement</td><td>Retirement</td></tr>
</tbody></table></div>

<h2>HYSA vs brokerage account</h2>
<p>A brokerage account is a container. Holding cash in it is similar to savings; holding stocks or funds is investing. SIPC protects up to $500,000 (including $250,000 of cash) if the broker fails — it does <em>not</em> protect against investments losing value. Use savings for what you might need in the next few years, and the brokerage for the rest.</p>

<h2>Roth IRA vs high-yield savings account</h2>
<p>A Roth IRA is a tax wrapper, not an investment: you can even hold cash in one. You can withdraw your <em>contributions</em> at any time without tax or penalty; earnings are restricted until the rules are met. Annual contributions are capped, so an unused year's allowance is gone. That is why many people fill a Roth for the long term and keep the emergency fund in a HYSA, rather than choosing one.</p>

<h2>High-yield savings account vs 401(k)</h2>
<p>A 401(k) is for retirement. Withdrawals before age 59½ are generally taxable and face an additional 10% tax, with some exceptions. An employer match is an immediate return no savings rate can beat — but it is not an emergency fund.</p>

<h2>Money market fund vs HYSA</h2>
<p>A money market fund is a low-risk investment fund held at a brokerage; its yield moves with short-term rates, and it is not FDIC-insured. A HYSA is a bank deposit. If your cash sits at a brokerage anyway, a money market fund can be convenient; for an emergency fund, the insured deposit is simpler. See <a href="/learn/hysa-vs-money-market/">HYSA vs money market</a>.</p>

<h2>A simple way to decide</h2>
<ol>
<li>Size your emergency fund with the <a href="/calculators/emergency-fund/">emergency fund calculator</a> and keep it in a HYSA.</li>
<li>Money for goals within about five years: HYSA or <a href="/calculators/cd-ladder/">CDs</a>.</li>
<li>Money for more than five years away: consider investing, ideally through tax-advantaged accounts first.</li>
</ol>
""",
        [("Is a HYSA better than a brokerage account?",
          "Neither is better; they do different jobs. A HYSA keeps money safe and reachable. A brokerage account holding investments can grow more over long periods but can fall in value."),
         ("Should I put money in a Roth IRA or a high-yield savings account?",
          "Many people do both: the emergency fund in a HYSA, long-term money in a Roth IRA. Roth contributions (not earnings) can be withdrawn at any time, but contribution room is capped each year."),
         ("Is a money market fund safer than a HYSA?",
          "A HYSA at an FDIC-insured bank is insured to $250,000; a money market fund is not insured, though it is designed to be low-risk.")],
        "HYSA vs investing")


def learn_how_much_in_hysa():
    ef = R.emergency_fund([3200], 6, 0, 0, 0.04)
    return learn_page(
        "/learn/how-much-to-keep-in-a-hysa/", "How Much Should You Keep in a High-Yield Savings Account?",
        "How much to keep in a HYSA: your emergency fund plus money for goals within a few years, under the $250,000 FDIC limit. How many accounts you need.",
        "How much to keep in a high-yield savings account",
        "Enough to cover emergencies and near-term plans — and less than you might think beyond that.",
        ["Keep your <b>emergency fund</b> — commonly three to six months of essential expenses — plus money for "
         "goals in roughly the next few years. Beyond that, long-term money usually belongs in investments.",
         "There is no maximum, but deposits over <b>$250,000</b> at one bank in one ownership category are not "
         "FDIC-insured; split larger sums across banks."],
        f"""
<h2>Three layers</h2>
<ol>
<li><b>Emergency fund.</b> Three months of essentials is a floor; six is common; more if your income is irregular or you are the sole earner. On $3,200 of monthly essentials, six months is {money(ef['target'])}, which earns {money(ef['yearlyInterestAtTarget'])} a year at 4% APY. <a href="/calculators/emergency-fund/">Work out your own number</a>.</li>
<li><b>Known expenses within a few years</b> — a car, a house deposit, tuition, a wedding. Money you cannot afford to see fall in value.</li>
<li><b>Nothing much else.</b> Cash you will not need for many years loses ground to inflation after tax. See <a href="/learn/hysa-vs-investing/">HYSA vs investing</a>.</li>
</ol>

<h2>Is there such a thing as too much?</h2>
<p>Two limits matter. The first is insurance: $250,000 per depositor, per bank, per ownership category. Joint accounts and certain trust accounts are separate categories, so a couple can insure more at one bank. The second is opportunity cost: the <a href="/learn/hysa-pros-and-cons/">real after-tax return</a> on savings can be close to zero.</p>

<h2>How many high-yield savings accounts should you have?</h2>
<p>One is enough for most people. Reasons to have more:</p>
<ul>
<li><b>Over the insurance limit</b> — a second bank insures the excess.</li>
<li><b>Separate goals</b> — many banks offer "buckets" or sub-accounts inside one account, which does the same job without extra logins.</li>
<li><b>Rate chasing</b> — possible, but the gain on a small balance is often a few dollars a year.</li>
</ul>
<p>Several accounts at the <em>same</em> bank in the same ownership category share one $250,000 limit.</p>
""",
        [("How much money should I keep in a HYSA?",
          "Your emergency fund — commonly three to six months of essential expenses — plus money for goals in the next few years."),
         ("How many high-yield savings accounts should I have?",
          "One is enough for most people. A second bank makes sense if you are above the $250,000 FDIC limit."),
         ("Is it smart to keep a lot of money in a high-yield savings account?",
          "It is safe, but after tax and inflation the real return can be close to zero, so money you will not need for many years usually does better invested.")],
        "How much to keep in a HYSA")


if __name__ == "__main__":
    note = parity_summary()
    PARITY_N = re.search(r"^(\S+) comparisons", note).group(1)
    print("engine:", note)
    for d in SITE.iterdir():
        if d.name not in ("assets",):
            shutil.rmtree(d) if d.is_dir() else d.unlink()
    paths = [home(), calculators_hub(), reverse_calc(), cd_calc(), goal_calc(), withdrawal_calc(),
             apy_converter(), cd_calculator(), emergency_fund_calc(), simple_interest_calc(), cd_ladder_calc(),
             learn_what_is_apy(), learn_apy_formula(), learn_apy_vs_rate(),
             learn_apr_vs_apy(), learn_what_is_hysa(), learn_money_market(), learn_compounding(),
             learn_tax(), learn_how_mma_works(), learn_checking_vs_savings(), learn_hysa_pros_cons(),
             learn_can_withdraw(), learn_hysa_vs_investing(), learn_how_much_in_hysa(),
             learn_hub(), rates_page(), answers_hub()]
    paths += [answer_page(a) for a in ANSWER_AMOUNTS]
    paths += [glossary(), methodology(note)]
    static_pages()
    paths += ["/about/", "/disclosures/", "/privacy/", "/terms/"]
    robots(); llms_txt(paths, note); api_summary(note); htaccess(); icons(); sitemap(paths)
    print(f"built {len(paths)} pages + 404 → {SITE}")
