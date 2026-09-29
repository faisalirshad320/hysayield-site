// Cross-checks site/assets/calc.js against build/reference.py over the shared
// input sweep. Two independent implementations (iterative vs closed-form).
// Run: node build/parity.js
const M = require("../site/assets/calc.js");
const cases = require("./sweep.json");

let worstAbs = 0, worstRel = 0, worstCase = null, checked = 0;

for (const c of cases) {
  const [principal, apy, compounding, monthlyDeposit, months] = c.in;
  const r = M.project({
    principal, apy, compounding, monthlyDeposit, months,
    fedRate: 0.24, stateRate: 0.05, inflation: 0.03
  });
  for (const key of ["finalBalance", "interest", "afterTaxBalance", "realBalance"]) {
    const got = r[key], want = c[key];
    const abs = Math.abs(got - want);
    const rel = Math.abs(want) > 1 ? abs / Math.abs(want) : abs;
    checked++;
    if (rel > worstRel) { worstRel = rel; worstAbs = abs; worstCase = { key, in: c.in, got, want }; }
  }
}

// Property checks the sweep does not cover.
const props = [];
function prop(name, got, want, tol) {
  const ok = Math.abs(got - want) <= tol;
  props.push((ok ? "ok   " : "FAIL ") + name + `  got ${got.toFixed(6)} want ${want.toFixed(6)}`);
  return ok;
}
let allProps = true;
// APY invariance in JS too.
for (const comp of ["daily", "monthly", "quarterly", "annually"]) {
  allProps &= prop(`APY invariance (${comp})`,
    M.project({ principal: 10000, apy: 0.05, compounding: comp, monthlyDeposit: 0, months: 12 }).finalBalance,
    10500, 0.02);
}
// nominal <-> APY round trip
allProps &= prop("nominal→APY→nominal", M.nominalFromApy(M.apyFromNominal(0.0425, 365), 365), 0.0425, 1e-12);
// reverse solver
allProps &= prop("balance for $1000/mo @4.5%",
  M.balanceForMonthlyIncome(1000, 0.045) * (Math.pow(1.045, 1 / 12) - 1), 1000, 1e-6);
// after-tax reverse solver needs a bigger balance
const gross = M.balanceForMonthlyIncome(1000, 0.045, { fedRate: 0.24, stateRate: 0.05, afterTax: true });
allProps &= prop("after-tax solver nets $1000",
  gross * (Math.pow(1.045, 1 / 12) - 1) * (1 - 0.29), 1000, 1e-6);
// goal solver agrees with the projection
const g = M.monthsToGoal(20000, { principal: 5000, apy: 0.045, compounding: "daily", monthlyDeposit: 400 });
const atGoal = M.project({ principal: 5000, apy: 0.045, compounding: "daily", monthlyDeposit: 400, months: g });
allProps &= prop("monthsToGoal reaches goal", atGoal.finalBalance >= 20000 ? 1 : 0, 1, 0);
const before = M.project({ principal: 5000, apy: 0.045, compounding: "daily", monthlyDeposit: 400, months: g - 1 });
allProps &= prop("monthsToGoal is the FIRST month", before.finalBalance < 20000 ? 1 : 0, 1, 0);
// schedule sums to the totals
const s = M.project({ principal: 1000, apy: 0.05, compounding: "monthly", monthlyDeposit: 250, months: 36 });
const schedInterest = s.schedule.reduce((a, x) => a + x.interest, 0);
allProps &= prop("schedule interest sums to total", schedInterest, s.interest, 1e-6);
allProps &= prop("closing = final", s.schedule[s.schedule.length - 1].closing, s.finalBalance, 1e-9);
// CD tie
const cd = M.compareCd({ principal: 10000, apy: 0.045, cdApy: 0.045, months: 24, penaltyMonths: 3 });
allProps &= prop("CD ties HYSA at equal rate", cd.difference, 0, 0.02);
allProps &= prop("CD break-even = CD APY", cd.breakEvenApy, 0.045, 1e-9);

// --- new tools: CD, simple interest, ladder, emergency fund -------------------
const s2 = require("./sweep2.json");
let n2 = 0, bad2 = [], worst2 = 0;
function cmp(name, got, want, tol) {
  n2++;
  if (want === null || got === null) { if (want !== got) bad2.push(`${name}: got ${got} want ${want}`); return; }
  const d = Math.abs(got - want) / Math.max(1, Math.abs(want));
  if (d > worst2) worst2 = d;
  if (d > tol) bad2.push(`${name}: got ${got} want ${want}`);
}
for (const c of s2.cd) {
  const [principal, apy, months, penaltyMonths, compounding] = c.in;
  const r = M.cd({ principal, apy, months, penaltyMonths, compounding });
  cmp(`cd maturity ${c.in}`, r.maturity, c.maturity, 1e-9);
  cmp(`cd penalty ${c.in}`, r.penalty, c.penalty, 1e-9);
  cmp(`cd breakEven ${c.in}`, r.breakEvenMonth, c.breakEvenMonth, 0);
}
for (const c of s2.simple) cmp(`simple ${c.in}`, M.simpleInterest(...c.in).interest, c.interest, 1e-12);
for (const c of s2.ladder) {
  const L = M.ladder(c.in[0], c.in[1].map(([months, apy]) => ({ months, apy })));
  cmp(`ladder interest ${c.in[0]}`, L.totalInterest, c.totalInterest, 1e-9);
  cmp(`ladder blended ${c.in[0]}`, L.blendedApy, c.blendedApy, 1e-12);
}
for (const c of s2.ef) {
  const [expenses, months, current, monthlyContribution, apy] = c.in;
  const e = M.emergencyFund({ expenses, months, current, monthlyContribution, apy });
  cmp(`ef target ${c.in}`, e.target, c.target, 1e-12);
  cmp(`ef gap ${c.in}`, e.gap, c.gap, 1e-12);
  cmp(`ef months ${JSON.stringify(c.in)}`, e.monthsToTarget, c.monthsToTarget, 0);
}
props.push((bad2.length ? "FAIL " : "ok   ") + `new tools: ${n2} checks, worst ${worst2.toExponential(2)}` +
  (bad2.length ? "\n  " + bad2.slice(0, 5).join("\n  ") : ""));
allProps &= !bad2.length;
checked += n2;

console.log(props.join("\n"));
console.log(`\nsweep: ${checked} comparisons over ${cases.length} cases`);
console.log(`worst relative difference: ${worstRel.toExponential(3)} (absolute ${worstAbs.toExponential(3)})`);
if (worstCase) console.log("worst case:", JSON.stringify(worstCase));

const pass = allProps && worstRel < 1e-9;
console.log("\nparity:", pass ? "PASS" : "FAIL");
process.exit(pass ? 0 : 1);
