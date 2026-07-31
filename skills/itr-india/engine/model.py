from __future__ import annotations
import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional


def _add_months(d: date, n: int) -> date:
    """d plus n calendar months, clamping the day to the target month's length."""
    m0 = d.month - 1 + n
    year = d.year + m0 // 12
    month = m0 % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class Regime(Enum):
    OLD = "old"
    NEW = "new"


class AgeBand(Enum):
    BELOW_60 = "below_60"
    SENIOR = "senior"            # 60-79
    SUPER_SENIOR = "super_senior"  # 80+


class PresumptiveScheme(Enum):
    NONE = "none"
    SECTION_44AD = "44ad"
    SECTION_44ADA = "44ada"
    SECTION_44AE = "44ae"


class AssetClass(Enum):
    LISTED_EQUITY_STT = "listed_equity_stt"
    EQUITY_MF_STT = "equity_mf_stt"
    DEBT_MF_50AA = "debt_mf_50aa"
    GOLD_ETF_LISTED = "gold_etf_listed"
    UNLISTED_SHARES = "unlisted_shares"
    LAND_BUILDING = "land_building"
    OTHER = "other"


@dataclass(frozen=True)
class Taxpayer:
    ay: int
    resident: bool
    age_band: AgeBand
    regime: Regime
    # Section 207(2) exempts a resident senior from advance tax only when the
    # senior has no income chargeable under "Profits and gains of business or
    # profession". Keep the default for callers created before this field was
    # introduced, while making ITR-3/4 callers state the disqualifier.
    has_business_or_profession_income: bool = False
    # Sections 44AD and 44ADA use the single-instalment s.234C schedule:
    # 100% advance tax by 15 March. Section 44AE does not receive that
    # statutory concession and remains on the ordinary quarterly schedule.
    presumptive_scheme: PresumptiveScheme = PresumptiveScheme.NONE

    @property
    def has_pgbp_income(self) -> bool:
        return (
            self.has_business_or_profession_income
            or self.presumptive_scheme is not PresumptiveScheme.NONE
        )


@dataclass(frozen=True)
class CapitalGainItem:
    asset: AssetClass
    acquisition_date: date
    sale_date: date
    proceeds: Decimal
    cost: Decimal
    stt_paid: bool = False
    fmv_31jan2018: Optional[Decimal] = None

    def __post_init__(self):
        if self.sale_date < self.acquisition_date:
            raise ValueError("sale_date is before acquisition_date")

    @property
    def gain(self) -> Decimal:
        return self.proceeds - self.cost

    @property
    def holding_days(self) -> int:
        return (self.sale_date - self.acquisition_date).days

    def held_more_than_months(self, n: int) -> bool:
        """True if held for MORE than n calendar months
        (s.2(42A): long-term = held for more than the threshold). Calendar-exact."""
        return self.sale_date > _add_months(self.acquisition_date, n)


@dataclass(frozen=True)
class VdaItem:
    proceeds: Decimal
    cost: Decimal
    # Needed only for the s.234C capital-gains carve-out (quarterly accrual);
    # bucketing/set-off/rates never read it.
    sale_date: Optional[date] = None

    @property
    def gain(self) -> Decimal:
        return self.proceeds - self.cost


@dataclass(frozen=True)
class AdvanceTaxPayment:
    paid_on: date
    amount: Decimal

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("advance-tax payment amount must be positive")


class CFLossKind(Enum):
    STCL = "stcl"
    LTCL = "ltcl"


@dataclass(frozen=True)
class BroughtForwardLoss:
    """A capital loss brought forward from an earlier AY (s.74).

    ay_incurred is the AY for which the loss was first computed; s.74(2) makes
    it usable through ay_incurred + 8. return_filed_by_due_date asserts the
    s.80/139(3) gate was met in the loss year — the engine cannot verify it.
    """
    kind: CFLossKind
    ay_incurred: int
    amount: Decimal
    return_filed_by_due_date: bool = True

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("brought-forward loss amount must be positive")
