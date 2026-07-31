from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from engine.buckets import Bucket, classify
from engine.model import BroughtForwardLoss, CFLossKind, Taxpayer, VdaItem
from engine.rulebase import RuleTable
from engine.scope import OutOfScopeError
from engine.trace import Trace, TraceLine

_ST_BUCKETS = (Bucket.STCG_SLAB, Bucket.STCG_111A)
_LT_BUCKETS = (Bucket.LTCG_112, Bucket.LTCG_112A)


@dataclass(frozen=True)
class SetOffStep:
    loss_label: str
    against: Bucket
    amount: Decimal          # positive: how much loss was absorbed here
    rule_key: str


@dataclass(frozen=True)
class DeadLoss:
    label: str
    amount: Decimal
    rule_key: str
    reason: str


@dataclass(frozen=True)
class CarryForwardOut:
    kind: CFLossKind
    ay_incurred: int
    amount: Decimal
    usable_through_ay: int
    # True for losses first computed this AY: s.80 makes their carry-forward
    # conditional on this year's return being filed by the s.139(1) due date,
    # which the engine cannot verify.
    conditional_on_timely_return: bool


@dataclass
class SetOffResult:
    buckets: dict
    steps: list = field(default_factory=list)
    carry_forward: list = field(default_factory=list)
    dead: list = field(default_factory=list)


def _absorb(pool: Decimal, label: str, targets: list, buckets: dict,
            rule_key: str, steps: list) -> Decimal:
    """Absorb `pool` against positive `targets` in order; returns the remainder."""
    remaining = pool
    for b in targets:
        if remaining <= 0:
            break
        if buckets[b] <= 0:
            continue
        take = min(remaining, buckets[b])
        buckets[b] -= take
        remaining -= take
        steps.append(SetOffStep(label, b, take, rule_key))
    return remaining


def apply_setoff(items: list, bf_losses: list, taxpayer: Taxpayer,
                 table: RuleTable, ay_ref_date: date,
                 normal_income: Decimal = Decimal("0")) -> SetOffResult:
    """Statutory set-off & carry-forward over classified income (Phase 2).

    Works per item (not from bucket_income totals) because s.115BBH(2)(b)
    quarantines each VDA loss individually — netting inside the VDA bucket
    would be an illegal set-off. NORMAL and VDA buckets are never reduced
    (s.71(3) / s.115BBH(2)(b)).
    """
    for bfl in bf_losses:
        if bfl.ay_incurred >= taxpayer.ay:
            raise OutOfScopeError(
                f"brought-forward loss dated AY {bfl.ay_incurred} is not earlier "
                f"than the current AY {taxpayer.ay}")

    order_rule = table.get("engine.cg_setoff_order", ay_ref_date)
    order = [Bucket(v) for v in order_rule.value]
    st_order = [b for b in order if b in _ST_BUCKETS]
    lt_order = [b for b in order if b in _LT_BUCKETS]

    buckets = {b: Decimal("0") for b in Bucket}
    buckets[Bucket.NORMAL] = normal_income
    steps: list = []
    dead: list = []
    carry: list = []

    vda_dead_rule = table.get("s115bbh.loss_setoff_disallowed", ay_ref_date)
    for i, it in enumerate(items):
        b, _ = classify(it, table, ay_ref_date)
        if isinstance(it, VdaItem) and it.gain < 0:
            dead.append(DeadLoss(
                f"item[{i}] VdaItem loss", -it.gain, vda_dead_rule.key,
                "s.115BBH(2)(b): VDA loss — no set-off, no carry-forward"))
            continue
        buckets[b] += it.gain

    # Current-year loss pools: negative CG buckets, zeroed as they're pooled.
    stcl = Decimal("0")
    ltcl = Decimal("0")
    for b in _ST_BUCKETS:
        if buckets[b] < 0:
            stcl += -buckets[b]
            buckets[b] = Decimal("0")
    for b in _LT_BUCKETS:
        if buckets[b] < 0:
            ltcl += -buckets[b]
            buckets[b] = Decimal("0")

    # s.70: LTCL first (restricted to LTCG, so it gets first claim), then STCL
    # against ST gains and only then LT gains. Never NORMAL (s.71(3)), never
    # VDA (s.115BBH).
    ltcl = _absorb(ltcl, "current-year LTCL", lt_order, buckets,
                   "s70.ltcl_setoff_ltcg_only", steps)
    stcl = _absorb(stcl, "current-year STCL", st_order + lt_order, buckets,
                   "s70.stcl_setoff_any_cg", steps)

    # s.74 brought-forward, oldest first, after current-year set-off (the ITR
    # BFLA-after-CYLA ordering).
    cf_years = table.get("s74.cf_years", ay_ref_date).value
    for bfl in sorted(bf_losses, key=lambda x: x.ay_incurred):
        label = f"b/f {bfl.kind.value.upper()} (AY {bfl.ay_incurred})"
        if not bfl.return_filed_by_due_date:
            dead.append(DeadLoss(
                label, bfl.amount, "s80.timely_return_required",
                "s.80: loss-year return not filed by the s.139(1) due date"))
            continue
        usable_through = bfl.ay_incurred + cf_years
        if taxpayer.ay > usable_through:
            dead.append(DeadLoss(
                label, bfl.amount, "s74.cf_years",
                f"s.74(2): lapsed — usable only through AY {usable_through}"))
            continue
        if bfl.kind is CFLossKind.STCL:
            rem = _absorb(bfl.amount, label, st_order + lt_order, buckets,
                          "s74.cf_stcl_setoff_any_cg", steps)
        else:
            rem = _absorb(bfl.amount, label, lt_order, buckets,
                          "s74.cf_ltcl_setoff_ltcg_only", steps)
        if rem > 0:
            # s.74(2): the loss is usable through ay_incurred + 8. Remainder
            # left after set-off in that last usable AY expires — it must not
            # reappear as carry_forward for a later year.
            if taxpayer.ay >= usable_through:
                dead.append(DeadLoss(
                    label, rem, "s74.cf_years",
                    f"s.74(2): unabsorbed remainder expires after last usable "
                    f"AY {usable_through}"))
            else:
                carry.append(CarryForwardOut(bfl.kind, bfl.ay_incurred, rem,
                                             usable_through, False))

    # Unabsorbed current-year losses carry forward from this AY (s.74(1)),
    # conditional on this year's return meeting s.80/139(3).
    for kind, rem in ((CFLossKind.STCL, stcl), (CFLossKind.LTCL, ltcl)):
        if rem > 0:
            carry.append(CarryForwardOut(kind, taxpayer.ay, rem,
                                         taxpayer.ay + cf_years, True))

    assert all(v >= 0 for v in buckets.values()), \
        "internal invariant violated: negative bucket after set-off"
    assert buckets[Bucket.NORMAL] == normal_income, \
        "internal invariant violated: s.71(3) — NORMAL bucket was touched"

    return SetOffResult(buckets=buckets, steps=steps, carry_forward=carry, dead=dead)


def trace_setoff(result: SetOffResult, table: RuleTable, ay_ref_date: date) -> Trace:
    """Render set-off applications through the existing Trace machinery.

    Amounts are negative: each line is a reduction of the bucket it names.
    Dead and carried losses live on SetOffResult, not here — they reduce no
    bucket.
    """
    tr = Trace()
    for s in result.steps:
        rule = table.get(s.rule_key, ay_ref_date)
        tr.add(TraceLine(s.loss_label, -s.amount, s.against, s.rule_key,
                         rule.source_primary, rule.confidence == "contested"))
    return tr
