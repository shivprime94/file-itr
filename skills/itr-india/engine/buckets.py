from __future__ import annotations
from collections import defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum
from engine.model import CapitalGainItem, VdaItem, AssetClass
from engine.rulebase import RuleTable
from engine.scope import OutOfScopeError

# Finance (No. 2) Act, 2024, s.3(b) (eGazette; retrospective 23-Jul-2024) amends
# s.2(42A) so a LISTED unit that is not an equity-oriented-fund unit — gold/
# silver ETF, listed debt/hybrid/REIT/InVIT/AIF unit — has a flat 12-month
# long-term threshold, with NO acquisition-date grandfathering. For AY 2026-27
# gold/silver ETFs are also outside s.50AA (s.21(b) of the same Act, w.e.f.
# 1-Apr-2026 — SMF = >65% debt / qualifying FoF). Threshold lives in the rule
# table (holding.listed_nonequity.lt_months); classify() reads it directly —
# there is no 24-month "transitional" band.

# s.55(2)(ac): equity share/equity-MF unit acquired before 1-Feb-2018 gets a
# grandfathered cost of acquisition for s.112A purposes (only post-31-Jan-2018
# appreciation is taxed).
_S55_GRANDFATHER_CUTOFF = date(2018, 2, 1)


class Bucket(Enum):
    NORMAL = "normal"
    STCG_111A = "stcg_111a"
    STCG_SLAB = "stcg_slab"
    LTCG_112A = "ltcg_112a"
    LTCG_112 = "ltcg_112"
    VDA_115BBH = "vda_115bbh"


def classify(item, table: RuleTable, ay_ref_date: date) -> tuple[Bucket, str]:
    if isinstance(item, VdaItem):
        return Bucket.VDA_115BBH, "s115bbh.applies"

    if isinstance(item, CapitalGainItem):
        a = item.asset
        if a is AssetClass.DEBT_MF_50AA:
            rule = table.get("s50aa.acquired_from", ay_ref_date)
            if item.acquisition_date >= rule.value:
                return Bucket.STCG_SLAB, rule.key
            raise ValueError("Debt MF acquired before 1-Apr-2023 pre-dates s.50AA — out of Phase 1 scope")
        if a in (AssetClass.LISTED_EQUITY_STT, AssetClass.EQUITY_MF_STT) and item.stt_paid:
            r = table.get("holding.listed_equity.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112A, r.key) if lt else (Bucket.STCG_111A, r.key)
        if a is AssetClass.GOLD_ETF_LISTED:
            r = table.get("holding.listed_nonequity.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112, r.key) if lt else (Bucket.STCG_SLAB, r.key)
        if a in (AssetClass.LAND_BUILDING, AssetClass.UNLISTED_SHARES):
            r = table.get("holding.other.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112, r.key) if lt else (Bucket.STCG_SLAB, r.key)

    raise ValueError(
        f"internal invariant violated: unclassifiable item {item!r} reached classify; "
        "check_scope should have refused it")


def effective_gain(item, bucket: Bucket, table: RuleTable, ay_ref_date: date) -> Decimal:
    """Item's gain for tax purposes: raw, except LTCG_112A items acquired
    before 1-Feb-2018 get the s.55(2)(ac) grandfathered cost of acquisition."""
    if bucket is Bucket.LTCG_112A and item.acquisition_date < _S55_GRANDFATHER_CUTOFF:
        table.get("s55.grandfather_112a_coa", ay_ref_date)
        if item.fmv_31jan2018 is None:
            raise OutOfScopeError(
                "LTCG_112A item acquired before 1-Feb-2018 needs fmv_31jan2018 "
                "for s.55(2)(ac) grandfathering — not supplied")
        coa = max(item.cost, min(item.fmv_31jan2018, item.proceeds))
        return item.proceeds - coa
    return item.gain


def bucket_income(items: list, table: RuleTable, ay_ref_date: date) -> dict[Bucket, Decimal]:
    out: dict[Bucket, Decimal] = defaultdict(lambda: Decimal("0"))
    for it in items:
        bucket, _ = classify(it, table, ay_ref_date)
        out[bucket] += effective_gain(it, bucket, table, ay_ref_date)
    return dict(out)
