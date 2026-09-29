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
        # "cd rates calculator" / "cd calculator apy" moved to /calculators/cd-calculator/
        # (low-fruit expansion) so the two CD pages do not cannibalise each other.
        terms=[("cd vs high yield savings", 2500, 0, 1.70)],
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

# --- 1b. Low-fruit expansion (data/lowfruits.json has SERP verdicts) -------
# CPC not carried here (None); the shortlist file holds it.
CLUSTERS.update({
    "/calculators/emergency-fund/": dict(
        tier="tier1", intent='utility',
        head=('emergency fund calculator', 4800, 0, None),
        terms=[('emergency fund amount', 1000, 0, None),
               ('how much emergency fund', 900, 0, None),
               ('building an emergency fund', 500, 0, None),
               ('what is a emergency fund', 300, 0, None),
               ('how much is a good emergency fund', 200, 0, None),
               ('6 month emergency fund calculator', 200, 0, None),
               ('using heloc as emergency fund', 150, 0, None),
               ('emergency fund for rental property', 100, 0, None),
               ('saving for emergency fund', 90, 0, None),
               ('creating an emergency fund', 90, 0, None),
               ('whats a good emergency fund amount', 60, 0, None),
               ('roth ira emergency fund', 60, 0, None),
               ('emergency fund ratio calculator', 50, 0, None)]),
    "/calculators/cd-calculator/": dict(
        tier="tier1", intent='utility',
        head=('cd rates calculator', 7000, 0, None),
        terms=[('cd account calculator', 3500, 0, None),
               ('cd calculator apy', 2700, 0, None),
               ('free cd calculator', 1500, 0, None),
               ('cd compound interest calculator', 1200, 0, None),
               ('3 month cd calculator', 1000, 0, None),
               ('bank cd calculator', 800, 0, None),
               ('cd yield calculator', 600, 0, None),
               ('how to calculate cd rates', 350, 0, None),
               ('calculator for cd rates', 200, 0, None),
               ('saving cd calculator', 200, 0, None),
               ('cd calculator compounded quarterly', 150, 0, None),
               ('cd returns calculator', 150, 0, None)]),
    "/calculators/simple-interest/": dict(
        tier="tier1", intent='utility',
        head=('simple interest calculator', 24000, 0, None),
        terms=[]),
    "/learn/how-money-market-accounts-work/": dict(
        tier="tier2", intent='informational',
        head=('how does a money market account work', 6700, 0, None),
        terms=[('money market account typical interest rate', 4100, 0, None),
               ('how do money market accounts work', 2000, 0, None),
               ('typical interest rate for money market account', 600, 0, None),
               ('typical interest rate of a money market account', 500, 2, None),
               ('money market account fees', 500, 0, None),
               ('money market checking', 500, 0, None),
               ('what is a high yield money market account', 250, 0, None),
               ('interest on money market', 150, 0, None)]),
    "/learn/checking-vs-savings/": dict(
        tier="tier2", intent='informational',
        head=('what are the main differences between a checking and savings account?', 1800, 9, None),
        terms=[('what is a traditional savings account', 900, 0, None),
               ("what's the difference between a savings and checking account", 200, 3, None),
               ('what is a checking vs savings account', 100, 6, None)]),
    "/rates/": dict(
        tier="tier2", intent='informational + linkable asset',
        head=('savings account interest rates chart', 800, 0, None),
        terms=[('what is the average interest rate on a savings account', 600, 4, None),
               ('current interest rates on savings accounts', 600, 3, None),
               ('current savings account interest rate', 250, 0, None)]),
    "/learn/hysa-pros-and-cons/": dict(
        tier="tier2", intent='informational',
        head=('disadvantages of high-yield savings account', 900, 0, None),
        terms=[('pros and cons of high yield savings accounts', 150, 0, None),
               ('high yield savings account risks', 50, 3, None)]),
    "/learn/can-you-withdraw-from-a-hysa/": dict(
        tier="tier2", intent='informational',
        head=('can you withdraw from a high yield savings account', 200, 2, None),
        terms=[('can you take money out of high yield savings account', 150, 0, None),
               ('can you withdraw money from a high yield savings account', 150, 9, None),
               ('can you withdraw from high yield savings account', 80, 4, None),
               ('can you withdraw from hysa', 70, 6, None),
               ('can i withdraw from a high yield savings account', 60, 8, None),
               ('can you withdraw money from high yield savings account', 60, 1, None),
               ('can you take money out of a hysa', 60, 1, None),
               ('high yield savings account can you withdraw money', 50, 8, None),
               ('can you withdraw from a hysa', 50, 1, None)]),
    "/learn/hysa-vs-investing/": dict(
        tier="tier2", intent='commercial investigation',
        head=('hysa vs brokerage account', 150, 1, None),
        terms=[('brokerage account vs high yield savings', 150, 0, None),
               ('roth ira vs high yield savings account', 100, 0, None),
               ('money market fund vs hysa', 100, 0, None),
               ('high yield savings account vs 401k', 60, 0, None),
               ('high yield savings account vs brokerage account', 60, 8, None)]),
    "/learn/how-much-to-keep-in-a-hysa/": dict(
        tier="tier2", intent='informational',
        head=('how much to keep in hysa', 150, 1, None),
        terms=[('how many high yield savings accounts should i have', 100, 2, None)]),
    "/calculators/cd-ladder/": dict(
        tier="tier3", intent='utility',
        head=('how to cd ladder', 200, 8, None),
        terms=[('create a cd ladder', 150, 9, None),
               ('build a cd ladder', 150, 10, None),
               ('how to set up a cd ladder', 150, 6, None),
               ('what is a cd ladder strategy', 150, 0, None),
               ('short term cd ladder', 70, 0, None)]),
})
# Folded into existing pages (secondary terms, no new URL).
CLUSTERS["/"]["terms"] += [('interest calculator savings account', 600, 0, None), ('calculating interest on savings account', 100, 0, None), ('calculator high yield savings', 60, 0, None), ('how to calculate interest for savings account', 50, 0, None)]
CLUSTERS["/learn/hysa-vs-money-market/"]["terms"] += [('money market account vs high yield savings account', 1300, 0, None), ('money market vs hysa', 800, 0, None), ('mma vs high yield savings', 90, 0, None)]
CLUSTERS["/calculators/withdrawal/"]["terms"] += [('savings calculator with withdrawals', 350, 9, None), ('how long will savings last calculator', 150, 0, None)]
CLUSTERS["/calculators/apy-converter/"]["terms"] += [('effective interest rate calculator', 1300, 5, None), ('daily to annual interest rate calculator', 150, 0, None), ('interest yield calculator', 150, 0, None)]
CLUSTERS["/learn/what-is-apy/"]["terms"] += [('what is apy savings account', 1200, 0, None), ('what is the difference between apy and dividend rate', 100, 0, None)]
CLUSTERS["/learn/what-is-a-hysa/"]["terms"] += [('high yield savings account meaning', 800, 0, None), ('how does a high yield savings work', 600, 2, None), ('what is a hysa savings account', 250, 0, None), ('how do high interest savings accounts work', 200, 0, None)]

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
    "/calculators/cd-calculator/": "CD calculator",
    "/calculators/cd-ladder/": "CD ladder calculator",
    "/calculators/emergency-fund/": "Emergency fund calculator",
    "/calculators/simple-interest/": "Simple interest calculator",
    "/learn/how-money-market-accounts-work/": "How money market accounts work",
    "/learn/checking-vs-savings/": "Checking vs savings",
    "/learn/hysa-pros-and-cons/": "HYSA pros and cons",
    "/learn/can-you-withdraw-from-a-hysa/": "Can you withdraw from a HYSA?",
    "/learn/hysa-vs-investing/": "HYSA vs investing",
    "/learn/how-much-to-keep-in-a-hysa/": "How much to keep in a HYSA",
    "/rates/": "Savings rates chart",
}

