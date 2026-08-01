from datetime import date
from decimal import Decimal
import pytest
from engine.model import AssetClass, CapitalGainItem, VdaItem
from engine.rules.ay2026_27 import TABLE
from engine.buckets import Bucket, classify, bucket_income

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
    # Acquired on/after 1-Apr-2025 → 12-month LT threshold.
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2026, 5, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_gold_etf_short_term_is_slab():
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2025, 6, 1), 15000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_gold_etf_transitional_24m_still_short_at_16_months():
    # Acquired 23-Jul-2024..31-Mar-2025 → 24-month threshold, not 12.
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 1, 1), date(2026, 5, 1), 20000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_gold_etf_transitional_24m_long_term():
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2024, 8, 1), date(2026, 9, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_gold_etf_pre_jul2024_refused():
    from engine.scope import OutOfScopeError
    import pytest
    with pytest.raises(OutOfScopeError, match="before 23-Jul-2024"):
        classify(cg(AssetClass.GOLD_ETF_LISTED, date(2023, 6, 1), date(2025, 8, 1), 20000), TABLE, REF)


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
