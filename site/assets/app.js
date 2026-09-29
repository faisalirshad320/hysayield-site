/* UI for every calculator on the site. Reads the page's data-tool, wires the
   inputs, renders results. All maths is in calc.js; nothing leaves the browser. */
(function () {
  "use strict";
  var C = window.HysaCalc;
  var tool = document.querySelector("[data-tool]");
  if (!C || !tool) return;
  var kind = tool.getAttribute("data-tool");
  var $ = function (id) { return document.getElementById(id); };
  var out = $("out"), err = $("err");

  var fmt0 = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  var fmt2 = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var money = function (x, dp) { return isFinite(x) ? (dp ? fmt2 : fmt0).format(x) : "—"; };
  // Round half-up on the decimal value. A bare toFixed() on 3.285 gives "3.28", because the
  // double is 3.28499999...; nudging by 1e-9 fixes that without moving any real value.
  var pct = function (x, dp) { dp = dp == null ? 2 : dp; var f = Math.pow(10, dp);
    return (Math.round((x * 100 + 1e-9) * f) / f).toFixed(dp) + "%"; };

  // Read a number field. Empty → fallback. Never lets NaN reach the maths.
  function num(id, fallback) {
    var el = $(id);
    if (!el) return fallback;
    var v = parseFloat(String(el.value).replace(/[, $%]/g, ""));
    return isFinite(v) ? v : fallback;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function stat(label, value) { return '<div class="stat"><b>' + value + "</b><span>" + esc(label) + "</span></div>"; }

  // --- share links: inputs round-trip through the query string ----------------
  var KEYS = { principal: "p", apy: "a", deposit: "d", years: "y", compounding: "c", fed: "f", state: "s",
               inflation: "i", target: "t", months: "m", cdapy: "cd", drift: "dr", penalty: "pen",
               goal: "g", withdrawal: "w", rate: "r", apyin: "ai", unit: "u", time: "tm", total: "tt",
               rungs: "n", step: "st", slope: "sl", housing: "h1", food: "h2", utilities: "h3", transport: "h4",
               insurance: "h5", debt: "h6", other: "h7", cover: "cv", current: "cu", contribution: "co" };
  (function loadFromUrl() {
    var q = new URLSearchParams(location.search);
    Object.keys(KEYS).forEach(function (id) {
      var el = $(id), v = q.get(KEYS[id]);
      if (el && v !== null && v !== "") el.value = v;
    });
    // Open the advanced panel if a shared link carries tax or inflation.
    if (q.get("f") || q.get("s") || q.get("i")) { var d = tool.querySelector("details.adv"); if (d) d.open = true; }
  })();
  function shareUrl() {
    var q = new URLSearchParams();
    Object.keys(KEYS).forEach(function (id) { var el = $(id); if (el && el.value !== "") q.set(KEYS[id], el.value); });
    return location.origin + location.pathname + "?" + q.toString();
  }

  // --- a small inline chart: balance vs contributions ---------------------------
  function chart(schedule, principal) {
    if (!schedule.length) return "";
    var W = 640, H = 200, P = 34;
    var maxV = schedule[schedule.length - 1].closing || 1;
    var n = schedule.length;
    var step = Math.max(1, Math.floor(n / 120));
    var pts = [[0, principal]], ctr = [[0, principal]];
    for (var i = step - 1; i < n; i += step) pts.push([i + 1, schedule[i].closing]), ctr.push([i + 1, schedule[i].contributed]);
    if (pts[pts.length - 1][0] !== n) { pts.push([n, schedule[n - 1].closing]); ctr.push([n, schedule[n - 1].contributed]); }
    var x = function (m) { return P + (W - P - 8) * (m / n); };
    var y = function (v) { return H - 22 - (H - 40) * (v / maxV); };
    var line = function (a) { return a.map(function (p, j) { return (j ? "L" : "M") + x(p[0]).toFixed(1) + " " + y(p[1]).toFixed(1); }).join(" "); };
    // Shade only the band between balance and contributions: that band IS the interest.
    var back = ctr.slice().reverse().map(function (p) { return "L" + x(p[0]).toFixed(1) + " " + y(p[1]).toFixed(1); }).join(" ");
    var area = line(pts) + " " + back + " Z";
    var yrs = n / 12;
    return '<div class="chart"><svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Balance growth: interest shown as the gap above your contributions">' +
      '<path d="' + area + '" fill="var(--accent)" opacity=".13"/>' +
      '<path d="' + line(ctr) + '" fill="none" stroke="var(--muted)" stroke-width="2" stroke-dasharray="5 4"/>' +
      '<path d="' + line(pts) + '" fill="none" stroke="var(--accent)" stroke-width="2.5"/>' +
      '<line x1="' + P + '" y1="' + (H - 22) + '" x2="' + (W - 8) + '" y2="' + (H - 22) + '" stroke="var(--line)"/>' +
      '<text x="' + P + '" y="' + (H - 6) + '" font-size="12" fill="var(--muted)">Now</text>' +
      '<text x="' + (W - 8) + '" y="' + (H - 6) + '" font-size="12" fill="var(--muted)" text-anchor="end">' + (yrs % 1 ? yrs.toFixed(1) : yrs) + (yrs === 1 ? " year" : " years") + "</text>" +
      '<text x="' + (W - 8) + '" y="' + (y(maxV) - 6).toFixed(0) + '" font-size="12" fill="var(--accent)" text-anchor="end" font-weight="700">' + money(maxV) + "</text>" +
      "</svg><p class=\"hint\">Solid line: balance. Dashed: what you put in. The shaded gap is interest.</p></div>";
  }

  var lastSchedule = null;

  // --- the six tools ------------------------------------------------------------
  var render = {
    main: function () {
      var years = num("years", 5);
      var apyPct = num("apy", 4.5);
      var o = {
        principal: Math.max(0, num("principal", 0)), apy: apyPct / 100,
        compounding: $("compounding").value, monthlyDeposit: Math.max(0, num("deposit", 0)),
        months: Math.round(Math.max(1 / 12, Math.min(50, years)) * 12),
        fedRate: Math.max(0, num("fed", 0)) / 100, stateRate: Math.max(0, num("state", 0)) / 100,
        inflation: Math.max(0, num("inflation", 0)) / 100
      };
      var warn = [];
      if (apyPct > 20) warn.push("That APY is far above any current savings rate — check the figure.");
      if (apyPct < 0) warn.push("APY can't be negative; treated as 0%.");
      if (o.apy < 0) o.apy = 0;
      err.textContent = warn.join(" ");

      var r = C.project(o);
      lastSchedule = r.schedule;
      var hasTax = o.fedRate + o.stateRate > 0, hasInfl = o.inflation > 0;
      var yrs = o.months / 12;
      var h = '<p class="big">' + money(r.finalBalance) + '</p><p class="biglab">after ' +
        (yrs % 1 ? yrs.toFixed(1) : yrs) + (yrs === 1 ? " year" : " years") + " at " + pct(o.apy) + " APY</p>";
      h += '<div class="stats">' + stat("Interest earned", money(r.interest, true)) + stat("You put in", money(r.contributed));
      if (hasTax) h += stat("Interest after tax", money(r.afterTaxInterest, true));
      // Real value of what you actually keep: the after-tax balance, deflated.
      if (hasInfl) h += stat(hasTax ? "After-tax balance, in today's dollars" : "Balance in today's dollars", money((hasTax ? r.afterTaxBalance : r.finalBalance) / Math.pow(1 + o.inflation, yrs)));
      h += stat("First month's interest", money(r.schedule[0] ? r.schedule[0].interest : 0, true)) + "</div>";
      // Tax is proportional to interest, so the after-tax yield is exactly APY x (1 - tax rate).
      if (hasTax) h += '<p class="verdict">Tax takes ' + money(r.tax, true) + ". After tax, " + pct(o.apy) +
        " APY is really " + pct(o.apy * (1 - r.taxRate)) + (hasInfl ? ", and about " + pct((1 + o.apy * (1 - r.taxRate)) / (1 + o.inflation) - 1) + " after inflation" : "") + ".</p>";
      h += chart(r.schedule, o.principal);
      h += scheduleTable(r.schedule);
      out.innerHTML = h;
    },

    reverse: function () {
      var target = Math.max(0, num("target", 1000)), apy = Math.max(0, num("apy", 4.5)) / 100;
      var fed = Math.max(0, num("fed", 0)) / 100, st = Math.max(0, num("state", 0)) / 100;
      if (apy <= 0) { err.textContent = "Enter an APY above zero."; out.innerHTML = ""; return; }
      err.textContent = "";
      var gross = C.balanceForMonthlyIncome(target, apy);
      var net = C.balanceForMonthlyIncome(target, apy, { fedRate: fed, stateRate: st, afterTax: true });
      var h = '<p class="big">' + money(fed + st > 0 ? net : gross) + '</p><p class="biglab">needed to earn ' +
        money(target) + " a month" + (fed + st > 0 ? " after tax" : "") + " at " + pct(apy) + " APY</p>";
      h += '<div class="stats">' + stat("Before tax", money(gross));
      if (fed + st > 0) h += stat("To keep " + money(target) + " after tax", money(net));
      h += stat("Yearly interest", money(target * 12)) + "</div>";
      h += '<p class="verdict">If the rate fell to ' + pct(Math.max(0, apy - 0.015)) + ", the same " + money(fed + st > 0 ? net : gross) +
        " would pay about " + money((fed + st > 0 ? net : gross) * (Math.pow(1 + Math.max(0, apy - 0.015), 1 / 12) - 1) * (1 - (fed + st))) + " a month.</p>";
      out.innerHTML = h;
    },

    cd: function () {
      var o = {
        principal: Math.max(0, num("principal", 25000)), months: Math.max(1, Math.round(num("months", 24))),
        cdApy: Math.max(0, num("cdapy", 4.7)) / 100, apy: Math.max(0, num("apy", 4.5)) / 100,
        hysaDrift: num("drift", 0) / 100, penaltyMonths: Math.max(0, num("penalty", 0))
      };
      err.textContent = "";
      var r = C.compareCd(o);
      var winner = r.winner === "cd" ? "The CD" : r.winner === "hysa" ? "The savings account" : "Neither";
      var h = '<p class="big">' + (r.winner === "tie" ? "A tie" : winner + " wins") + '</p><p class="biglab">' +
        (r.winner === "tie" ? "both earn " + money(r.cdInterest, true) : "by " + money(Math.abs(r.difference), true)) +
        " over " + o.months + " months</p>";
      h += '<div class="stats">' + stat("CD interest", money(r.cdInterest, true)) + stat("Savings interest", money(r.hysaInterest, true)) +
        stat("Break-even savings APY", pct(r.breakEvenApy)) + stat("Penalty if CD broken early", money(r.cdEarlyPenalty, true)) + "</div>";
      var edge = r.cdEarlyPenalty > Math.max(0, r.difference);
      h += '<p class="verdict">' + (r.winner === "cd" && edge
        ? "The CD's advantage is smaller than its early-withdrawal penalty. If there is any real chance you'll need the money before " + o.months + " months, the savings account is the safer choice."
        : r.winner === "cd"
          ? "The CD comes out ahead as long as you hold it to maturity and savings rates average below " + pct(r.breakEvenApy) + "."
          : "The savings account comes out ahead and keeps your money available. The CD would need to pay above " + pct(o.apy) + " — or savings rates would need to fall faster — to win.") + "</p>";
      out.innerHTML = h;
    },

    goal: function () {
      var goal = Math.max(1, num("goal", 20000));
      var o = { principal: Math.max(0, num("principal", 0)), apy: Math.max(0, num("apy", 4.5)) / 100,
                compounding: "daily", monthlyDeposit: Math.max(0, num("deposit", 0)) };
      err.textContent = "";
      var m = C.monthsToGoal(goal, o);
      if (m === null) { out.innerHTML = '<p class="verdict">With no monthly deposit this goal is never reached at that rate. Add a deposit or raise the starting balance.</p>'; return; }
      if (m === 0) { out.innerHTML = '<p class="verdict">You are already there — your starting balance meets the goal.</p>'; return; }
      var r = C.project(Object.assign({ months: m }, o));
      var when = new Date(); when.setMonth(when.getMonth() + m);
      var h = '<p class="big">' + (m >= 12 ? (m / 12).toFixed(1) + " years" : m + (m === 1 ? " month" : " months")) +
        '</p><p class="biglab">to reach ' + money(goal) + " — around " + when.toLocaleDateString("en-US", { month: "long", year: "numeric" }) + "</p>";
      h += '<div class="stats">' + stat("You put in", money(r.contributed)) + stat("Interest does", money(r.interest)) +
        stat("Share from interest", pct(r.interest / r.finalBalance, 1)) + "</div>";
      out.innerHTML = h;
    },

    withdraw: function () {
      var o = { principal: Math.max(0, num("principal", 100000)), apy: Math.max(0, num("apy", 4.5)) / 100,
                compounding: $("compounding").value, monthlyWithdrawal: Math.max(0, num("withdrawal", 1000)) };
      err.textContent = "";
      var sustain = o.principal * (Math.pow(1 + o.apy, 1 / 12) - 1);
      var m = C.withdrawalMonths(o);
      var h;
      if (m === null) {
        h = '<p class="big">Indefinitely</p><p class="biglab">interest covers the withdrawal</p>';
      } else {
        h = '<p class="big">' + (m >= 12 ? (m / 12).toFixed(1) + " years" : m + " months") + '</p><p class="biglab">until the balance runs out</p>';
      }
      h += '<div class="stats">' + stat("Withdrawal the interest alone covers", money(sustain, true) + "/mo") +
        stat("Total withdrawn", m === null ? "—" : money(o.monthlyWithdrawal * m)) + "</div>";
      out.innerHTML = h;
    },

    convert: function (source) {
      var n = C.PERIODS[$("compounding").value];
      if (source === "apyin") {
        var a = num("apyin", 4.5) / 100;
        $("rate").value = (C.nominalFromApy(a, n) * 100).toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
      } else {
        var rt = num("rate", 4.4) / 100;
        $("apyin").value = (C.apyFromNominal(rt, n) * 100).toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
      }
      var rate = num("rate", 0) / 100, apy = num("apyin", 0) / 100;
      err.textContent = "";
      out.innerHTML = '<p class="big">' + pct(apy, 3) + '</p><p class="biglab">APY from a ' + pct(rate, 3) + " rate compounded " +
        $("compounding").value + "</p><div class=\"stats\">" + stat("Difference", ((apy - rate) * 10000).toFixed(1) + " basis points") +
        stat("On $10,000 in a year", money(10000 * apy, true)) + "</div>";
    }
  };

  // --- the four low-fruit tools ------------------------------------------------
  render.cdcalc = function () {
    var o = { principal: Math.max(0, num("principal", 10000)), apy: Math.max(0, num("apy", 4.2)) / 100,
              months: Math.max(1, Math.round(num("months", 12))), compounding: $("compounding").value,
              penaltyMonths: Math.max(0, num("penalty", 3)),
              fedRate: Math.max(0, num("fed", 0)) / 100, stateRate: Math.max(0, num("state", 0)) / 100 };
    var apyPct = num("apy", 4.2);
    err.textContent = apyPct > 15 ? "That APY is far above any current CD rate — check the figure." : "";
    var r = C.cd(o);
    var nat = window.HYSA_NAT, natLine = "";
    if (nat) {
      var terms = [1, 3, 6, 12, 24, 36, 48, 60], k = terms.reduce(function (b, t) { return Math.abs(t - o.months) < Math.abs(b - o.months) ? t : b; }, 12);
      var nr = nat["cd_" + k + "m"];
      if (nr != null) natLine = '<p class="verdict">The FDIC national average for a ' + k + "-month CD is " + nr.toFixed(2) +
        "%. " + (o.apy * 100 > nr ? "Your rate beats it by " + (o.apy * 100 - nr).toFixed(2) + " points." : "Your rate is below it — shop around.") + "</p>";
    }
    var h = '<p class="big">' + money(r.maturity, true) + '</p><p class="biglab">at maturity, after ' + o.months + " months at " + pct(o.apy) + " APY</p>";
    h += '<div class="stats">' + stat("Interest earned", money(r.interest, true));
    if (o.fedRate + o.stateRate > 0) h += stat("Interest after tax", money(r.afterTaxInterest, true));
    h += stat("Early-withdrawal penalty", money(r.penalty, true)) +
      stat("Break-even month", r.breakEvenMonth ? "Month " + r.breakEvenMonth : "—") + "</div>";
    h += '<p class="verdict">' + (o.penaltyMonths <= 0 ? "No early-withdrawal penalty entered."
      : r.breakEvenMonth === null ? "The penalty is larger than <b>all</b> the interest this CD earns over its term — breaking it at any point returns less than you deposited."
      : r.breakEvenMonth === 1 ? "Even broken in the first month, the interest covers the penalty."
      : "Break this CD before month " + r.breakEvenMonth + " and you get back <b>less than you deposited</b> — the penalty is larger than the interest earned by then.") + "</p>" + natLine;
    var rows = r.early.filter(function (x, i) { return i < 3 || (i + 1) % 3 === 0 || i === r.early.length - 1; })
      .map(function (x) { return "<tr><td>Month " + x.month + '</td><td class="n">' + money(x.interest, true) + '</td><td class="n">' + money(x.walkAway, true) + "</td></tr>"; }).join("");
    h += '<details class="adv"><summary>If you broke it early</summary><div class="tw"><table><thead><tr><th>Broken at</th><th class="n">Interest so far</th><th class="n">You walk away with</th></tr></thead><tbody>' + rows + "</tbody></table></div></details>";
    out.innerHTML = h;
  };

  render.simple = function () {
    var P = Math.max(0, num("principal", 10000)), rate = Math.max(0, num("rate", 5)) / 100;
    var unit = $("unit").value, t = Math.max(0, num("time", 3)), years = unit === "months" ? t / 12 : unit === "days" ? t / 365 : t;
    err.textContent = "";
    var si = C.simpleInterest(P, rate, years), ca = C.compoundOnNominal(P, rate, 1, years), cd = C.compoundOnNominal(P, rate, 365, years);
    var h = '<p class="big">' + money(si.interest, true) + '</p><p class="biglab">simple interest on ' + money(P) + " at " + pct(rate) + " for " + t + " " + unit + "</p>";
    h += '<div class="stats">' + stat("Total (principal + interest)", money(si.total, true)) + stat("Per year", money(P * rate, true)) +
      stat("Compounded yearly instead", money(ca.interest, true)) + stat("Compounded daily instead", money(cd.interest, true)) + "</div>";
    h += '<p class="verdict">Formula: I = P × r × t = ' + money(P) + " × " + (rate).toFixed(4).replace(/0+$/, "").replace(/\.$/, "") + " × " + (Math.round(years * 10000) / 10000) +
      " = " + money(si.interest, true) + ". Compounding would add " + money(cd.interest - si.interest, true) + " over the same period.</p>";
    out.innerHTML = h;
  };

  render.ladder = function () {
    var total = Math.max(0, num("total", 20000)), n = Math.max(2, Math.min(10, Math.round(num("rungs", 5))));
    var step = Math.max(1, Math.round(num("step", 12))), base = Math.max(0, num("apy", 4)) / 100, slope = num("slope", -0.1) / 100;
    err.textContent = "";
    var rungs = [];
    for (var i = 1; i <= n; i++) rungs.push({ months: step * i, apy: Math.max(0, base + slope * (i - 1)) });
    var L = C.ladder(total, rungs);
    var h = '<p class="big">' + money(L.totalInterest) + '</p><p class="biglab">interest across ' + n + " rungs of " + money(L.share) + " — a rung matures every " + step + " months</p>";
    h += '<div class="stats">' + stat("Blended APY", pct(L.blendedApy)) + stat("First cash available", "Month " + L.firstAccessMonths) + stat("Longest rung", rungs[n - 1].months + " months") + "</div>";
    h += '<div class="tw" style="margin-top:14px"><table><thead><tr><th>Rung</th><th class="n">Term</th><th class="n">APY</th><th class="n">Matures at</th><th class="n">Interest</th></tr></thead><tbody>' +
      L.rungs.map(function (r, j) { return "<tr><td>" + (j + 1) + '</td><td class="n">' + r.months + ' mo</td><td class="n">' + pct(r.apy) + '</td><td class="n">' + money(r.maturity, true) + '</td><td class="n">' + money(r.interest, true) + "</td></tr>"; }).join("") +
      "</tbody></table></div>";
    h += '<p class="verdict">When each rung matures, reinvest it in a new ' + (step * n) + "-month CD. After one full cycle every rung earns the long-term rate, and one still matures every " + step + " months.</p>";
    out.innerHTML = h;
  };

  render.ef = function () {
    var ids = ["housing", "food", "utilities", "transport", "insurance", "debt", "other"];
    var o = { expenses: ids.map(function (id) { return Math.max(0, num(id, 0)); }), months: Math.max(1, num("cover", 6)),
              current: Math.max(0, num("current", 0)), monthlyContribution: Math.max(0, num("contribution", 0)),
              apy: Math.max(0, num("apy", 4)) / 100 };
    err.textContent = "";
    var e = C.emergencyFund(o);
    if (e.monthlyExpenses <= 0) { out.innerHTML = '<p class="verdict">Enter your essential monthly costs above.</p>'; return; }
    var h = '<p class="big">' + money(e.target) + '</p><p class="biglab">' + o.months + " months of essential costs (" + money(e.monthlyExpenses) + "/month)</p>";
    h += '<div class="stats">' + stat("You have now", money(e.current)) + stat("Still to save", money(e.gap)) +
      stat("Months covered today", e.coverageNow.toFixed(1)) + stat("Interest a year at target", money(e.yearlyInterestAtTarget)) + "</div>";
    var when = "";
    if (e.gap <= 0) when = "You're fully funded. Anything above the target could be working harder elsewhere.";
    else if (e.monthsToTarget === null) when = "Add a monthly contribution to see when you'll get there.";
    else { var d = new Date(); d.setMonth(d.getMonth() + e.monthsToTarget);
      when = "At " + money(o.monthlyContribution) + " a month you'll be fully funded in <b>" + e.monthsToTarget + " months</b> — around " + d.toLocaleDateString("en-US", { month: "long", year: "numeric" }) + "."; }
    h += '<p class="verdict">' + when + "</p>";
    out.innerHTML = h;
  };

  function scheduleTable(s) {
    if (!s.length) return "";
    var rows = "", step = s.length > 60 ? 12 : 1;
    for (var i = step - 1; i < s.length; i += step) {
      var x = s[i];
      rows += "<tr><td>" + (step === 12 ? "Year " + x.month / 12 : "Month " + x.month) + '</td><td class="n">' +
        money(x.deposit * (step === 12 ? 12 : 1)) + '</td><td class="n">' + money(step === 12 ? sumInterest(s, i - 11, i) : x.interest, true) +
        '</td><td class="n">' + money(x.closing, true) + "</td></tr>";
    }
    return '<details class="adv"><summary>' + (step === 12 ? "Year-by-year" : "Month-by-month") + " schedule</summary>" +
      '<div class="tw"><table><thead><tr><th>' + (step === 12 ? "Year" : "Month") + '</th><th class="n">Deposits</th><th class="n">Interest</th><th class="n">Balance</th></tr></thead><tbody>' +
      rows + "</tbody></table></div></details>";
  }
  function sumInterest(s, a, b) { var t = 0; for (var i = Math.max(0, a); i <= b; i++) t += s[i].interest; return t; }

  // --- wiring -------------------------------------------------------------------
  var fn = render[kind];
  var timer;
  function run(ev) {
    clearTimeout(timer);
    var src = ev && ev.target && ev.target.id;
    timer = setTimeout(function () { try { fn(src); } catch (e) { err.textContent = "Something in those numbers couldn't be calculated. Check the fields."; } }, 60);
  }
  tool.addEventListener("input", run);
  tool.addEventListener("change", run);

  var csv = $("csv"), share = $("share");
  if (csv) csv.addEventListener("click", function () {
    if (!lastSchedule) return;
    var lines = ["month,deposit,interest,balance,total_contributed"];
    lastSchedule.forEach(function (x) { lines.push([x.month, x.deposit.toFixed(2), x.interest.toFixed(2), x.closing.toFixed(2), x.contributed.toFixed(2)].join(",")); });
    var blob = new Blob([lines.join("\n")], { type: "text/csv" });
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "hysa-schedule.csv";
    document.body.appendChild(a); a.click(); a.remove();
  });
  if (share) share.addEventListener("click", function () {
    var u = shareUrl();
    var done = function () { share.textContent = "Link copied"; setTimeout(function () { share.textContent = "Copy link to these numbers"; }, 2000); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(done, function () { prompt("Copy this link:", u); });
    else { history.replaceState(null, "", u); share.textContent = "Link is in the address bar"; }
  });

  fn(kind === "convert" ? "rate" : undefined);
})();
