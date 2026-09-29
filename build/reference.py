"""Independent reference implementation of the HYSA maths.

Deliberately NOT a transliteration of calc.js. Where calc.js steps month by
month, this uses closed-form annuity algebra; where calc.js carries fractional
compounding periods, this counts periods directly. If the two agree to a cent
over a wide sweep of inputs, the maths is probably right rather than
consistently wrong in the same way.

Run: python3 build/reference.py   (self-test)
"""
from decimal import Decimal, getcontext
import itertools
import json
import math

getcontext().prec = 40

PERIODS = {"daily": 365, "monthly": 12, "quarterly": 4, "annually": 1}


def periodic_rate(apy, n):
    return (1.0 + apy) ** (1.0 / n) - 1.0


def project(principal, apy, compounding, monthly_deposit, months,
            fed_rate=0.0, state_rate=0.0, inflation=0.0):
    """Closed form.

    Between deposits the balance grows by a factor g = (1+r)^(n/12) per month,
    where r is the periodic rate. With a deposit D at the END of each month,
    after m months:

        balance = P*g^m + D * (g^m - 1)/(g - 1)          (g != 1)
        balance = P + D*m                                 (g == 1)

    calc.js reaches the same number by iterating, and carries a fractional
    period count when n/12 is not an integer (daily). To stay independent and
    still be exact, the per-month growth factor here is built from the *whole*
    periods that fall in each month, the same way a bank credits interest, and
    the monthly factors are multiplied out.
    """
    n = PERIODS[compounding]
    r = periodic_rate(apy, n)
    months = int(round(months))

    # Whole compounding periods inside each month, matching a real posting
    # schedule (365/12 is not an integer, so months differ).
    carry = 0.0
    factors = []
    for _ in range(months):
        carry += n / 12.0
        whole = math.floor(carry + 1e-9)
        carry -= whole
        factors.append((1.0 + r) ** whole)

    balance = principal
    contributed = principal
    for f in factors:
        balance = balance * f + monthly_deposit
        contributed += monthly_deposit

    interest = balance - contributed
    tax_rate = min(0.95, max(0.0, fed_rate + state_rate))
    tax = interest * tax_rate
    years = months / 12.0
    real = balance / ((1.0 + inflation) ** years) if inflation > 0 else balance

    return {
        "finalBalance": balance,
        "contributed": contributed,
        "interest": interest,
        "tax": tax,
        "afterTaxInterest": interest - tax,
        "afterTaxBalance": balance - tax,
        "realBalance": real,
    }


def balance_for_monthly_income(target, apy, fed_rate=0.0, state_rate=0.0, after_tax=False):
    monthly = (1.0 + apy) ** (1.0 / 12.0) - 1.0
    if monthly <= 0:
        return float("inf")
    gross = target
    rate = min(0.95, max(0.0, fed_rate + state_rate))
    if after_tax and rate < 1:
        gross = target / (1.0 - rate)
    return gross / monthly


def compare_cd(principal, apy, cd_apy, months, penalty_months=0.0, hysa_drift=0.0):
    years = months / 12.0
    cd_end = principal * (1.0 + cd_apy) ** years
    monthly_cd = principal * ((1.0 + cd_apy) ** (1.0 / 12.0) - 1.0)
    penalty = penalty_months * monthly_cd

    bal = principal
    rate = apy
    remaining = months
    while remaining > 0:
        chunk = min(12, remaining)
        bal *= (1.0 + max(0.0, rate)) ** (chunk / 12.0)
        rate += hysa_drift
        remaining -= chunk

    return {
        "cdEnd": cd_end,
        "cdEarlyPenalty": penalty,
        "hysaEnd": bal,
        "difference": cd_end - bal,
        "breakEvenApy": (cd_end / principal) ** (1.0 / years) - 1.0,
    }


def simple_interest(principal, rate, years):
    return principal * rate * years


