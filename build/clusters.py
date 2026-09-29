"""Keyword clusters, topical map, glossary and page data for the HYSA site.

CLUSTERS is the categorised keyword map: one entry per page, with the head
term and the supporting terms that share its SERP intent. Volumes are US
monthly from Ahrefs, pulled 2026-09-29; CPC is in dollars (Ahrefs returns
cents). Nothing here renders as a keyword list — it drives titles, H1s,
answer blocks, internal links and the entity vocabulary.

Deliberately excluded, with reasons, in data/keywords.json: the commercial
listicle terms ("high yield savings account" 501k, "best hysa" 40k) and every
[bank] hysa term. Their KD reads 0 but the SERPs are NerdWallet, Bankrate and
Forbes at DR 90, and serving them honestly needs maintained live bank rates
we do not have.
"""

# --- 1. Clusters ------------------------------------------------------------

CLUSTERS = {
    "/": dict(
        tier="pillar", intent="utility",
        head=("hysa calculator", 24000, 0, 1.50),
        terms=[("savings account interest calculator", 11000, 0, 1.20),
               ("simple savings calculator", 5800, 0, 1.20),
               ("apy calculator savings", 2000, 0, 1.40),
               ("apy calculator monthly", 1900, 0, 1.40),
               ("monthly savings calculator", 1900, 6, 1.20),
               ("high-yield savings account calculator", 1400, 0, None)],
    ),
    "/calculators/how-much-to-earn/": dict(
        tier="supporting", intent="utility",
        head=("how much do i need in a hysa to make $1000 a month", None, None, None),
        terms=[("how much interest does $100,000 earn", None, None, None)],
    ),
    "/calculators/cd-vs-hysa/": dict(
        tier="supporting", intent="commercial investigation",
        head=("cd vs hysa", 2300, 1, 2.00),
        terms=[("cd rates calculator", 7000, 0, 1.30),
               ("cd calculator apy", 2700, 0, 1.30),
               ("cd vs high yield savings", 2500, 0, 1.70)],
    ),
    "/calculators/savings-goal/": dict(
        tier="supporting", intent="utility",
        head=("savings goal calculator", None, None, None),
        terms=[("how long to save", None, None, None)],
    ),
    "/calculators/withdrawal/": dict(
        tier="supporting", intent="utility",
        head=("savings withdrawal calculator", 3200, 18, 1.00), terms=[],
    ),
    "/calculators/apy-converter/": dict(
        tier="supporting", intent="utility",
        head=("apy to interest rate converter", None, None, None),
        terms=[("nominal rate to apy", None, None, None)],
    ),
    "/learn/what-is-apy/": dict(
        tier="pillar", intent="informational",
        head=("what is apy", 28000, 5, 1.70),
        terms=[("apy", 50000, 0, 2.00), ("what does apy mean", 12000, 13, 0.70),
               ("what does apy stand for", 3800, 0, 0.80),
               ("what is apy in banking", 3500, 24, 0.60),
               ("apy definition", 1700, 0, 0.30), ("whats apy", 1700, 0, 1.70)],
    ),
    "/learn/apy-formula/": dict(
        tier="supporting", intent="informational",
        head=("apy formula", 2700, 0, 0.80), terms=[],
    ),
    "/learn/apy-vs-interest-rate/": dict(
        tier="supporting", intent="informational",
        head=("apy vs interest rate", 12000, 14, 1.60),
        terms=[("interest rate vs apy", 1600, 14, 0.09)],
    ),
    "/learn/apr-vs-apy/": dict(
        tier="supporting", intent="informational",
        head=("apr vs apy", 8500, 0, 0.05),
        terms=[("apy vs apr", 6900, 0, 0.07)],
    ),
    "/learn/what-is-a-hysa/": dict(
        tier="pillar", intent="informational",
        head=("what is a high yield savings account", 21000, 9, 1.60),
        terms=[("how does a high yield savings account work", 2900, 3, 1.70),
               ("how do high yield savings accounts work", 2400, 0, 1.70),
               ("what is high yield savings account", 2300, 9, 1.70),
               ("what is hysa", 1700, 5, 1.50)],
    ),
    "/learn/hysa-vs-money-market/": dict(
        tier="supporting", intent="commercial investigation",
        head=("money market vs high yield savings", 3400, 0, 1.50),
        terms=[("money market account vs high yield savings", 1900, 4, 1.30),
               ("hysa vs money market", 1600, 5, 1.90)],
    ),
    "/learn/how-hysa-compounding-works/": dict(
        tier="supporting", intent="informational",
        head=("compound interest savings account", 3600, 10, 2.00), terms=[],
    ),
    "/learn/hysa-interest-tax/": dict(
        tier="supporting", intent="informational",
        head=("is hysa interest taxable", None, None, None),
        terms=[("do you pay taxes on high yield savings", None, None, None)],
    ),
    "/glossary/": dict(tier="supporting", intent="informational",
                       head=("savings and apy terms", None, None, None), terms=[]),
    "/methodology/": dict(tier="supporting", intent="informational",
                          head=("how this calculator works", None, None, None), terms=[]),
    "/calculators/": dict(tier="pillar", intent="utility",
                          head=("savings calculators", None, None, None), terms=[]),
    "/answers/": dict(tier="pillar", intent="informational",
                      head=("how much interest will my savings earn", None, None, None), terms=[]),
}

