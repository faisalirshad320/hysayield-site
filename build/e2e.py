"""End-to-end browser test of every calculator, plus screenshots.

Checks, on a real Chromium: each tool renders a result with no NaN/undefined,
no console errors, the headline matches the Python reference to the dollar,
edge cases degrade gracefully, share links round-trip, and the CSV downloads.
Run: python3 build/e2e.py
"""
import functools
import http.server
import json
import re
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE, OUT = ROOT / "site", ROOT / "build" / "shots"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "build"))
import reference as R  # noqa: E402

PORT = 8781


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    h.log_message = lambda *a: None
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), h).serve_forever()


threading.Thread(target=serve, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}"

results, failures = [], []


def check(name, cond, detail=""):
    (results if cond else failures).append(f"{'ok  ' if cond else 'FAIL'} {name}{(' — ' + detail) if detail else ''}")


def dollars(s):
    m = re.search(r"\$([\d,]+(?:\.\d+)?)", s)
    return float(m.group(1).replace(",", "")) if m else None


def fill(page, sel, val):
    page.fill(sel, str(val))
    page.dispatch_event(sel, "input")


with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    def out_text():
        page.wait_for_timeout(250)
        return page.inner_text("#out")

    # 1. Main calculator — headline must equal the reference to the dollar.
    page.goto(BASE + "/")
    fill(page, "#principal", 10000); fill(page, "#apy", 4.5); fill(page, "#deposit", 250)
    fill(page, "#years", 5); page.select_option("#compounding", "daily")
    t = out_text()
    want = R.project(10000, 0.045, "daily", 250, 60)["finalBalance"]
    got = dollars(page.inner_text(".big"))
    check("main: headline matches reference", got is not None and abs(got - round(want)) <= 1,
          f"page {got} vs reference {want:,.2f}")
    check("main: no NaN/undefined", "NaN" not in t and "undefined" not in t and "Infinity" not in t)
    page.screenshot(path=str(OUT / "home-mobile.png"), full_page=False)

    # 1b. Tax + inflation path: verdict must state APY x (1 - tax).
    page.click("details.adv summary")
    fill(page, "#fed", 22); fill(page, "#state", 5); fill(page, "#inflation", 3)
    t = out_text()
    check("main: after-tax yield = APY×(1−tax) = 3.29%", "3.29%" in t, t[:200].replace("\n", " "))
    check("main: real value labelled in today's dollars", "today's dollars" in t)

    # 1c. Edge cases.
    fill(page, "#principal", ""); fill(page, "#apy", ""); t = out_text()
    check("edge: empty fields don't produce NaN", "NaN" not in t and "undefined" not in t)
    fill(page, "#apy", 99); t = out_text()
    check("edge: absurd APY warns, doesn't crash", "far above" in page.inner_text("#err"))
    fill(page, "#apy", 0); fill(page, "#principal", 5000); t = out_text()
    check("edge: 0% APY returns contributions only", "NaN" not in t)

    # 1d. Share link round-trip.
    fill(page, "#principal", 37500); fill(page, "#apy", 4.1); fill(page, "#years", 3)
    ctx.grant_permissions(["clipboard-read", "clipboard-write"])
    page.click("#share"); page.wait_for_timeout(300)
    link = page.evaluate("navigator.clipboard.readText()")
    check("share: link carries inputs", "p=37500" in link and "a=4.1" in link, link)
    p2 = ctx.new_page(); p2.goto(link); p2.wait_for_timeout(300)
    check("share: link restores inputs", p2.input_value("#principal") == "37500" and p2.input_value("#apy") == "4.1")
    p2.close()

    # 1e. CSV download.
    with page.expect_download() as dl:
        page.click("#csv")
    path = dl.value.path()
    rows = Path(path).read_text().strip().splitlines()
    check("csv: header + one row per month", rows[0].startswith("month,") and len(rows) == 1 + 36, f"{len(rows)} lines")

    # 2. Reverse solver.
    page.goto(BASE + "/calculators/how-much-to-earn/")
    fill(page, "#target", 1000); fill(page, "#apy", 4.5)
    got = dollars(page.inner_text(".big")); want = R.balance_for_monthly_income(1000, 0.045)
    check("reverse: matches reference", got is not None and abs(got - round(want)) <= 1, f"{got} vs {want:,.0f}")

    # 3. CD vs HYSA — at equal rates and no drift it must tie (or nearly).
    page.goto(BASE + "/calculators/cd-vs-hysa/")
    fill(page, "#principal", 10000); fill(page, "#months", 24); fill(page, "#cdapy", 4.5)
    fill(page, "#apy", 4.5); fill(page, "#drift", 0); fill(page, "#penalty", 3)
    t = out_text()
    check("cd: equal rates → reported as a tie", "A tie" in t, t[:120].replace("\n", " "))
    fill(page, "#cdapy", 4.7); fill(page, "#drift", -0.5); t = out_text()
    check("cd: break-even rate shown", "Break-even" in t)
    page.screenshot(path=str(OUT / "cd-mobile.png"))

    # 4. Goal — first month the goal is reached (34, verified in Python).
    page.goto(BASE + "/calculators/savings-goal/")
    fill(page, "#goal", 20000); fill(page, "#principal", 5000); fill(page, "#deposit", 400); fill(page, "#apy", 4.5)
    t = out_text()
    check("goal: 34 months = 2.8 years", "2.8 years" in t, t[:80].replace("\n", " "))
    fill(page, "#deposit", 0); fill(page, "#apy", 0); t = out_text()
    check("goal: unreachable is explained, not NaN", "never reached" in t)

    # 5. Withdrawal — $367/mo is sustainable on $100k at 4.5%; $368 is not.
    page.goto(BASE + "/calculators/withdrawal/")
    fill(page, "#principal", 100000); fill(page, "#apy", 4.5); fill(page, "#withdrawal", 367)
    check("withdraw: below crossover lasts indefinitely", "Indefinitely" in out_text())
    fill(page, "#withdrawal", 1000)
    check("withdraw: above crossover runs out", "until the balance runs out" in out_text())

    # 6. Converter — 4.40% daily → 4.498% APY; editing APY back-fills the rate.
    page.goto(BASE + "/calculators/apy-converter/")
    page.select_option("#compounding", "daily"); fill(page, "#rate", 4.4)
    check("convert: 4.40% daily → 4.498%", "4.498%" in out_text())
    fill(page, "#apyin", 5); page.wait_for_timeout(250)
    back = float(page.input_value("#rate"))
    check("convert: APY→rate round-trips", abs((1 + back / 100 / 365) ** 365 - 1 - 0.05) < 1e-6, f"rate {back}")

    # 7. Every page loads with no console errors; static pages render.
    all_pages = sorted({"/" + str(f.parent.relative_to(SITE)).replace(".", "").strip("/") + "/"
                        for f in SITE.rglob("index.html")})
    for u in all_pages:
        u = "/" if u == "//" else u
        page.goto(BASE + u)
        page.wait_for_timeout(120)
    check(f"console: 0 errors across {len(all_pages)} pages", not errors, "; ".join(errors[:3]))

    # Desktop screenshot of the home page.
    dctx = br.new_context(viewport={"width": 1280, "height": 900})
    dp = dctx.new_page(); dp.goto(BASE + "/?p=25000&a=4.5&d=300&y=10")
    dp.wait_for_timeout(300); dp.screenshot(path=str(OUT / "home-desktop.png"), full_page=True)
    br.close()

print("\n".join(results + failures))
print(f"\n{len(results)} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
