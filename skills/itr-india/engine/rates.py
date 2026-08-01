from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from engine.buckets import Bucket
from engine.model import AgeBand, Regime, Taxpayer
from engine.rulebase import RuleTable
from engine.scope import OutOfScopeError

_CG_SPECIAL = (Bucket.STCG_111A, Bucket.LTCG_112, Bucket.LTCG_112A)
_SPECIAL = _CG_SPECIAL + (Bucket.VDA_115BBH,)

_OLD_SLAB_KEY = {
    AgeBand.BELOW_60: "slab.old_below60",
    AgeBand.SENIOR: "slab.old_senior",
    AgeBand.SUPER_SENIOR: "slab.old_super_senior",
}


@dataclass(frozen=True)
class TaxComputation:
    total_income: Decimal        # post-288A rounding
    slab_income: Decimal         # NORMAL + slab-rate STCG (post-rounding delta)
    special_taxable: dict        # bucket -> amount actually taxed at the special rate
    slab_tax: Decimal
    special_tax: dict            # bucket -> tax before rebate/surcharge/cess
    rebate_87a: Decimal
    surcharge: Decimal           # before marginal relief
    marginal_relief: Decimal     # surcharge marginal relief
    cess: Decimal
    total_tax: Decimal           # post-288B rounding


def _round_nearest(amount: Decimal, multiple: int) -> Decimal:
    """s.288A/288B rounding: ignore paise, then to the nearest `multiple`
    (last part >= multiple/2 rounds up)."""
    rupees = int(amount)  # amounts here are non-negative; truncation drops paise
    q, r = divmod(rupees, multiple)
    return Decimal(q * multiple + (multiple if r * 2 >= multiple else 0))


def _slab_tax(income: Decimal, slabs: list) -> Decimal:
    income = max(income, Decimal("0"))
    tax = Decimal("0")
    prev = Decimal("0")
    for upper, rate in slabs:
        if upper is None or income <= upper:
            return tax + (income - prev) * rate
        tax += (Decimal(upper) - prev) * rate
        prev = Decimal(upper)
    return tax


def _surcharge_rate(ti: Decimal, bands, regime: Regime, new_cap: Decimal) -> Decimal:
    for lower, upper, rate in bands:
        if ti > lower and (upper is None or ti <= upper):
            r = Decimal(rate)
            return min(r, new_cap) if regime is Regime.NEW else r
    return Decimal("0")


def _surcharge_on(tax_total: Decimal, cg_tax: Decimal, rate: Decimal,
                  cg_cap: Decimal) -> Decimal:
    if rate <= 0:
        return Decimal("0")
    return min(rate, cg_cap) * cg_tax + rate * (tax_total - cg_tax)


