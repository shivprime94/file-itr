from datetime import date
from decimal import Decimal
import pytest
from engine.model import (
    AdvanceTaxPayment, AgeBand, AssetClass, CapitalGainItem, PresumptiveScheme,
    Regime, Taxpayer, VdaItem,
)
from engine.rules.ay2026_27 import TABLE
from engine.rates import compute_tax
from engine.buckets import Bucket
from engine.scope import OutOfScopeError
from engine.interest import compute_interest

REF = date(2025, 6, 1)


def tp(regime=Regime.NEW, age=AgeBand.BELOW_60):
    return Taxpayer(ay=2027, resident=True, age_band=age, regime=regime)


def tax_of(normal=0, taxpayer=None, **kw):
    b = {Bucket.NORMAL: Decimal(normal), Bucket.STCG_SLAB: Decimal(0),
         Bucket.STCG_111A: Decimal(kw.get("s111a", 0)),
         Bucket.LTCG_112: Decimal(kw.get("s112", 0)),
         Bucket.LTCG_112A: Decimal(kw.get("s112a", 0)),
         Bucket.VDA_115BBH: Decimal(kw.get("vda", 0))}
    return compute_tax(b, taxpayer or tp(), TABLE, REF)


def pay(d, amt):
    return AdvanceTaxPayment(paid_on=d, amount=Decimal(amt))


def run(tax, tds=0, payments=(), items=(), taxpayer=None, **kw):
    return compute_interest(tax, Decimal(tds), list(payments), taxpayer or tp(),
                            TABLE, REF, items=list(items), **kw)


# tax_of(normal=2000000) under the new regime: slab tax 200000, cess 8000,
# total 208000 — used as the workhorse figure below.

# ---------------- 234B ----------------

def test_234b_zero_when_advance_at_least_90_percent():
    t = tax_of(normal=2000000)
    assert t.total_tax == Decimal("208000")
    r = run(t, payments=[pay(date(2026, 3, 10), 190000)],   # >= 90% of 208000
            self_assessment_date=date(2026, 7, 15))
    assert r.i234b == Decimal("0")


def test_234b_shortfall_1_percent_over_4_months():
    # assessed 208000; advance 100000 (< 90%); base 108000; Apr..Jul = 4 months
    t = tax_of(normal=2000000)
    r = run(t, payments=[pay(date(2026, 3, 10), 100000)],
            self_assessment_date=date(2026, 7, 15))
    assert r.i234b == Decimal("4320")


def test_234b_base_rounds_down_to_100_rule_119a():
    # shortfall 208000-100050 = 107950 -> base 107900 -> 1 month (paid 20 Apr)
    t = tax_of(normal=2000000)
    r = run(t, payments=[pay(date(2026, 3, 10), 100050)],
            self_assessment_date=date(2026, 4, 20))
    assert r.i234b == Decimal("1079")


def test_no_234b_234c_when_net_liability_at_most_10k():
    # ti 12.5L: slab 67500, 87A marginal relief 17500 -> tax 50000 + cess = 52000
    t = tax_of(normal=1250000)
    assert t.total_tax == Decimal("52000")
    r = run(t, tds=45000, self_assessment_date=date(2026, 7, 15))
    assert r.i234b == Decimal("0") and r.i234c == Decimal("0")


def test_senior_resident_without_pgbp_owes_no_234b_234c():
    # s.207(2): resident senior with no business income has no advance-tax
    # obligation at all.
    senior = tp(Regime.NEW, AgeBand.SENIOR)
    t = tax_of(normal=2000000, taxpayer=senior)
    r = run(t, taxpayer=senior, self_assessment_date=date(2026, 7, 15))
    assert r.i234b == Decimal("0") and r.i234c == Decimal("0")


def test_senior_with_pgbp_is_not_exempt_from_advance_tax():
    senior_business = Taxpayer(
        ay=2027,
        resident=True,
        age_band=AgeBand.SENIOR,
        regime=Regime.NEW,
        has_business_or_profession_income=True,
    )
    t = tax_of(normal=2000000, taxpayer=senior_business)
    r = run(t, taxpayer=senior_business, self_assessment_date=date(2026, 7, 15))
    assert r.i234b == Decimal("8320")
    assert r.i234c == Decimal("10504")


# ---------------- 234C ----------------

def test_234c_textbook_full_default():
    # nothing paid all year: shortfalls are the full cumulative requirements
    # 31200@3% + 93600@3% + 156000@3% + 208000@1% = 936+2808+4680+2080
    t = tax_of(normal=2000000)
    r = run(t, self_assessment_date=date(2026, 7, 15))
    assert r.i234c == Decimal("10504")


def test_234c_safe_harbor_12_percent_june():
    t = tax_of(normal=2000000)          # net 208000
    net = t.total_tax
    # 12.5% by 15 Jun (>= 12% safe harbor even though < 15%), then exact
    r = run(t, payments=[
        pay(date(2025, 6, 10), int(net * Decimal("0.125"))),   # 26000
        pay(date(2025, 9, 10), int(net * Decimal("0.325"))),   # cum 45%
        pay(date(2025, 12, 10), int(net * Decimal("0.30"))),   # cum 75%
        pay(date(2026, 3, 10), int(net * Decimal("0.25")) + 1),
    ], self_assessment_date=date(2026, 7, 15))
    assert r.i234c == Decimal("0")


