from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from engine.interest import InterestComputation, compute_interest, tax_credits
from engine.model import Taxpayer
from engine.rates import TaxComputation, compute_tax
from engine.rulebase import RuleTable
from engine.rules.ay2026_27 import TABLE as _TABLE_AY2026_27
from engine.scope import check_rate_scope, check_scope
from engine.setoff import SetOffResult, apply_setoff, trace_setoff
from engine.trace import Trace, trace_bucketing


@dataclass(frozen=True)
class Computation:
    setoff: SetOffResult
    tax: TaxComputation
    interest: Optional[InterestComputation]   # None when self_assessment_date not given
    trace: Trace                               # bucketing + set-off lines
    total_credits: Decimal                     # TDS/TCS + advance-tax payments
    total_payable: Decimal                     # max(tax + interest - credits, 0)
    refund_due: Decimal                        # max(credits - tax - interest, 0)


def compute(taxpayer: Taxpayer, items: list, *, bf_losses: list = (),
            normal_income: Decimal = Decimal("0"), tds: Decimal = Decimal("0"),
            advance_payments: list = (), self_assessment_date: date = None,
            filing_date: date = None, due_date: date = None,
            table: RuleTable = None, ay_ref_date: date = None) -> Computation:
    """One fail-loud pass: scope -> buckets -> set-off -> rates -> interest.

    Interest (234A/B/C) is computed only when `self_assessment_date` is given —
    without it the result's `interest` is None and `total_payable` is tax only.
    `normal_income` is the already-reconciled slab-rate income (salary after
    standard deduction, interest, dividends...); the engine does not rebuild it.
    `total_payable` is net of non-negative `tds` and the supplied advance-tax
    payments; an excess credit is exposed separately as `refund_due`.
    """
    table = table or _TABLE_AY2026_27
    # a date inside the relevant FY, so date-windowed rules resolve
    ay_ref_date = ay_ref_date or date(taxpayer.ay - 2, 6, 1)

    check_scope(taxpayer, items)
    check_rate_scope(taxpayer, items, table, ay_ref_date)

    setoff = apply_setoff(items, list(bf_losses), taxpayer, table, ay_ref_date,
                          normal_income=normal_income)
    tax = compute_tax(setoff.buckets, taxpayer, table, ay_ref_date)

    interest = None
    if self_assessment_date is not None:
        interest = compute_interest(
            tax, tds, list(advance_payments), taxpayer, table, ay_ref_date,
            items=items, self_assessment_date=self_assessment_date,
            filing_date=filing_date, due_date=due_date)

    trace = trace_bucketing(items, table, ay_ref_date)
    for line in trace_setoff(setoff, table, ay_ref_date).lines:
        trace.add(line)

    interest_total = interest.total if interest else Decimal("0")
    # Same payment window as interest: ignore pre-FY challans; count FY advance
    # and post-FY self-assessment toward credits.
    credits = tax_credits(tds, list(advance_payments), taxpayer.ay)
    net = tax.total_tax + interest_total - credits
    return Computation(setoff=setoff, tax=tax, interest=interest,
                       trace=trace, total_credits=credits,
                       total_payable=max(net, Decimal("0")),
                       refund_due=max(-net, Decimal("0")))


def render_report(c: Computation) -> str:
    """Human-readable audit of the whole computation, for portal verification."""
    out = ["== income lines =="]
    out.append(c.trace.render() or "(none)")
    if c.setoff.carry_forward:
        out.append("== carry-forward ==")
        for cf in c.setoff.carry_forward:
            cond = " (conditional on timely return)" if cf.conditional_on_timely_return else ""
            out.append(f"{cf.kind.value.upper()} of AY {cf.ay_incurred}: {cf.amount} "
                       f"usable through AY {cf.usable_through_ay}{cond}")
    if c.setoff.dead:
        out.append("== lapsed / disallowed losses ==")
        for d in c.setoff.dead:
            out.append(f"{d.label}: {d.amount} — {d.reason}")
    t = c.tax
    out.append("== tax ==")
    out.append(f"total income (288A): {t.total_income}")
    out.append(f"slab tax: {t.slab_tax}")
    for b, amt in t.special_tax.items():
        if amt:
            out.append(f"{b.value} tax: {amt} (on {t.special_taxable[b]})")
    if t.rebate_87a:
        out.append(f"87A rebate: -{t.rebate_87a}")
    if t.surcharge:
        out.append(f"surcharge: {t.surcharge}"
                   + (f" less marginal relief {t.marginal_relief}" if t.marginal_relief else ""))
    out.append(f"cess: {t.cess}")
    out.append(f"tax payable (288B): {t.total_tax}")
    if c.interest:
        i = c.interest
        out.append("== interest ==")
        out.append(f"234A: {i.i234a}  234B: {i.i234b}  234C: {i.i234c}")
    out.append(f"tax credits (TDS/TCS + advance tax): -{c.total_credits}")
    if c.refund_due:
        out.append(f"== REFUND DUE: {c.refund_due} ==")
    out.append(f"== TOTAL PAYABLE: {c.total_payable} ==")
    contested = c.trace.contested()
    if contested:
        out.append(f"({len(contested)} contested-rule line(s) above — review flagged items)")
    return "\n".join(out)