LINKS = {
    "/": ["/calculators/cd-vs-hysa/", "/calculators/how-much-to-earn/",
          "/learn/what-is-apy/", "/learn/hysa-interest-tax/", "/methodology/", "/answers/"],
    "/calculators/": ["/", "/calculators/cd-vs-hysa/", "/calculators/how-much-to-earn/",
                      "/calculators/savings-goal/", "/calculators/withdrawal/",
                      "/calculators/apy-converter/"],
    "/calculators/how-much-to-earn/": ["/", "/learn/hysa-interest-tax/", "/answers/", "/calculators/"],
    "/calculators/cd-vs-hysa/": ["/", "/calculators/cd-calculator/", "/calculators/cd-ladder/", "/learn/hysa-vs-money-market/", "/calculators/"],
    "/calculators/savings-goal/": ["/", "/calculators/emergency-fund/", "/learn/how-hysa-compounding-works/", "/calculators/"],
    "/calculators/withdrawal/": ["/", "/learn/can-you-withdraw-from-a-hysa/", "/calculators/how-much-to-earn/", "/calculators/"],
    "/calculators/apy-converter/": ["/learn/apy-vs-interest-rate/", "/learn/apy-formula/", "/", "/calculators/"],
    "/learn/what-is-apy/": ["/", "/learn/apy-formula/", "/learn/apy-vs-interest-rate/",
                            "/learn/apr-vs-apy/", "/glossary/"],
    "/learn/apy-formula/": ["/learn/what-is-apy/", "/calculators/apy-converter/", "/methodology/", "/"],
    "/learn/apy-vs-interest-rate/": ["/learn/what-is-apy/", "/calculators/apy-converter/",
                                     "/learn/how-hysa-compounding-works/", "/"],
    "/learn/apr-vs-apy/": ["/learn/what-is-apy/", "/learn/apy-vs-interest-rate/", "/glossary/"],
    "/learn/what-is-a-hysa/": ["/", "/learn/hysa-vs-money-market/", "/learn/hysa-interest-tax/",
                               "/learn/what-is-apy/", "/learn/hysa-pros-and-cons/", "/rates/"],
    "/learn/hysa-vs-money-market/": ["/learn/what-is-a-hysa/", "/calculators/cd-vs-hysa/", "/glossary/"],
    "/learn/how-hysa-compounding-works/": ["/learn/what-is-apy/", "/", "/methodology/"],
    "/learn/hysa-interest-tax/": ["/", "/calculators/how-much-to-earn/", "/learn/what-is-a-hysa/"],
    "/glossary/": ["/", "/learn/what-is-apy/", "/methodology/"],
    "/methodology/": ["/", "/learn/apy-formula/", "/glossary/"],
    "/answers/": ["/", "/calculators/how-much-to-earn/", "/learn/what-is-apy/"],
    "/learn/": ["/", "/calculators/", "/glossary/", "/answers/", "/rates/"],
    "/calculators/cd-calculator/": ["/calculators/cd-vs-hysa/", "/calculators/cd-ladder/", "/rates/", "/"],
    "/calculators/cd-ladder/": ["/calculators/cd-calculator/", "/calculators/cd-vs-hysa/", "/rates/"],
    "/calculators/emergency-fund/": ["/learn/how-much-to-keep-in-a-hysa/", "/calculators/savings-goal/", "/", "/learn/can-you-withdraw-from-a-hysa/"],
    "/calculators/simple-interest/": ["/learn/how-hysa-compounding-works/", "/", "/learn/apy-formula/"],
    "/learn/how-money-market-accounts-work/": ["/learn/hysa-vs-money-market/", "/learn/checking-vs-savings/", "/rates/", "/"],
    "/learn/checking-vs-savings/": ["/learn/what-is-a-hysa/", "/learn/how-money-market-accounts-work/", "/calculators/emergency-fund/"],
    "/learn/hysa-pros-and-cons/": ["/learn/what-is-a-hysa/", "/learn/can-you-withdraw-from-a-hysa/", "/learn/hysa-interest-tax/", "/"],
    "/learn/can-you-withdraw-from-a-hysa/": ["/calculators/withdrawal/", "/learn/hysa-pros-and-cons/", "/learn/what-is-a-hysa/"],
    "/learn/hysa-vs-investing/": ["/learn/how-much-to-keep-in-a-hysa/", "/calculators/emergency-fund/", "/learn/hysa-vs-money-market/"],
    "/learn/how-much-to-keep-in-a-hysa/": ["/calculators/emergency-fund/", "/learn/hysa-vs-investing/", "/learn/hysa-pros-and-cons/"],
    "/rates/": ["/", "/calculators/cd-calculator/", "/learn/how-money-market-accounts-work/", "/learn/what-is-a-hysa/"],
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
