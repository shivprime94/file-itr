from datetime import date
from decimal import Decimal
import pytest
from engine.model import AssetClass, CapitalGainItem, VdaItem
from engine.rules.ay2026_27 import TABLE
from engine.buckets import Bucket, classify, bucket_income, effective_gain

REF = date(2025, 6, 1)


def cg(asset, acq, sale, gain, stt=False):
    return CapitalGainItem(asset, acq, sale, Decimal(gain), Decimal(0), stt_paid=stt)


def test_equity_stt_short_term_is_111a():
    b, key = classify(cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1), 30000, stt=True), TABLE, REF)
    assert b is Bucket.STCG_111A
    # FINDING 4: Assert rule_key
    assert key == "holding.listed_equity.lt_months"


def test_equity_stt_long_term_is_112a():
    b, _ = classify(cg(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2024, 6, 1), 50000, stt=True), TABLE, REF)
    assert b is Bucket.LTCG_112A


def test_arbitrage_fund_short_holding_still_111a():
    # arbitrage funds are equity-oriented: short holding -> 111A, not slab
    b, _ = classify(cg(AssetClass.EQUITY_MF_STT, date(2024, 1, 1), date(2024, 9, 1), 10000, stt=True), TABLE, REF)
    assert b is Bucket.STCG_111A


def test_equity_boundary_exact_12_months_is_short():
    # FINDING 2: Calendar-exact boundary — acquired 2024-01-01, sold exactly 2025-01-01 (12 months to the day)
    # Should be short-term (NOT more than 12 months)
    b, _ = classify(cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2025, 1, 1), 25000, stt=True), TABLE, REF)
    assert b is Bucket.STCG_111A


def test_equity_boundary_12_months_plus_1_day_is_long():
    # FINDING 2: Calendar-exact boundary — acquired 2024-01-01, sold 2025-01-02 (12m + 1 day)
    # Should be long-term (MORE than 12 months)
    b, _ = classify(cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2025, 1, 2), 35000, stt=True), TABLE, REF)
    assert b is Bucket.LTCG_112A


