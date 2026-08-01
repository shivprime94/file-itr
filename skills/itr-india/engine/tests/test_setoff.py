from datetime import date
from decimal import Decimal
import pytest
from engine.model import (
    AgeBand, AssetClass, BroughtForwardLoss, CapitalGainItem, CFLossKind,
    Regime, Taxpayer, VdaItem,
)
from engine.rules.ay2026_27 import TABLE
from engine.buckets import Bucket
from engine.scope import OutOfScopeError
from engine.setoff import apply_setoff, trace_setoff

REF = date(2025, 6, 1)
TP = Taxpayer(ay=2027, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)


def cg(asset, acq, sale, gain, stt=False):
    return CapitalGainItem(asset, acq, sale, Decimal(gain), Decimal(0), stt_paid=stt)


def st_111a(gain):  # listed equity, STT, held < 12m
    return cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1), gain, stt=True)


def st_slab(gain):  # gold ETF held < 12m (post-1-Apr-2025 acq → 12m threshold)
    return cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2025, 6, 1), gain)


def lt_112a(gain):  # equity MF, STT, held > 12m
    return cg(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2024, 6, 1), gain, stt=True)


def lt_112(gain):  # gold ETF held > 12m (post-1-Apr-2025 acq)
    return cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2026, 5, 1), gain)


def bf(kind, ay, amount, timely=True):
    return BroughtForwardLoss(kind=kind, ay_incurred=ay, amount=Decimal(amount),
                              return_filed_by_due_date=timely)


def run(items, bfs=(), normal=Decimal("0")):
    return apply_setoff(items, list(bfs), TP, TABLE, REF, normal_income=normal)


# ---------------- current-year set-off (s.70) ----------------