NAV_LABEL = {
    "/": "HYSA calculator",
    "/calculators/": "All calculators",
    "/calculators/how-much-to-earn/": "How much do I need to earn $1,000 a month",
    "/calculators/cd-vs-hysa/": "CD vs HYSA",
    "/calculators/savings-goal/": "Savings goal",
    "/calculators/withdrawal/": "Withdrawal calculator",
    "/calculators/apy-converter/": "APY and interest rate converter",
    "/learn/what-is-apy/": "What is APY",
    "/learn/apy-formula/": "The APY formula",
    "/learn/apy-vs-interest-rate/": "APY vs interest rate",
    "/learn/apr-vs-apy/": "APR vs APY",
    "/learn/what-is-a-hysa/": "What is a high-yield savings account",
    "/learn/hysa-vs-money-market/": "HYSA vs money market",
    "/learn/how-hysa-compounding-works/": "How compounding works",
    "/learn/hysa-interest-tax/": "Tax on savings interest",
    "/glossary/": "Glossary",
    "/methodology/": "Methodology",
    "/answers/": "Worked examples",
    "/learn/": "All guides",
}

LINKS = {
    "/": ["/calculators/cd-vs-hysa/", "/calculators/how-much-to-earn/",
          "/learn/what-is-apy/", "/learn/hysa-interest-tax/", "/methodology/", "/answers/"],
    "/calculators/": ["/", "/calculators/cd-vs-hysa/", "/calculators/how-much-to-earn/",
                      "/calculators/savings-goal/", "/calculators/withdrawal/",
                      "/calculators/apy-converter/"],
    "/calculators/how-much-to-earn/": ["/", "/learn/hysa-interest-tax/", "/answers/", "/calculators/"],
    "/calculators/cd-vs-hysa/": ["/", "/learn/hysa-vs-money-market/", "/methodology/", "/calculators/"],
    "/calculators/savings-goal/": ["/", "/calculators/", "/learn/how-hysa-compounding-works/"],
    "/calculators/withdrawal/": ["/", "/calculators/", "/calculators/how-much-to-earn/"],
    "/calculators/apy-converter/": ["/learn/apy-vs-interest-rate/", "/learn/apy-formula/", "/", "/calculators/"],
    "/learn/what-is-apy/": ["/", "/learn/apy-formula/", "/learn/apy-vs-interest-rate/",
                            "/learn/apr-vs-apy/", "/glossary/"],
    "/learn/apy-formula/": ["/learn/what-is-apy/", "/calculators/apy-converter/", "/methodology/", "/"],
    "/learn/apy-vs-interest-rate/": ["/learn/what-is-apy/", "/calculators/apy-converter/",
                                     "/learn/how-hysa-compounding-works/", "/"],
    "/learn/apr-vs-apy/": ["/learn/what-is-apy/", "/learn/apy-vs-interest-rate/", "/glossary/"],
    "/learn/what-is-a-hysa/": ["/", "/learn/hysa-vs-money-market/", "/learn/hysa-interest-tax/",
                               "/learn/what-is-apy/"],
    "/learn/hysa-vs-money-market/": ["/learn/what-is-a-hysa/", "/calculators/cd-vs-hysa/", "/glossary/"],
    "/learn/how-hysa-compounding-works/": ["/learn/what-is-apy/", "/", "/methodology/"],
    "/learn/hysa-interest-tax/": ["/", "/calculators/how-much-to-earn/", "/learn/what-is-a-hysa/"],
    "/glossary/": ["/", "/learn/what-is-apy/", "/methodology/"],
    "/methodology/": ["/", "/learn/apy-formula/", "/glossary/"],
    "/answers/": ["/", "/calculators/how-much-to-earn/", "/learn/what-is-apy/"],
    "/learn/": ["/", "/calculators/", "/glossary/", "/answers/"],
}

