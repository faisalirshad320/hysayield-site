/* HYSA calculator engine. Pure functions, no DOM, no network.
   Every figure the site shows comes from here, and the same maths is
   reimplemented independently in build/reference.py and checked against
   this file by build/parity.js. See /methodology/ for the formulas. */
(function (root) {
  "use strict";

  var M = {};

  // Compounding periods per year. Banks quote APY, so the periodic rate is
  // derived from APY rather than from a nominal rate: this is what makes the
  // result match a real statement instead of being a few dollars out.
  M.PERIODS = { daily: 365, monthly: 12, quarterly: 4, annually: 1 };

  // Periodic rate from APY: (1 + APY)^(1/n) - 1.
  M.periodicRate = function (apy, n) {
    return Math.pow(1 + apy, 1 / n) - 1;
  };

  // Nominal annual rate (what a bank calls "interest rate") from APY.
  M.nominalFromApy = function (apy, n) {
    return n * M.periodicRate(apy, n);
  };

  // APY from a nominal annual rate compounded n times a year.
  M.apyFromNominal = function (nominal, n) {
    return Math.pow(1 + nominal / n, n) - 1;
  };

  /* Core projection.
     Deposits are made monthly, at the END of each month (ordinary annuity),
     which is how a standing transfer actually behaves. Interest compounds on
     its own schedule, which may be more frequent than the deposits, so the
     two are stepped independently rather than approximated.

     opts: { principal, apy, compounding, monthlyDeposit, months,
             fedRate, stateRate, inflation }
     Rates are decimals: 0.045 not 4.5. */
  M.project = function (o) {
    var n = M.PERIODS[o.compounding] || 12;
    var r = M.periodicRate(o.apy, n);
    var months = Math.max(0, Math.round(o.months));
    var dep = o.monthlyDeposit || 0;

    var balance = o.principal || 0;
    var contributed = o.principal || 0;
    var interestTotal = 0;
    var schedule = [];
    var carry = 0; // fractional compounding periods carried between months

    for (var m = 1; m <= months; m++) {
      // How many compounding periods fall inside this month.
      carry += n / 12;
      var whole = Math.floor(carry + 1e-9);
      carry -= whole;

      var opening = balance;
      for (var k = 0; k < whole; k++) {
        var interest = balance * r;
        balance += interest;
        interestTotal += interest;
      }
      balance += dep;
      contributed += dep;

      schedule.push({
        month: m,
        opening: opening,
        deposit: dep,
        interest: balance - opening - dep,
        closing: balance,
        contributed: contributed
      });
    }

    var taxRate = Math.min(0.95, Math.max(0, (o.fedRate || 0) + (o.stateRate || 0)));
    var tax = interestTotal * taxRate;
    var years = months / 12;
    var infl = o.inflation || 0;
    var real = infl > 0 ? balance / Math.pow(1 + infl, years) : balance;

    return {
      finalBalance: balance,
      contributed: contributed,
      interest: interestTotal,
      taxRate: taxRate,
      tax: tax,
      afterTaxInterest: interestTotal - tax,
      afterTaxBalance: balance - tax,
      realBalance: real,
      effectiveApy: o.apy,
      periodsPerYear: n,
      periodicRate: r,
      months: months,
      schedule: schedule
    };
  };

  /* Reverse solver: the balance needed to earn a target amount of interest
     per month, at a given APY. Closed form, no iteration.
     Monthly interest on a steady balance B is B * ((1+APY)^(1/12) - 1). */
  M.balanceForMonthlyIncome = function (target, apy, opts) {
    opts = opts || {};
    var monthlyRate = Math.pow(1 + apy, 1 / 12) - 1;
    if (monthlyRate <= 0) return Infinity;
    var gross = target;
    var taxRate = Math.min(0.95, Math.max(0, (opts.fedRate || 0) + (opts.stateRate || 0)));
    if (opts.afterTax && taxRate < 1) gross = target / (1 - taxRate);
    return gross / monthlyRate;
  };

  /* Months needed to reach a savings goal. Returns null if unreachable
     (no deposits and the goal is above the starting balance with 0% APY). */
  M.monthsToGoal = function (goal, o) {
    var n = M.PERIODS[o.compounding] || 12;
    var r = M.periodicRate(o.apy, n);
    var dep = o.monthlyDeposit || 0;
    var balance = o.principal || 0;
    if (balance >= goal) return 0;
    if (dep <= 0 && r <= 0) return null;
    var carry = 0;
    for (var m = 1; m <= 1200; m++) {
      carry += n / 12;
      var whole = Math.floor(carry + 1e-9);
      carry -= whole;
      for (var k = 0; k < whole; k++) balance += balance * r;
      balance += dep;
      if (balance >= goal) return m;
    }
    return null;
  };

  /* CD vs HYSA.
     A CD's rate is locked; a HYSA's floats and is assumed to drift by
     `hysaDrift` (decimal, annual, may be negative) applied per year.
     The CD is penalised `penaltyMonths` of interest if broken early.
     Returns both end values plus the HYSA rate at which they tie. */
  M.compareCd = function (o) {
    var months = Math.max(1, Math.round(o.months));
    var years = months / 12;

    // CD: simple locked compounding at its own APY, no deposits.
    var cdEnd = (o.principal || 0) * Math.pow(1 + o.cdApy, years);
    var cdInterest = cdEnd - (o.principal || 0);

    // Early withdrawal: penalty is quoted in months of interest.
    var monthlyCdInterest = (o.principal || 0) * (Math.pow(1 + o.cdApy, 1 / 12) - 1);
    var penalty = (o.penaltyMonths || 0) * monthlyCdInterest;

    // HYSA: drifting rate, stepped year by year.
    var bal = o.principal || 0;
    var rate = o.apy;
    var remaining = months;
    while (remaining > 0) {
      var chunk = Math.min(12, remaining);
      bal *= Math.pow(1 + Math.max(0, rate), chunk / 12);
      rate += (o.hysaDrift || 0);
      remaining -= chunk;
    }
    var hysaInterest = bal - (o.principal || 0);

    // Break-even: the flat HYSA APY that would match the CD over this term.
    var breakEvenApy = Math.pow(cdEnd / (o.principal || 1), 1 / years) - 1;

    return {
      months: months,
      cdEnd: cdEnd,
      cdInterest: cdInterest,
      cdEarlyPenalty: penalty,
      cdEndIfBrokenEarly: cdEnd - penalty,
      hysaEnd: bal,
      hysaInterest: hysaInterest,
      difference: cdEnd - bal,
      breakEvenApy: breakEvenApy,
      // Under half a cent apart is a tie; otherwise float noise would declare a winner "by $0.00".
      winner: Math.abs(cdEnd - bal) < 0.005 ? "tie" : (cdEnd > bal ? "cd" : "hysa")
    };
  };

  /* Steady drawdown: how long a balance lasts at a fixed monthly withdrawal,
     with interest still accruing. Returns months, or null if it never runs out. */
  M.withdrawalMonths = function (o) {
    var n = M.PERIODS[o.compounding] || 12;
    var r = M.periodicRate(o.apy, n);
    var bal = o.principal || 0;
    var w = o.monthlyWithdrawal || 0;
    if (w <= 0) return null;
    var carry = 0;
    for (var m = 1; m <= 1200; m++) {
      carry += n / 12;
      var whole = Math.floor(carry + 1e-9);
      carry -= whole;
      for (var k = 0; k < whole; k++) bal += bal * r;
      bal -= w;
      if (bal <= 0) return m;
    }
    return null; // interest covers the withdrawal indefinitely
  };

  if (typeof module !== "undefined" && module.exports) module.exports = M;
  else root.HysaCalc = M;
})(this);
