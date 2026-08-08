from decimal import Decimal
import pytest
from engine.form16 import Form16Record, aggregate_form16s
from engine.model import Regime


def test_two_employers_new_regime_matches_reference_example():
    records = [
        Form16Record(
            "Employer A",
            gross_17_1=Decimal("600000"),
            section_10_exemptions=Decimal("50000"),
            professional_tax=Decimal("2400"),
            tds_192=Decimal("45000"),
        ),
        Form16Record(
            "Employer B",
            gross_17_1=Decimal("900000"),
            perquisites_17_2=Decimal("20000"),
            section_10_exemptions=Decimal("120000"),
            professional_tax=Decimal("2400"),
            tds_192=Decimal("110000"),
        ),
    ]
    agg = aggregate_form16s(records, regime=Regime.NEW)
    assert agg.income_before_standard_deduction == Decimal("1345200")
    assert agg.income_after_standard_deduction == Decimal("1270200")
    assert agg.total_tds_192 == Decimal("155000")
    assert agg.standard_deduction == Decimal("75000")


def test_old_regime_standard_deduction():
    r = Form16Record("Only", gross_17_1=Decimal("500000"))
    agg = aggregate_form16s([r], regime=Regime.OLD)
    assert agg.standard_deduction == Decimal("50000")
    assert agg.income_after_standard_deduction == Decimal("450000")


def test_empty_list_rejected():
    with pytest.raises(ValueError, match="at least one"):
        aggregate_form16s([], regime=Regime.NEW)


def test_negative_gross_rejected():
    with pytest.raises(ValueError, match="gross_17_1"):
        Form16Record("X", gross_17_1=Decimal("-1"))