@pytest.mark.parametrize(
    "scheme",
    [PresumptiveScheme.SECTION_44AD, PresumptiveScheme.SECTION_44ADA],
)
def test_234c_presumptive_44ad_44ada_due_in_full_only_by_march(scheme):
    presumptive = Taxpayer(
        ay=2027,
        resident=True,
        age_band=AgeBand.BELOW_60,
        regime=Regime.NEW,
        presumptive_scheme=scheme,
    )
    t = tax_of(normal=2000000, taxpayer=presumptive)
    r = run(
        t,
        taxpayer=presumptive,
        payments=[pay(date(2026, 3, 10), 208000)],
        self_assessment_date=date(2026, 7, 15),
    )
    assert r.i234c == Decimal("0")


def test_234c_presumptive_shortfall_is_one_percent_for_march_only():
    presumptive = Taxpayer(
        ay=2027,
        resident=True,
        age_band=AgeBand.BELOW_60,
        regime=Regime.NEW,
        presumptive_scheme=PresumptiveScheme.SECTION_44ADA,
    )
    t = tax_of(normal=2000000, taxpayer=presumptive)
    r = run(t, taxpayer=presumptive, self_assessment_date=date(2026, 7, 15))
    assert r.i234c == Decimal("2080")


def test_234c_section_44ae_keeps_ordinary_quarterly_schedule():
    transporter = Taxpayer(
        ay=2027,
        resident=True,
        age_band=AgeBand.BELOW_60,
        regime=Regime.NEW,
        presumptive_scheme=PresumptiveScheme.SECTION_44AE,
    )
    t = tax_of(normal=2000000, taxpayer=transporter)
    r = run(
        t,
        taxpayer=transporter,
        payments=[pay(date(2026, 3, 10), 208000)],
        self_assessment_date=date(2026, 7, 15),
    )
    assert r.i234c == Decimal("8424")


def test_234c_carveout_for_late_year_capital_gain():
    # 112A gain realised 20 Jan: its tax is excluded from the Jun/Sep/Dec
    # requirements (proviso to s.234C(1)); only the March instalment needs it.
    item = CapitalGainItem(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2026, 1, 20),
                           Decimal("1425000"), Decimal("100000"), stt_paid=True)
    t = tax_of(normal=2000000, s112a=1325000)
    assert t.total_tax == Decimal("364000")
    net_slab = Decimal("208000")   # tax with the gain carved out
    r = run(t, items=[item], payments=[
        pay(date(2025, 6, 10), int(net_slab * Decimal("0.15"))),
        pay(date(2025, 9, 10), int(net_slab * Decimal("0.30"))),
        pay(date(2025, 12, 10), int(net_slab * Decimal("0.30"))),
        pay(date(2026, 3, 10), 208001),   # tops up to the full 364000 by 15 Mar
    ], self_assessment_date=date(2026, 7, 15))
    assert r.i234c == Decimal("0")


def test_234c_vda_item_without_sale_date_refused():
    t = tax_of(normal=2000000, vda=100000)
    with pytest.raises(OutOfScopeError, match="sale_date"):
        run(t, items=[VdaItem(Decimal("150000"), Decimal("50000"))],
            self_assessment_date=date(2026, 7, 15))


def test_234c_refused_when_surcharge_applies():
    t = tax_of(normal=6000000)
    with pytest.raises(OutOfScopeError, match="surcharge"):
        run(t, self_assessment_date=date(2026, 7, 15))


def test_234c_refused_on_special_item_loss():
    item = CapitalGainItem(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2026, 1, 20),
                           Decimal("50000"), Decimal("90000"), stt_paid=True)
    t = tax_of(normal=2000000)
    with pytest.raises(OutOfScopeError, match="loss"):
        run(t, items=[item], self_assessment_date=date(2026, 7, 15))


# ---------------- 234A ----------------

def test_234a_zero_when_filed_by_due_date():
    t = tax_of(normal=2000000)
    r = run(t, self_assessment_date=date(2026, 7, 15),
            due_date=date(2026, 9, 15), filing_date=date(2026, 9, 1))
    assert r.i234a == Decimal("0")


def test_234a_part_month_counts_full():
    # due 15 Sep, filed 20 Oct -> 2 months; unpaid 108000 after 100000 advance
    t = tax_of(normal=2000000)
    r = run(t, payments=[pay(date(2026, 3, 10), 100000)],
            self_assessment_date=date(2026, 10, 20),
            due_date=date(2026, 9, 15), filing_date=date(2026, 10, 20))
    assert r.i234a == Decimal("2160")


def test_total_is_sum_of_components():
    t = tax_of(normal=2000000)
    r = run(t, payments=[pay(date(2026, 3, 10), 100000)],
            self_assessment_date=date(2026, 7, 15))
    assert r.total == r.i234a + r.i234b + r.i234c
