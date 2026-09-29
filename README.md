# HYSA Yield — high-yield savings calculators

A static site: no database, no server code. The contents of `site/` are the web root.

Planned domain: **www.hysayield.com** (not yet registered — see "Switching domain" below).

## What's here

- `site/` — the website. 30 pages + 404, `assets/calc.js` (the engine), `assets/app.js` (UI),
  `llms.txt`, `api/summary.json`, `robots.txt`, `sitemap.xml`, `.htaccess`, icons.
- `build/build.py` — regenerates `site/`. **Refuses to build if the engine fails its cross-check.**
- `build/clusters.py` — keyword clusters, topical map, glossary, internal-link graph.
- `build/reference.py` — independent Python implementation of the maths + self-tests.
- `build/parity.js` — cross-checks the shipped JS engine against the Python reference.
- `build/e2e.py` — 20 browser tests on real Chromium.
- `data/keywords.json` — the Ahrefs keyword universe, with what was excluded and why.

## Page set

| Cluster | Page | Head keyword (US vol/mo, KD) |
| --- | --- | --- |
| Core tool | `/` | hysa calculator (24k, 0) + savings account interest calculator (11k, 0) |
| Reverse solver | `/calculators/how-much-to-earn/` | "how much to make $1,000 a month" (PAA) |
| CD comparison | `/calculators/cd-vs-hysa/` | cd rates calculator (7k, 0), cd vs hysa (2.3k, 1) |
| Goal | `/calculators/savings-goal/` | savings goal |
| Withdrawal | `/calculators/withdrawal/` | savings withdrawal calculator (3.2k, 18) |
| Converter | `/calculators/apy-converter/` | apy formula / apy calculator |
| APY | `/learn/what-is-apy/` | what is apy (28k, 5), apy (50k, 0) |
| | `/learn/apy-vs-interest-rate/` | apy vs interest rate (12k, 14) |
| | `/learn/apr-vs-apy/` | apr vs apy + apy vs apr (15.4k, 0) |
| | `/learn/apy-formula/` | apy formula (2.7k, 0) |
| HYSA basics | `/learn/what-is-a-hysa/` | what is a high yield savings account (21k, 9) |
| Comparison | `/learn/hysa-vs-money-market/` | money market vs high yield savings (3.4k, 0) |
| | `/learn/how-hysa-compounding-works/` | compound interest savings account (3.6k, 10) |
| | `/learn/hysa-interest-tax/` | is hysa interest taxable |
| Worked examples | `/answers/{1000..250000}/` | "how much does $X earn" (PAA) — 7 pages, each a computed table |

Deliberately **not** targeted: "high yield savings account" (501k), "best hysa" (40k) and every
"[bank] hysa" term. KD reads 0 but those SERPs are NerdWallet/Bankrate/Forbes at DR 90, and serving
them honestly needs maintained live bank rates.

## Build and test

```
python3 build/build.py      # regenerates site/ (runs the cross-check first)
node build/parity.js        # engine vs independent reference: must print PASS
python3 build/e2e.py        # 20 browser tests: must print "20 passed, 0 failed"
```

## Switching domain

The domain lives on one line: `URL = "https://www.hysayield.com"` near the top of
`build/build.py`. Change it, run the build, and every canonical, sitemap entry, schema URL,
llms.txt link, `.htaccess` redirect and contact address follows.

## Deploy on Cloudways (same as snowdayforecaster.com)

1. Register the domain.
2. Cloudways: add a PHP application on the existing server; add the domain; enable Let's Encrypt.
3. DNS at the registrar: `www` A record → the server IP; `@` URL redirect (301) → `https://www.<domain>/`.
4. Push `site/` to the GitHub repo's `main`; in Cloudways → Deployment via GIT set the path to
   `public_html/` and Pull.
5. Purge Varnish (Application Settings → Purge Site Cache).
6. Search Console: add a **Domain** property, verify by DNS TXT, submit `/sitemap.xml`.
7. Email forwarding: `hello@<domain>` → your inbox (the About, Privacy and Methodology pages use it).

## Before monetising

- This is a YMYL (finance) site. Keep "Not financial advice" disclosures, never recommend specific
  banks without clear affiliate disclosure, and update `/disclosures/` and `/privacy/` **before**
  adding ads, analytics or affiliate links.
- Finance CPCs here are high ($1–$14), so display ads are viable once traffic exists. Affiliate links
  to banks are the bigger opportunity but change the site's neutrality — decide deliberately.