def test_debt_50aa_always_slab():
    b, _ = classify(cg(AssetClass.DEBT_MF_50AA, date(2023, 5, 1), date(2027, 1, 1), 40000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_debt_50aa_pre_2023_04_01_raises():
    # FINDING 5: DEBT_MF_50AA acquired before 2023-04-01 raises ValueError
    with pytest.raises(ValueError, match="pre-dates s.50AA"):
        classify(cg(AssetClass.DEBT_MF_50AA, date(2022, 5, 1), date(2024, 1, 1), 50000), TABLE, REF)


def test_gold_etf_long_term_is_112():
    # Listed gold ETF held > 12 months (s.2(42A), w.e.f. 23-Jul-2024) → LTCG u/s 112.
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2026, 5, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_gold_etf_short_term_is_slab():
    # Held <= 12 months → STCG at slab.
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2025, 6, 1), 15000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_gold_etf_15_months_is_long_term_not_slab():
    # Flat 12-month threshold regardless of acquisition date: a gold ETF acquired
    # 1-Sep-2024 and sold 1-Dec-2025 (15 months, FY 2025-26) is LONG-term u/s 112,
    # NOT short-term slab. No 24-month acquisition-date transitional exists — for
    # AY 2026-27 gold ETFs are outside s.50AA and take the s.2(42A) 12-month rule.
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2024, 9, 1), date(2025, 12, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_gold_etf_pre_jul2024_acquisition_is_long_term():
    # A gold ETF acquired before 23-Jul-2024 and sold in FY 2025-26, held > 12
    # months, is an ordinary LTCG u/s 112 — NOT out of scope (the earlier
    # acquisition-date fail-loud over-refused it).
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2023, 6, 1), date(2025, 8, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_gold_etf_boundary_exact_12_months_is_short():
    # Calendar-exact: acquired 2025-01-01, sold exactly 2026-01-01 (12 months to
    # the day) → short-term (not MORE than 12 months).
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 1, 1), date(2026, 1, 1), 20000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_land_building_long_term_is_112():
    # FINDING 1: LAND_BUILDING long-term (>24m) untested
    b, _ = classify(cg(AssetClass.LAND_BUILDING, date(2022, 1, 1), date(2024, 6, 1), 100000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_land_building_short_term_is_slab():
    # FINDING 1: LAND_BUILDING short-term (<24m) untested
    b, _ = classify(cg(AssetClass.LAND_BUILDING, date(2024, 1, 1), date(2024, 11, 1), 50000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_unlisted_shares_long_term_is_112():
    # FINDING 1: UNLISTED_SHARES long-term (>24m) untested
    b, _ = classify(cg(AssetClass.UNLISTED_SHARES, date(2022, 1, 1), date(2024, 6, 1), 75000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_unlisted_shares_short_term_is_slab():
    # FINDING 1: UNLISTED_SHARES short-term (<24m) untested
    b, _ = classify(cg(AssetClass.UNLISTED_SHARES, date(2024, 1, 1), date(2024, 11, 1), 60000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_vda_is_115bbh():
    b, _ = classify(VdaItem(Decimal("100000"), Decimal("60000")), TABLE, REF)
    assert b is Bucket.VDA_115BBH


def test_bucket_income_sums_and_partitions():
    items = [
        cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1), 30000, stt=True),
        cg(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2024, 6, 1), 50000, stt=True),
        VdaItem(Decimal("100000"), Decimal("60000")),
    ]
    out = bucket_income(items, TABLE, REF)
    assert out[Bucket.STCG_111A] == Decimal("30000")
    assert out[Bucket.LTCG_112A] == Decimal("50000")
    assert out[Bucket.VDA_115BBH] == Decimal("40000")
    # every rupee accounted for exactly once
    assert sum(out.values()) == Decimal("120000")


def _cg_item(asset, acq, sale, proceeds, cost, fmv=None):
    return CapitalGainItem(asset, acq, sale, Decimal(proceeds), Decimal(cost),
                           stt_paid=True, fmv_31jan2018=fmv)


def test_effective_gain_112a_pre2018_reduces_to_post_fmv_appreciation():
    # cost 1L, FMV-on-31Jan2018 4L, sale 10L -> COA=4L, gain = 10L-4L = 6L
    # (only appreciation after 31-Jan-2018 is taxed; raw gain would be 9L)
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                    1000000, 100000, fmv=400000)
    assert effective_gain(item, Bucket.LTCG_112A, TABLE, REF) == Decimal("600000")


def test_effective_gain_112a_pre2018_sale_within_fmv_band_is_zero():
    # cost 1L, FMV 5L, sale 3L (between cost and FMV) -> COA=min(FMV,sale)=3L,
    # gain = 3L-3L = 0: the entire gain is pre-2018 appreciation.
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                    300000, 100000, fmv=500000)
    assert effective_gain(item, Bucket.LTCG_112A, TABLE, REF) == Decimal("0")


def test_effective_gain_112a_pre2018_crash_below_cost_is_genuine_loss():
    # cost 5L, FMV 8L, sale 3L (price crashed below actual cost) -> COA=cost
    # (never FMV-inflated), loss = 3L-5L = -2L, not manufactured by FMV.
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                    300000, 500000, fmv=800000)
    assert effective_gain(item, Bucket.LTCG_112A, TABLE, REF) == Decimal("-200000")


def test_effective_gain_112a_pre2018_missing_fmv_raises():
    from engine.scope import OutOfScopeError
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                    1000000, 100000)   # fmv=None
    with pytest.raises(OutOfScopeError, match="fmv_31jan2018"):
        effective_gain(item, Bucket.LTCG_112A, TABLE, REF)


def test_effective_gain_post_cutoff_acquisition_unchanged():
    # acquired 2019 (after the 1-Feb-2018 cutoff) -> grandfathering never
    # applies, even though fmv is supplied.
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2019, 1, 1), date(2025, 8, 1),
                    500000, 200000, fmv=999999)
    assert effective_gain(item, Bucket.LTCG_112A, TABLE, REF) == item.gain
    assert effective_gain(item, Bucket.LTCG_112A, TABLE, REF) == Decimal("300000")


def test_effective_gain_non_112a_bucket_unchanged_even_if_pre2018():
    # LAND_BUILDING -> LTCG_112, not LTCG_112A: s.55(2)(ac) grandfathering is
    # 112A-specific and must never apply here, regardless of acquisition date.
    item = CapitalGainItem(AssetClass.LAND_BUILDING, date(2016, 1, 1), date(2025, 8, 1),
                           Decimal("1000000"), Decimal("100000"),
                           fmv_31jan2018=Decimal("400000"))
    assert effective_gain(item, Bucket.LTCG_112, TABLE, REF) == item.gain
    assert effective_gain(item, Bucket.LTCG_112, TABLE, REF) == Decimal("900000")


def test_bucket_income_applies_112a_grandfathering():
    item = _cg_item(AssetClass.EQUITY_MF_STT, date(2016, 1, 1), date(2025, 8, 1),
                    1000000, 100000, fmv=700000)
    out = bucket_income([item], TABLE, REF)
    assert out[Bucket.LTCG_112A] == Decimal("300000")   # not the raw 900000