def compute_tax(buckets: dict, taxpayer: Taxpayer, table: RuleTable,
                ay_ref_date: date) -> TaxComputation:
    """Phase 3: rates, rebate, surcharge, cess, rounding on post-set-off buckets."""
    if any(v < 0 for v in buckets.values()):
        raise OutOfScopeError("negative bucket reached the rate layer — run set-off first")

    normal = buckets.get(Bucket.NORMAL, Decimal("0"))
    slab_st = buckets.get(Bucket.STCG_SLAB, Decimal("0"))
    raw = {b: buckets.get(b, Decimal("0")) for b in _SPECIAL}

    ti_raw = normal + slab_st + sum(raw.values())
    ti = _round_nearest(ti_raw, table.get("rounding.income_288a", ay_ref_date).value)
    # the (tiny, <= half-multiple) 288A rounding delta lands on the slab base
    slab_base = max(normal + slab_st + (ti - ti_raw), Decimal("0"))

    slab_key = "slab.new_regime" if taxpayer.regime is Regime.NEW \
        else _OLD_SLAB_KEY[taxpayer.age_band]
    slabs = [(u, Decimal(r)) for u, r in table.get(slab_key, ay_ref_date).value]
    # the 0%-rate first band IS the basic exemption limit
    exemption_limit = Decimal(slabs[0][0])
    assert slabs[0][1] == 0, "first slab band must be the nil band"

    taxable = dict(raw)
    taxable[Bucket.LTCG_112A] = max(
        taxable[Bucket.LTCG_112A] -
        table.get("exemption.ltcg_112a", ay_ref_date).value, Decimal("0"))

    # Residents set unexhausted basic exemption against 111A/112/112A — never
    # VDA (s.115BBH). VDA still *consumes* the exemption residual for the
    # purpose of measuring what remains: if VDA alone already fills total
    # income above the BEL, no 111A/112/112A relief remains. check_scope
    # already refuses non-residents in Phase 1, but guard anyway so the rule
    # stays load-bearing if that changes.
    if taxpayer.resident and table.get(
            "basic_exemption.adjust_against_special_cg", ay_ref_date).value:
        # Income that is taxed but cannot itself absorb BEL still counts toward
        # whether any BEL residual exists (VDA @ s.115BBH).
        bel_base = slab_base + raw[Bucket.VDA_115BBH]
        unexhausted = max(exemption_limit - bel_base, Decimal("0"))
        order = [Bucket(v) for v in
                 table.get("engine.basic_exemption_adjust_order", ay_ref_date).value]
        for b in order:
            if unexhausted <= 0:
                break
            take = min(unexhausted, taxable[b])
            taxable[b] -= take
            unexhausted -= take

    slab_tax = _slab_tax(slab_base, slabs)
    rates = {
        Bucket.STCG_111A: table.get("rate.stcg_111a", ay_ref_date).value,
        Bucket.LTCG_112: table.get("rate.ltcg_112", ay_ref_date).value,
        Bucket.LTCG_112A: table.get("rate.ltcg_112a", ay_ref_date).value,
        Bucket.VDA_115BBH: table.get("s115bbh.applies", ay_ref_date).value,
    }
    special_tax = {b: taxable[b] * rates[b] for b in _SPECIAL}

    # --- s.87A rebate ---
    rebate = Decimal("0")
    if taxpayer.regime is Regime.NEW:
        r87_new = table.get("rebate.87a_new", ay_ref_date).value

        def _new_regime_rebate(base: Decimal) -> Decimal:
            if base <= r87_new["threshold"]:
                return min(slab_tax, Decimal(r87_new["max"]))
            excess = base - r87_new["threshold"]
            return slab_tax - excess if slab_tax > excess else Decimal("0")

        # Finance Act 2025: 111A/112/112A income is out of s.87A's scope
        # entirely, so both the ₹12L threshold and marginal relief are tested
        # against slab_base (income excluding those special-rate buckets), not
        # ti (total income including them) — see rebate.87a_new's contested_note.
        rebate = _new_regime_rebate(slab_base)
        # The sources behind that exclusion address 111A/112/112A only, never
        # VDA (s.115BBH — a separate Chapter-XII regime). Whether VDA should
        # count toward the ₹12L test is this engine's own inference either
        # way, so only refuse where it actually matters: compare against the
        # answer if VDA *did* count, and fail loud only on disagreement —
        # matching results mean the VDA question doesn't change the outcome.
        vda_amt = raw[Bucket.VDA_115BBH]
        if vda_amt > 0 and _new_regime_rebate(slab_base + vda_amt) != rebate:
            raise OutOfScopeError(
                "new-regime 87A rebate depends on whether VDA income counts toward "
                "the ₹12L threshold/marginal-relief test, which is not source-"
                "confirmed here (sources cover 111A/112/112A only) — compute manually")
    else:
        r87_old = table.get("rebate.87a_old", ay_ref_date).value
        if ti <= r87_old["threshold"]:
            if any(v > 0 for v in special_tax.values()):
                raise OutOfScopeError(
                    "old-regime 87A with special-rate tax present is contested "
                    "(s.112A(6); utility behavior on 111A/VDA) — compute manually")
            rebate = min(slab_tax, Decimal(r87_old["max"]))

    tax_after_rebate = slab_tax + sum(special_tax.values()) - rebate

    # --- surcharge, with 15% CG cap and marginal relief ---
    bands = table.get("surcharge.bands", ay_ref_date).value
    new_cap = table.get("surcharge.new_regime_cap", ay_ref_date).value
    cg_cap = table.get("surcharge.cg_dividend_cap", ay_ref_date).value
    cg_tax = sum(special_tax[b] for b in _CG_SPECIAL)
    rate = _surcharge_rate(ti, bands, taxpayer.regime, new_cap)
    surcharge = _surcharge_on(tax_after_rebate, cg_tax, rate, cg_cap)

    relief = Decimal("0")
    if surcharge > 0 and table.get("surcharge.marginal_relief", ay_ref_date).value:
        threshold = Decimal([lo for lo, _, _ in bands if ti > lo][-1])
        shave = ti - threshold
        if slab_base < shave:
            raise OutOfScopeError(
                "surcharge marginal relief needs slab income >= the excess over the "
                "threshold; special-rate-heavy composition is out of scope")
        # tax at threshold income: shave slab income only, specials unchanged
        # (engine policy — see surcharge.marginal_relief contested note).
        tax_t = _slab_tax(slab_base - shave, slabs) + sum(special_tax.values())
        rate_t = _surcharge_rate(threshold, bands, taxpayer.regime, new_cap)
        cap = tax_t + _surcharge_on(tax_t, cg_tax, rate_t, cg_cap) + shave
        relief = max(tax_after_rebate + surcharge - cap, Decimal("0"))

    pre_cess = tax_after_rebate + surcharge - relief
    cess = pre_cess * table.get("cess.health_education", ay_ref_date).value
    total = _round_nearest(pre_cess + cess,
                           table.get("rounding.tax_288b", ay_ref_date).value)

    return TaxComputation(
        total_income=ti, slab_income=slab_base, special_taxable=taxable,
        slab_tax=slab_tax, special_tax=special_tax, rebate_87a=rebate,
        surcharge=surcharge, marginal_relief=relief, cess=cess, total_tax=total)