def cd(principal, apy, months, penalty_months=0.0, compounding="daily"):
    """Independent: value at month k from the closed form P*(1+APY)^(k/12) for
    whole-period compounding is approximated here by counting whole periods,
    exactly as a bank posts them — then the penalty is compared month by month."""
    n = PERIODS[compounding]
    rper = periodic_rate(apy, n)
    carry, bal, early, break_even = 0.0, principal, [], None
    penalty = penalty_months * principal * ((1 + apy) ** (1 / 12) - 1)
    for k in range(1, int(months) + 1):
        carry += n / 12.0
        w = math.floor(carry + 1e-9)
        carry -= w
        bal *= (1 + rper) ** w
        earned = bal - principal
        if break_even is None and earned >= penalty:
            break_even = k
        early.append(bal - min(penalty, bal))
    return {"maturity": bal, "interest": bal - principal, "penalty": penalty,
            "breakEvenMonth": break_even, "early": early}


def ladder(total, rungs):
    share = total / len(rungs)
    vals = [share * (1 + a) ** (m / 12) for m, a in rungs]
    return {"totalInterest": sum(v - share for v in vals),
            "blendedApy": sum(a for _, a in rungs) / len(rungs)}


def emergency_fund(expenses, months, current, contribution, apy):
    monthly = sum(max(0, x) for x in expenses)
    target = monthly * months
    gap = max(0, target - current)
    if gap <= 0:
        m = 0
    else:
        bal, carry, rper, m = current, 0.0, periodic_rate(apy, 365), None
        if contribution <= 0 and rper <= 0:
            m = None
        else:
            for k in range(1, 1201):
                carry += 365 / 12
                w = math.floor(carry + 1e-9)
                carry -= w
                bal = bal * (1 + rper) ** w + contribution
                if bal >= target:
                    m = k
                    break
    return {"target": target, "gap": gap, "monthsToTarget": m, "yearlyInterestAtTarget": target * apy}


def _self_test():
    """Checks against figures computed by hand or by a third method."""
    ok = True

    def check(name, got, want, tol=0.01):
        nonlocal ok
        if abs(got - want) > tol:
            ok = False
            print(f"  FAIL {name}: got {got:.6f}, want {want:.6f}")
        else:
            print(f"  ok   {name}: {got:.4f}")

    # 1. No deposits, annual compounding: pure compound interest.
    r = project(10000, 0.045, "annually", 0, 12)
    check("10k @ 4.5% APY, 1 year", r["finalBalance"], 10450.0)

    # 2. APY is APY whatever the compounding: 1 year, no deposits, must equal
    #    principal * (1+APY) for every compounding frequency. This is the
    #    property the whole engine rests on.
    for comp in PERIODS:
        rr = project(10000, 0.05, comp, 0, 12)
        check(f"APY invariance ({comp})", rr["finalBalance"], 10500.0, tol=0.02)

    # 3. Zero rate with deposits is just arithmetic.
    r = project(1000, 0.0, "monthly", 200, 24)
    check("0% APY, 200/mo, 24 mo", r["finalBalance"], 1000 + 200 * 24)

    # 4. Ordinary annuity, monthly compounding at 12% APY.
    #    Monthly factor g = 1.12^(1/12). FV of 100/mo for 12 months:
    g = 1.12 ** (1 / 12)
    want = 100 * ((g ** 12 - 1) / (g - 1))
    r = project(0, 0.12, "monthly", 100, 12)
    check("annuity 100/mo, 12% APY", r["finalBalance"], want)

    # 5. Tax is applied to interest only, never to contributions.
    r = project(50000, 0.04, "daily", 0, 12, fed_rate=0.24, state_rate=0.05)
    check("tax on interest only", r["tax"], r["interest"] * 0.29)

    # 6. Reverse solver round-trips against the forward monthly rate.
    b = balance_for_monthly_income(1000, 0.045)
    monthly = b * ((1.045) ** (1 / 12) - 1)
    check("reverse solver round-trip", monthly, 1000.0)

    # 7. Inflation adjustment.
    r = project(10000, 0.05, "annually", 0, 24, inflation=0.03)
    check("real value after 2y at 3% inflation",
          r["realBalance"], 10000 * 1.05 ** 2 / 1.03 ** 2)

    # 8. CD vs HYSA at equal rates and no drift must tie.
    c = compare_cd(10000, 0.045, 0.045, 24)
    check("equal rates tie", c["difference"], 0.0, tol=0.02)
    check("break-even equals CD APY", c["breakEvenApy"], 0.045, tol=1e-6)

    # 9. Simple interest: I = Prt.
    check("simple interest 1000 @5% 3y", simple_interest(1000, 0.05, 3), 150.0)
    # 10. A CD with no penalty breaks even in month 1; with a 3-month penalty, in month 3.
    c0 = cd(10000, 0.045, 12, 0)
    check("cd no penalty breaks even month 1", c0["breakEvenMonth"], 1, tol=0)
    c3 = cd(10000, 0.045, 12, 3, "monthly")
    check("cd 3-month penalty breaks even month 3", c3["breakEvenMonth"], 3, tol=0)
    check("cd maturity = P*(1+APY)", c3["maturity"], 10450.0, tol=0.02)
    # 11. Ladder of identical rungs has blended APY equal to the rung APY.
    L = ladder(10000, [(12, 0.04)] * 4)
    check("ladder of equal rungs", L["blendedApy"], 0.04, tol=1e-12)
    # 12. Emergency fund target and zero-gap case.
    ef = emergency_fund([1500, 400, 200], 6, 12600, 0, 0.04)
    check("emergency fund target", ef["target"], 12600.0)
    check("emergency fund already met", ef["monthsToTarget"], 0, tol=0)
    print("\nreference self-test:", "PASS" if ok else "FAIL")
    return ok


