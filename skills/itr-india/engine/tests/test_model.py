from datetime import date
from decimal import Decimal
import pytest
from engine.model import (
    Regime, AgeBand, AssetClass, PresumptiveScheme, Taxpayer, CapitalGainItem,
    VdaItem, _add_months,
)


def test_capitalgain_gain_and_holding():
    it = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 12, 1),
                         Decimal("130000"), Decimal("100000"), stt_paid=True)
    assert it.gain == Decimal("30000")
    assert it.held_more_than_months(12) is False   # 11 months


def test_held_more_than_months_is_calendar_exact():
    exactly_12 = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2025, 1, 1),
                                 Decimal("1"), Decimal("0"), stt_paid=True)
    assert exactly_12.held_more_than_months(12) is False    # exactly 12 months -> short-term
    past_12 = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2025, 1, 2),
                              Decimal("1"), Decimal("0"), stt_paid=True)
    assert past_12.held_more_than_months(12) is True        # 12 months + 1 day -> long-term


def test_sale_before_acquisition_rejected():
    with pytest.raises(ValueError):
        CapitalGainItem(AssetClass.OTHER, date(2024, 12, 1), date(2024, 1, 1),
                        Decimal("1"), Decimal("0"))


def test_taxpayer_constructs():
    tp = Taxpayer(ay=2027, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)
    assert tp.ay == 2027
    assert tp.has_business_or_profession_income is False
    assert tp.presumptive_scheme is PresumptiveScheme.NONE
    assert tp.has_pgbp_income is False


def test_presumptive_scheme_implies_pgbp_income():
    tp = Taxpayer(
        ay=2027,
        resident=True,
        age_band=AgeBand.BELOW_60,
        regime=Regime.NEW,
        presumptive_scheme=PresumptiveScheme.SECTION_44ADA,
    )
    assert tp.has_pgbp_income is True


def test_add_months_clamps_to_month_end():
    # Jan 31 + 1 month -> 2024 is a leap year, Feb has 29 days
    assert _add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    # Jan 31 + 1 month -> 2023 is not a leap year, Feb has 28 days
    assert _add_months(date(2023, 1, 31), 1) == date(2023, 2, 28)