def test_no_losses_passthrough():
    r = run([st_111a(30000), lt_112a(50000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("30000")
    assert r.buckets[Bucket.LTCG_112A] == Decimal("50000")
    assert r.steps == [] and r.carry_forward == [] and r.dead == []


def test_stcl_nets_against_st_gains_first():
    r = run([st_111a(30000), st_slab(-10000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("20000")
    assert r.buckets[Bucket.STCG_SLAB] == Decimal("0")
    assert r.carry_forward == []
    assert any(s.rule_key == "s70.stcl_setoff_any_cg" for s in r.steps)


def test_stcl_spills_over_to_ltcg():
    r = run([st_111a(-10000), lt_112a(50000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("0")
    assert r.buckets[Bucket.LTCG_112A] == Decimal("40000")


def test_ltcl_never_sets_off_against_stcg():
    r = run([lt_112(-20000), st_111a(30000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("30000")
    [cf] = r.carry_forward
    assert cf.kind is CFLossKind.LTCL
    assert cf.amount == Decimal("20000")
    assert cf.ay_incurred == 2027
    assert cf.usable_through_ay == 2035
    assert cf.conditional_on_timely_return is True


def test_ltcl_gets_priority_claim_on_ltcg_over_stcl_spillover():
    # LTCL is the more restricted loss: it must absorb LTCG before STCL spills in.
    r = run([lt_112(-10000), st_111a(-10000), lt_112a(15000)])
    assert r.buckets[Bucket.LTCG_112A] == Decimal("0")
    [cf] = r.carry_forward
    assert cf.kind is CFLossKind.STCL and cf.amount == Decimal("5000")


def test_setoff_order_within_term_is_slab_before_concession():
    # engine.cg_setoff_order (contested policy): STCG_SLAB before STCG_111A.
    r = run([st_slab(8000), st_111a(9000), lt_112(-12000), st_111a(0)])
    # LTCL cannot touch ST at all; nothing absorbed, both ST buckets intact.
    assert r.buckets[Bucket.STCG_SLAB] == Decimal("8000")
    assert r.buckets[Bucket.STCG_111A] == Decimal("9000")
    # Now an STCL: eats slab bucket first, then 111A.
    r2 = run([st_slab(8000), st_111a(9000), lt_112(-12000), st_slab(-10000)])
    assert r2.buckets[Bucket.STCG_SLAB] == Decimal("0")
    assert r2.buckets[Bucket.STCG_111A] == Decimal("7000")
    rule = TABLE.get("engine.cg_setoff_order", REF)
    assert rule.confidence == "contested"


# ---------------- VDA quarantine (s.115BBH(2)(b)) ----------------

def test_vda_loss_is_quarantined_not_netted():
    r = run([VdaItem(Decimal("100000"), Decimal("60000")),   # +40k
             VdaItem(Decimal("10000"), Decimal("25000"))])   # -15k
    assert r.buckets[Bucket.VDA_115BBH] == Decimal("40000")
    [d] = r.dead
    assert d.amount == Decimal("15000")
    assert d.rule_key == "s115bbh.loss_setoff_disallowed"
    assert r.carry_forward == []  # VDA loss cannot be carried forward either


def test_cg_loss_never_absorbs_vda_gains():
    r = run([st_111a(-10000), VdaItem(Decimal("50000"), Decimal("10000"))])
    assert r.buckets[Bucket.VDA_115BBH] == Decimal("40000")
    [cf] = r.carry_forward
    assert cf.kind is CFLossKind.STCL and cf.amount == Decimal("10000")


# ---------------- inter-head bar (s.71(3)) ----------------

def test_capital_loss_never_touches_normal_income():
    r = run([st_111a(-10000)], normal=Decimal("500000"))
    assert r.buckets[Bucket.NORMAL] == Decimal("500000")
    [cf] = r.carry_forward
    assert cf.amount == Decimal("10000")


# ---------------- brought-forward losses (s.74 / s.80) ----------------

def test_bf_stcl_applied_after_current_year_setoff():
    r = run([st_111a(50000), st_slab(-20000)], [bf(CFLossKind.STCL, 2024, 10000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("20000")
    assert r.carry_forward == []
    bf_steps = [s for s in r.steps if s.rule_key == "s74.cf_stcl_setoff_any_cg"]
    assert len(bf_steps) == 1 and bf_steps[0].amount == Decimal("10000")


def test_bf_ltcl_only_against_ltcg():
    r = run([st_111a(50000)], [bf(CFLossKind.LTCL, 2024, 30000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("50000")
    [cf] = r.carry_forward
    assert cf.kind is CFLossKind.LTCL
    assert cf.ay_incurred == 2024
    assert cf.usable_through_ay == 2032
    assert cf.conditional_on_timely_return is False


def test_bf_oldest_first():
    r = run([st_111a(15000)],
            [bf(CFLossKind.STCL, 2025, 10000), bf(CFLossKind.STCL, 2021, 10000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("0")
    [cf] = r.carry_forward
    assert cf.ay_incurred == 2025 and cf.amount == Decimal("5000")


def test_bf_expired_loss_lapses():
    # AY 2018 loss usable through AY 2026 (< current AY 2027): lapsed.
    r = run([st_111a(50000)], [bf(CFLossKind.STCL, 2018, 10000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("50000")
    [d] = r.dead
    assert d.rule_key == "s74.cf_years"
    assert r.carry_forward == []


def test_bf_last_usable_year_boundary():
    # AY 2019 loss usable through AY 2027 (== current AY): still usable.
    r = run([st_111a(50000)], [bf(CFLossKind.STCL, 2019, 10000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("40000")


def test_bf_remainder_on_last_usable_year_expires_not_carried():
    # AY 2019 loss usable through AY 2027. Absorb 30k of 100k; remainder must
    # die under s.74(2), not reappear as carry_forward for AY 2028+.
    r = run([st_111a(30000)], [bf(CFLossKind.STCL, 2019, 100000)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("0")
    assert r.carry_forward == []
    [d] = [x for x in r.dead if "remainder expires" in x.reason]
    assert d.amount == Decimal("70000")
    assert d.rule_key == "s74.cf_years"


def test_bf_without_timely_return_is_dead_not_carried():
    r = run([st_111a(50000)], [bf(CFLossKind.STCL, 2024, 10000, timely=False)])
    assert r.buckets[Bucket.STCG_111A] == Decimal("50000")
    [d] = r.dead
    assert d.rule_key == "s80.timely_return_required"
    assert r.carry_forward == []


def test_bf_from_current_or_future_ay_refused():
    with pytest.raises(OutOfScopeError):
        run([st_111a(1000)], [bf(CFLossKind.STCL, 2027, 5000)])


def test_bf_nonpositive_amount_rejected_at_construction():
    with pytest.raises(ValueError):
        BroughtForwardLoss(kind=CFLossKind.STCL, ay_incurred=2024,
                           amount=Decimal("-5000"), return_filed_by_due_date=True)


# ---------------- invariants & trace ----------------

def test_conservation_of_losses():
    items = [st_111a(30000), st_slab(-20000), lt_112a(10000), lt_112(-25000),
             VdaItem(Decimal("5000"), Decimal("9000"))]
    bfs = [bf(CFLossKind.STCL, 2018, 7000),           # lapsed
           bf(CFLossKind.LTCL, 2024, 4000),
           bf(CFLossKind.STCL, 2025, 3000, timely=False)]  # dead (s.80)
    r = run(items, bfs)
    losses_in = Decimal("20000") + Decimal("25000") + Decimal("4000") + \
        Decimal("7000") + Decimal("3000") + Decimal("4000")  # incl. VDA 4k
    absorbed = sum(s.amount for s in r.steps)
    carried = sum(c.amount for c in r.carry_forward)
    dead = sum(d.amount for d in r.dead)
    assert absorbed + carried + dead == losses_in
    assert all(v >= 0 for v in r.buckets.values())


def test_every_step_rule_key_resolves():
    r = run([st_111a(30000), st_slab(-20000), lt_112a(10000), lt_112(-25000)],
            [bf(CFLossKind.STCL, 2024, 5000)])
    for s in r.steps:
        TABLE.get(s.rule_key, REF)  # raises if unresolvable
    for d in r.dead:
        TABLE.get(d.rule_key, REF)


def test_trace_setoff_renders():
    r = run([st_111a(30000), st_slab(-20000)])
    tr = trace_setoff(r, TABLE, REF)
    out = tr.render()
    assert "s70.stcl_setoff_any_cg" in out


def test_setoff_buckets_use_grandfathered_112a_gain():
    item = CapitalGainItem(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                           Decimal("1000000"), Decimal("100000"), stt_paid=True,
                           fmv_31jan2018=Decimal("700000"))
    result = run([item])
    assert result.buckets[Bucket.LTCG_112A] == Decimal("300000")   # not raw 900000
