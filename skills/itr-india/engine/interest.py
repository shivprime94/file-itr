from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from engine.buckets import Bucket, classify, effective_gain
from engine.model import (
    AdvanceTaxPayment, AgeBand, PresumptiveScheme, Taxpayer, VdaItem,
)
from engine.rates import TaxComputation
from engine.rulebase import RuleTable
from engine.scope import OutOfScopeError

_SPECIAL_CG = (Bucket.STCG_111A, Bucket.LTCG_112, Bucket.LTCG_112A, Bucket.VDA_115BBH)


@dataclass(frozen=True)
class InterestComputation:
    i234a: Decimal
    i234b: Decimal
    i234c: Decimal
    total: Decimal


def _round_down(amount: Decimal, multiple: int) -> Decimal:
    """Rule 119A: any fraction of the multiple is ignored."""
    return Decimal(max(int(amount) // multiple, 0) * multiple)


def _months_from_april(ay: int, until: date) -> int:
    """Months (part = full) from 1 Apr of the AY to `until` inclusive."""
    apr1 = date(ay - 1, 4, 1)
    if until < apr1:
        return 0
    return (until.year - apr1.year) * 12 + (until.month - 4) + 1


def _months_late(due: date, filed: date) -> int:
    m = (filed.year - due.year) * 12 + (filed.month - due.month)
    if filed.day > due.day:
        m += 1
    return max(m, 0)


def _instalment_due(fy_start: int, month: int, day: int) -> date:
    """Calendar date of an s.234C instalment within the FY beginning `fy_start`.

    Months Jan–Mar fall in the FY's closing calendar year (fy_start+1); Apr–Dec
    fall in the opening year. Shared by the schedule loop and first_due so
    presumptive March-only schedules do not land a year early.
    """
    return date(fy_start + 1 if month < 4 else fy_start, month, day)


def fy_bounds(ay: int) -> tuple[date, date]:
    """Previous year for AY `ay`: 1 Apr (ay-2) … 31 Mar (ay-1)."""
    return date(ay - 2, 4, 1), date(ay - 1, 3, 31)


def classify_payments(payments: list, ay: int) -> tuple[Decimal, list]:
    """Split challans into FY advance total and the post-FY list (SAT candidates).

    Payments dated before the FY start are ignored (wrong year) — they must not
    reduce 234A/B/C or inflate tax credits.
    """
    fy_lo, fy_hi = fy_bounds(ay)
    advance = Decimal("0")
    post_fy = []
    for p in payments:
        if fy_lo <= p.paid_on <= fy_hi:
            advance += p.amount
        elif p.paid_on > fy_hi:
            post_fy.append(p)
    return advance, post_fy


def tax_credits(tds: Decimal, payments: list, ay: int) -> Decimal:
    """TDS/TCS + challans dated on/after FY start (advance + self-assessment)."""
    fy_lo, _ = fy_bounds(ay)
    paid = sum((p.amount for p in payments if p.paid_on >= fy_lo), Decimal("0"))
    return max(tds, Decimal("0")) + paid


def compute_interest(tax: TaxComputation, tds: Decimal, payments: list,
                     taxpayer: Taxpayer, table: RuleTable, ay_ref_date: date,
                     items: list = (), self_assessment_date: date = None,
                     filing_date: date = None, due_date: date = None
                     ) -> InterestComputation:
    """Phase 4: s.234A/234B/234C interest on the Phase 3 tax figure.

    `tds` covers TDS/TCS credit; `payments` are challans — only those dated in
    the previous year count as advance tax; post-FY payments with
    `paid_on <= due_date` reduce the s.234A base (self-assessment). `items` are
    needed only for the s.234C capital-gains carve-out; without them, all
    income is treated as foreseeable from the first instalment (never
    understates interest).
    """
    if tds < 0:
        raise OutOfScopeError("tds/tcs credit cannot be negative")

    rate = table.get("interest.rate_pm", ay_ref_date).value
    m100 = table.get("rule119a.interest_base_round_down", ay_ref_date).value
    net = max(tax.total_tax - tds, Decimal("0"))
    fy_lo, fy_hi = fy_bounds(taxpayer.ay)
    advance_total, post_fy = classify_payments(payments, taxpayer.ay)

    # --- 234A: late filing ---
    i234a = Decimal("0")
    if filing_date is not None:
        if due_date is None:
            raise OutOfScopeError("s.234A needs both filing_date and due_date")
        if filing_date > due_date:
            # CIT v. Pranoy Roy (SC) / CBDT Circular 2/2015 — s.234A is not
            # chargeable on tax already paid by the due date, so post-FY
            # self-assessment paid on or before it reduces the base.
            table.get("s234a.sat_before_due_date_reduces_base", ay_ref_date)
            sat = sum((p.amount for p in post_fy if p.paid_on <= due_date),
                      Decimal("0"))
            base = _round_down(net - advance_total - sat, m100)
            i234a = base * rate * _months_late(due_date, filing_date)

    # --- advance-tax obligation gates (s.208 / s.207(2)) ---
    senior_exempt = (
        taxpayer.resident
        and taxpayer.age_band in (AgeBand.SENIOR, AgeBand.SUPER_SENIOR)
        and not taxpayer.has_pgbp_income
        and table.get("s207.senior_no_advance_tax", ay_ref_date).value)
    if net <= table.get("s208.advance_tax_threshold", ay_ref_date).value or senior_exempt:
        return InterestComputation(i234a, Decimal("0"), Decimal("0"), i234a)

    # --- 234B: advance tax below 90% of assessed tax ---
    i234b = Decimal("0")
    if advance_total < table.get("s234b.advance_shortfall_trigger", ay_ref_date).value * net:
        if self_assessment_date is None:
            raise OutOfScopeError(
                "s.234B runs from 1 Apr of the AY until the self-assessment payment — "
                "pass self_assessment_date")
        base = _round_down(net - advance_total, m100)
        i234b = base * rate * _months_from_april(taxpayer.ay, self_assessment_date)

    # --- 234C: instalment deferment, with the CG carve-out ---
    if tax.surcharge > 0:
        raise OutOfScopeError(
            "s.234C with surcharge: attributing surcharge across instalments is not "
            "statute-determined — out of scope")

    fy_start = taxpayer.ay - 2
    single_instalment = taxpayer.presumptive_scheme in (
        PresumptiveScheme.SECTION_44AD,
        PresumptiveScheme.SECTION_44ADA,
    )
    schedule_key = (
        "s234c.schedule_presumptive_44ad_44ada"
        if single_instalment else "s234c.schedule"
    )
    schedule = table.get(schedule_key, ay_ref_date).value
    first_due = _instalment_due(fy_start, schedule[0][0], schedule[0][1])
    last_due = _instalment_due(fy_start, schedule[-1][0], schedule[-1][1])
    mar31 = fy_hi  # 31 Mar of the FY
    cess = table.get("cess.health_education", ay_ref_date).value

    # Per-item tax attribution for the carve-out (proviso to s.234C(1)).
    carve_items = []   # (sale_date, attributed tax incl. cess)
    if table.get("s234c.cg_carveout", ay_ref_date).value and items:
        bucket_gains: dict = {}
        classified = []
        for it in items:
            b, _ = classify(it, table, ay_ref_date)
            if b in _SPECIAL_CG or b is Bucket.STCG_SLAB:
                gain = effective_gain(it, b, table, ay_ref_date)
                if gain < 0:
                    raise OutOfScopeError(
                        "s.234C quarterly attribution with a capital loss in the mix "
                        "is not statute-determined — out of scope")
                classified.append((b, it))
                bucket_gains[b] = bucket_gains.get(b, Decimal("0")) + gain
        for b, it in classified:
            sale = it.sale_date   # CapitalGainItem always has one; VdaItem may not
            if b is Bucket.VDA_115BBH and sale is None:
                raise OutOfScopeError(
                    "s.234C carve-out needs VdaItem.sale_date for quarterly accrual")
            if b is Bucket.STCG_SLAB:
                if sale > first_due:
                    raise OutOfScopeError(
                        "slab-rate STCG sold after the first instalment: its marginal-"
                        "rate attribution for s.234C is not statute-determined")
                continue
            share = effective_gain(it, b, table, ay_ref_date) / bucket_gains[b]
            attributed = tax.special_tax[b] * share * (1 + cess)
            carve_items.append((sale, attributed))

    i234c = Decimal("0")
    for month, day, cum, safe, nmonths in schedule:
        due = _instalment_due(fy_start, month, day)
        carved = sum((amt for sale, amt in carve_items if sale > due), Decimal("0"))
        annual = max(net - carved, Decimal("0"))
        # Only FY advance challans count toward instalment compliance.
        paid = sum((p.amount for p in payments
                    if fy_lo <= p.paid_on <= due), Decimal("0"))
        if safe and paid >= Decimal(safe) * annual:
            continue
        shortfall = Decimal(cum) * annual - paid
        if shortfall > 0:
            i234c += _round_down(shortfall, m100) * rate * nmonths

    # Proviso to s.234C(1): CG accruing after the last instalment is carved out
    # only if the tax on it is paid by 31 March. Otherwise charge 1% for one
    # month on the uncovered late-CG amount.
    late_cg = sum((amt for sale, amt in carve_items if sale > last_due), Decimal("0"))
    if late_cg > 0:
        paid_to_mar31 = sum((p.amount for p in payments
                             if fy_lo <= p.paid_on <= mar31), Decimal("0"))
        uncovered = min(late_cg, max(net - paid_to_mar31, Decimal("0")))
        if uncovered > 0:
            i234c += _round_down(uncovered, m100) * rate * 1

    return InterestComputation(i234a, i234b, i234c, i234a + i234b + i234c)