# --- 2. Worked-example pages ("how much does $X earn?") ---------------------
# Each renders a computed matrix, so no two pages carry the same numbers.

ANSWER_AMOUNTS = [1000, 5000, 10000, 25000, 50000, 100000, 250000]
ANSWER_APYS = [0.005, 0.02, 0.035, 0.04, 0.045, 0.05]
ANSWER_HORIZONS = [("1 month", 1), ("6 months", 6), ("1 year", 12),
                   ("2 years", 24), ("5 years", 60), ("10 years", 120)]

# --- 3. Glossary (rendered as schema.org DefinedTermSet) --------------------

GLOSSARY = [
    ("APY", "Annual percentage yield: what a deposit actually earns in a year once "
            "compounding is counted. It is the number banks must quote for savings "
            "accounts in the US, and the one to compare between banks."),
    ("Interest rate (nominal rate)", "The headline rate before compounding. A 4.40% rate "
            "compounded daily produces about 4.50% APY. Comparing one bank's rate against "
            "another's APY is not a like-for-like comparison."),
    ("APR", "Annual percentage rate: the cost of borrowing, including some fees. APR is for "
            "loans and credit cards; APY is for deposits. APR does not account for compounding, "
            "which is why the two differ on the same underlying rate."),
    ("High-yield savings account (HYSA)", "An ordinary savings account paying a much higher rate "
            "than a branch bank's standard account, usually because the bank is online and has no "
            "branch costs. The money is still a bank deposit and still FDIC-insured to the same limits."),
    ("Compounding", "Interest earning interest. How often it happens — daily, monthly, quarterly — "
            "changes the outcome, though far less than the rate itself does."),
    ("Compounding frequency", "How many times a year interest is added to the balance. Daily is "
            "most common for US high-yield savings. Once APY is quoted, frequency is already "
            "baked in, which is why two accounts with the same APY pay the same."),
    ("Money market account", "A deposit account that usually adds cheque-writing or a debit card, "
            "often with a higher minimum balance. Rates are broadly comparable to a HYSA; the "
            "difference is access, not yield."),
    ("Certificate of deposit (CD)", "A deposit locked for a fixed term at a fixed rate. You get "
            "rate certainty and lose access; breaking it early costs a penalty, typically quoted "
            "as a number of months of interest."),
    ("Early withdrawal penalty", "What a bank charges for breaking a CD before its term ends, "
            "usually expressed as 3, 6 or 12 months of interest. It can exceed the interest earned "
            "so far, meaning you get back less than you put in."),
    ("FDIC insurance", "US federal deposit insurance, $250,000 per depositor, per insured bank, "
            "per ownership category. It covers the bank failing; it does not cover the rate falling."),
    ("Variable rate", "A rate the bank can change at any time without notice. Every HYSA rate is "
            "variable, which is the main practical difference from a CD."),
    ("Ordinary annuity", "A series of equal payments made at the end of each period. Monthly "
            "deposits into savings behave this way, which is the assumption this calculator uses."),
    ("Real return", "What is left after inflation. A 4.5% APY with 3% inflation is about 1.5% in "
            "purchasing power, before tax."),
    ("Form 1099-INT", "The US tax form a bank issues when it pays you $10 or more of interest in a "
            "year. Savings interest is taxed as ordinary income, not at capital-gains rates."),
]

# --- 4. AI crawlers welcomed explicitly in robots.txt ----------------------

AI_CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
    "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot",
    "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent", "Amazonbot",
    "DuckAssistBot", "cohere-ai", "YouBot", "Timpibot", "Diffbot",
]