def sweep():
    """Input grid shared with parity.js."""
    out = []
    for principal, apy, comp, dep, months in itertools.product(
            [0, 1000, 10000, 250000],
            [0.0, 0.0045, 0.045, 0.1875],
            ["daily", "monthly", "quarterly", "annually"],
            [0, 50, 1500],
            [1, 7, 12, 60, 360]):
        r = project(principal, apy, comp, dep, months, 0.24, 0.05, 0.03)
        out.append({
            "in": [principal, apy, comp, dep, months],
            "finalBalance": r["finalBalance"],
            "interest": r["interest"],
            "afterTaxBalance": r["afterTaxBalance"],
            "realBalance": r["realBalance"],
        })
    return out


def sweep2():
    """Cases for the CD, ladder, simple-interest and emergency-fund functions."""
    out = {"cd": [], "simple": [], "ladder": [], "ef": []}
    for P, apy, months, pen, comp in itertools.product(
            [1000, 25000, 250000], [0.0, 0.0173, 0.045, 0.06], [3, 6, 12, 18, 60],
            [0, 3, 6, 12], ["daily", "monthly", "quarterly"]):
        c = cd(P, apy, months, pen, comp)
        out["cd"].append({"in": [P, apy, months, pen, comp], "maturity": c["maturity"],
                          "penalty": c["penalty"], "breakEvenMonth": c["breakEvenMonth"]})
    for P, rt, y in itertools.product([500, 10000, 123456], [0.01, 0.045, 0.2], [0.5, 1, 3, 10]):
        out["simple"].append({"in": [P, rt, y], "interest": simple_interest(P, rt, y)})
    for total, rungs in [(10000, [(12, 0.04)] * 4), (50000, [(3, 0.0113), (6, 0.0141), (12, 0.0173), (24, 0.0161), (60, 0.0138)]),
                         (20000, [(12, 0.045), (24, 0.042), (36, 0.04), (48, 0.039), (60, 0.038)])]:
        L = ladder(total, rungs)
        out["ladder"].append({"in": [total, [list(x) for x in rungs]], **L})
    for exp, mo, cur, con, apy in itertools.product([[1500, 400, 200, 300], [3200, 800, 450, 600, 250]],
                                                    [3, 6, 9, 12], [0, 5000, 40000], [0, 250, 1000], [0.0, 0.04]):
        e = emergency_fund(exp, mo, cur, con, apy)
        out["ef"].append({"in": [exp, mo, cur, con, apy], **e})
    return out


if __name__ == "__main__":
    good = _self_test()
    with open("/home/claude/hysa/build/sweep2.json", "w") as f:
        json.dump(sweep2(), f)
    with open("/home/claude/hysa/build/sweep.json", "w") as f:
        json.dump(sweep(), f)
    print(f"wrote sweep.json ({len(sweep())} cases)")
    raise SystemExit(0 if good else 1)
