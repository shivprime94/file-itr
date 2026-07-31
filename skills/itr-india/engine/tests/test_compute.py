from datetime import date
from decimal import Decimal
import pytest
from engine.model import (
    AdvanceTaxPayment, AgeBand, AssetClass, BroughtForwardLoss, CapitalGainItem,
    CFLossKind, Regime, Taxpayer, VdaItem,
)
from engine.buckets import Bucket
from engine.scope import OutOfScopeError
from engine.compute import compute, render_report

TP = Taxpayer(ay=2027, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)


def test_end_to_end_salaried_with_equity_and_bf_loss():
    items = [
        # equity STCG 30k (STT, held < 12m)
        CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2025, 5, 1), date(2025, 12, 1),
                        Decimal("130000"), Decimal("100000"), stt_paid=True),
        # equity LTCG 50k (within the 1.25L 112A exemption)
        CapitalGainItem(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2025, 8, 1),
                        Decimal("250000"), Decimal("200000"), stt_paid=True),
    ]
    bf = [BroughtForwardLoss(kind=CFLossKind.STCL, ay_incurred=2025,
                             amount=Decimal("10000"))]
    c = compute(TP, items, bf_losses=bf, normal_income=Decimal("1100000"),
                self_assessment_date=date(2026, 7, 31))
    # b/f STCL 10k absorbs into the 30k STCG
    assert c.setoff.buckets[Bucket.STCG_111A] == Decimal("20000")
    # ti = 11L + 20k + 50k = 11.7L <= 12L: slab tax fully rebated,
    # 112A within exemption, only 111A 20k @ 20% + cess survives
    assert c.tax.rebate_87a == c.tax.slab_tax
    assert c.tax.special_tax[Bucket.STCG_111A] == Decimal("4000")
    assert c.tax.total_tax == Decimal("4160")
    # net liability 4160 <= 10k: no advance-tax interest
    assert c.interest.i234b == Decimal("0") and c.interest.i234c == Decimal("0")
    assert c.total_payable == Decimal("4160")


def test_end_to_end_vda_quarantine_flows_through():
    items = [VdaItem(Decimal("100000"), Decimal("60000")),
             VdaItem(Decimal("10000"), Decimal("25000"))]
    c = compute(TP, items, normal_income=Decimal("500000"))
    assert c.setoff.buckets[Bucket.VDA_115BBH] == Decimal("40000")
    assert len(c.setoff.dead) == 1
    # slab tax on 5L rebated (ti 5.4L <= 12L); VDA 40k @ 30% stands
    assert c.tax.special_tax[Bucket.VDA_115BBH] == Decimal("12000")
    assert c.tax.total_tax == Decimal("12480")
    assert c.interest is None            # no self_assessment_date given
    assert c.total_payable == Decimal("12480")


def test_compute_refuses_pre_jul2024_land_ltcg():
    items = [CapitalGainItem(AssetClass.LAND_BUILDING, date(2020, 1, 1), date(2025, 12, 1),
                             Decimal("5000000"), Decimal("2000000"))]
    with pytest.raises(OutOfScopeError, match="indexation"):
        compute(TP, items)


def test_compute_refuses_wrong_ay():
    tp = Taxpayer(ay=2026, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)
    with pytest.raises(OutOfScopeError, match="AY"):
        compute(tp, [])


def test_trace_contains_bucketing_and_setoff_lines():
    items = [
        CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2025, 5, 1), date(2025, 12, 1),
                        Decimal("130000"), Decimal("100000"), stt_paid=True),
        CapitalGainItem(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2025, 11, 1),
                        Decimal("50000"), Decimal("70000")),   # slab STCL 20k
    ]
    c = compute(TP, items, normal_income=Decimal("300000"))
    rendered = c.trace.render()
    assert "CapitalGainItem" in rendered            # bucketing lines
    assert "current-year STCL" in rendered          # set-off line
    assert "s70.stcl_setoff_any_cg" in rendered


def test_render_report_end_to_end():
    items = [VdaItem(Decimal("100000"), Decimal("60000"), sale_date=date(2025, 5, 10))]
    c = compute(TP, items, normal_income=Decimal("2000000"),
                advance_payments=[AdvanceTaxPayment(date(2026, 3, 10), Decimal("100000"))],
                self_assessment_date=date(2026, 7, 15))
    report = render_report(c)
    assert "TOTAL PAYABLE" in report
    assert "234B" in report
    assert "vda_115bbh tax: 12000" in report   # pre-cess special-rate tax line


def test_interest_totals_flow_into_total_payable():
    c = compute(TP, [], normal_income=Decimal("2000000"),
                self_assessment_date=date(2026, 7, 15))
    assert c.tax.total_tax == Decimal("208000")
    assert c.interest.total > 0                      # nothing prepaid: 234B + 234C
    assert c.total_payable == c.tax.total_tax + c.interest.total


def test_tds_and_advance_tax_reduce_amount_payable():
    c = compute(
        TP,
        [],
        normal_income=Decimal("2000000"),
        tds=Decimal("100000"),
        advance_payments=[AdvanceTaxPayment(date(2026, 3, 10), Decimal("100000"))],
        self_assessment_date=date(2026, 7, 15),
    )
    assert c.total_credits == Decimal("200000")
    assert c.total_payable == c.tax.total_tax + c.interest.total - c.total_credits
    assert c.refund_due == Decimal("0")


def test_excess_tds_is_reported_as_refund_not_payable():
    c = compute(TP, [], normal_income=Decimal("500000"), tds=Decimal("25000"))
    assert c.tax.total_tax == Decimal("0")
    assert c.total_payable == Decimal("0")
    assert c.refund_due == Decimal("25000")
    report = render_report(c)
    assert "REFUND DUE: 25000" in report
    assert "TOTAL PAYABLE: 0" in report
