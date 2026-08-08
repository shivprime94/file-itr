from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from engine.model import Regime


def fy_bounds_for_ay(ay: int) -> tuple[date, date]:
    """Financial year for assessment year `ay` (AY 2026-27 → FY 2025-04-01 … 2026-03-31)."""
    if ay < 2000:
        raise ValueError("ay looks invalid")
    start = date(ay - 2, 4, 1)
    end = date(ay - 1, 3, 31)
    return start, end


def _clip_stint(start: date, end: date, fy_start: date, fy_end: date) -> Optional[tuple[date, date]]:
    if end < fy_start or start > fy_end:
        return None
    return max(start, fy_start), min(end, fy_end)


def _merge_intervals(intervals: list[tuple[date, date]]) -> list[tuple[date, date]]:
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_iv[0]]
    for s, e in sorted_iv[1:]:
        prev_s, prev_e = merged[-1]
        if s <= prev_e + timedelta(days=1):
            merged[-1] = (prev_s, max(prev_e, e))
        else:
            merged.append((s, e))
    return merged


def _complement_gaps(fy_start: date, fy_end: date,
                     covered: list[tuple[date, date]]) -> list[tuple[date, date]]:
    merged = _merge_intervals(covered)
    gaps: list[tuple[date, date]] = []
    cursor = fy_start
    for s, e in merged:
        if s > cursor:
            gaps.append((cursor, s - timedelta(days=1)))
        cursor = max(cursor, e + timedelta(days=1))
    if cursor <= fy_end:
        gaps.append((cursor, fy_end))
    return gaps


@dataclass(frozen=True)
class EmploymentStint:
    """One employment period (dates inclusive). Synthetic labels only in tests."""

    employer_label: str
    from_date: date
    to_date: date

    def __post_init__(self):
        if self.to_date < self.from_date:
            raise ValueError("to_date is before from_date")
        if not self.employer_label.strip():
            raise ValueError("employer_label is required")


@dataclass(frozen=True)
class EmploymentGap:
    from_date: date
    to_date: date

    @property
    def days(self) -> int:
        return (self.to_date - self.from_date).days + 1


@dataclass(frozen=True)
class EmploymentAnalysis:
    ay: int
    fy_start: date
    fy_end: date
    stints_in_fy: tuple[EmploymentStint, ...]
    gaps: tuple[EmploymentGap, ...]
    expected_form16_count: int
    changed_jobs: bool
    concurrent_employers: bool
    form16_records_received: int
    missing_form16_count: int

    def render_timeline(self) -> str:
        lines = [
            f"== Employment FY {self.fy_start.year}-{str(self.fy_end.year)[-2:]} (AY {self.ay}) ==",
            f"expected Form 16 count: {self.expected_form16_count}",
            f"Form 16s provided: {self.form16_records_received}",
        ]
        for s in self.stints_in_fy:
            lines.append(f"  {s.from_date} → {s.to_date}: {s.employer_label}")
        if self.gaps:
            lines.append("gaps (no employment):")
            for g in self.gaps:
                lines.append(f"  {g.from_date} → {g.to_date} ({g.days} days)")
        else:
            lines.append("gaps: none within FY")
        return "\n".join(lines)


def analyze_employment(
    stints: list[EmploymentStint],
    *,
    ay: int,
    form16_records: Optional[list[Form16Record]] = None,
) -> EmploymentAnalysis:
    """Map FY employment to expected Form 16 count, job-change flag, and unpaid gaps."""
    fy_start, fy_end = fy_bounds_for_ay(ay)
    clipped: list[EmploymentStint] = []
    intervals: list[tuple[date, date]] = []
    employers: set[str] = set()

    for stint in stints:
        clip = _clip_stint(stint.from_date, stint.to_date, fy_start, fy_end)
        if clip is None:
            continue
        cs, ce = clip
        clipped.append(EmploymentStint(stint.employer_label, cs, ce))
        intervals.append((cs, ce))
        employers.add(stint.employer_label.strip())

    merged = _merge_intervals(intervals)
    gap_tuples = _complement_gaps(fy_start, fy_end, merged)
    gaps = tuple(EmploymentGap(a, b) for a, b in gap_tuples)

    expected = len(employers)
    received = len(form16_records or [])
    changed = expected > 1
    concurrent = len(clipped) > len(employers) or _has_overlap(clipped)

    return EmploymentAnalysis(
        ay=ay,
        fy_start=fy_start,
        fy_end=fy_end,
        stints_in_fy=tuple(clipped),
        gaps=gaps,
        expected_form16_count=expected,
        changed_jobs=changed,
        concurrent_employers=concurrent,
        form16_records_received=received,
        missing_form16_count=max(expected - received, 0),
    )


def _has_overlap(stints: list[EmploymentStint]) -> bool:
    for i, a in enumerate(stints):
        for b in stints[i + 1:]:
            if a.employer_label == b.employer_label:
                continue
            if a.from_date <= b.to_date and b.from_date <= a.to_date:
                return True
    return False


def employment_prompts(analysis: EmploymentAnalysis) -> list[str]:
    """Questions the agent should ask before reconciling salary."""
    prompts = [
        "For this financial year, list each employer with approximate join and exit "
        "dates (or months). Include any second job you held at the same time.",
    ]
    if analysis.expected_form16_count == 0:
        prompts.append(
            "You have no employment stints in this FY — confirm whether any salary "
            "or pension was received (Form 16, Form 16A, or 26AS section 192)."
        )
        return prompts

    if analysis.expected_form16_count == 1 and not analysis.gaps:
        prompts.append(
            "Confirm you had only one employer for the full financial year — you "
            "should have exactly one Form 16 for that deductor."
        )
    if analysis.changed_jobs or analysis.expected_form16_count > 1:
        prompts.append(
            f"You changed jobs or had multiple employers — collect **{analysis.expected_form16_count} "
            "separate Form 16s** (one per employer TAN), not a single combined PDF."
        )
    if analysis.missing_form16_count > 0:
        prompts.append(
            f"Still missing {analysis.missing_form16_count} Form 16(s) — request "
            "Part A + Part B from each employer before filing."
        )
    if analysis.gaps:
        longest = max(analysis.gaps, key=lambda g: g.days)
        prompts.append(
            f"There is an employment gap of about {longest.days} day(s) "
            f"({longest.from_date} to {longest.to_date}). A gap does **not** require "
            "a Form 16 — confirm: (1) no salary was paid in those months, "
            "(2) any freelance/consulting or notice-period/settlement pay, "
            "(3) rent/HRA still paid if claiming exemption for the full year."
        )
    if analysis.concurrent_employers:
        prompts.append(
            "Concurrent employers detected — expect multiple section-192 TDS lines "
            "in Form 26AS and one Form 16 from each deductor."
        )
    return prompts


@dataclass(frozen=True)
class Form16Record:
    """One employer's Form 16 Part B figures (synthetic / redacted only in tests)."""

    employer_label: str
    gross_17_1: Decimal
    perquisites_17_2: Decimal = Decimal("0")
    profit_in_lieu_17_3: Decimal = Decimal("0")
    section_10_exemptions: Decimal = Decimal("0")
    professional_tax: Decimal = Decimal("0")
    tds_192: Decimal = Decimal("0")
    tan: Optional[str] = None
    # Optional: tie to employment history (must fall within the stint in FY).
    employment_from: Optional[date] = None
    employment_to: Optional[date] = None
    # NPS verification: employer contribution to NPS per Form 16 Part B (if itemized).
    employer_nps_contribution: Decimal = Decimal("0")
    # Basic salary (or None if only gross available — caller infers from gross).
    basic_salary: Optional[Decimal] = None

    def __post_init__(self):
        for name, val in (
            ("gross_17_1", self.gross_17_1),
            ("perquisites_17_2", self.perquisites_17_2),
            ("profit_in_lieu_17_3", self.profit_in_lieu_17_3),
            ("section_10_exemptions", self.section_10_exemptions),
            ("professional_tax", self.professional_tax),
            ("tds_192", self.tds_192),
            ("employer_nps_contribution", self.employer_nps_contribution),
        ):
            if val < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True)
class Form16Aggregation:
    gross_17_1: Decimal
    perquisites_17_2: Decimal
    profit_in_lieu_17_3: Decimal
    section_10_exemptions: Decimal
    professional_tax: Decimal
    total_tds_192: Decimal
    income_before_standard_deduction: Decimal
    standard_deduction: Decimal
    income_after_standard_deduction: Decimal
    employer_count: int

    def render_table(self) -> str:
        lines = [
            "== Form 16 aggregation (reconciliation) ==",
            f"employers: {self.employer_count}",
            f"Σ 17(1): {self.gross_17_1}",
            f"Σ 17(2): {self.perquisites_17_2}",
            f"Σ 17(3): {self.profit_in_lieu_17_3}",
            f"Σ u/s 10 exemptions: {self.section_10_exemptions}",
            f"Σ professional tax u/s 16(iii): {self.professional_tax}",
            f"income before std deduction: {self.income_before_standard_deduction}",
            f"standard deduction ({self.standard_deduction}): -{self.standard_deduction}",
            f"income after std deduction: {self.income_after_standard_deduction}",
            f"Σ TDS u/s 192 (26AS check): {self.total_tds_192}",
        ]
        return "\n".join(lines)


def _std_deduction(regime: Regime) -> Decimal:
    return Decimal("75000") if regime is Regime.NEW else Decimal("50000")


def reconcile_form16s_to_employment(
    analysis: EmploymentAnalysis,
    records: list[Form16Record],
) -> list[str]:
    """Warnings when Form 16 count or employer labels don't match stated history."""
    warnings: list[str] = []
    if not records and analysis.expected_form16_count:
        warnings.append(
            f"Employment history implies {analysis.expected_form16_count} Form 16(s); none supplied yet."
        )
        return warnings
    if len(records) != analysis.expected_form16_count:
        warnings.append(
            f"Form 16 count mismatch: history implies {analysis.expected_form16_count}, "
            f"received {len(records)}."
        )
    history_employers = {s.employer_label.strip().lower() for s in analysis.stints_in_fy}
    form16_employers = {r.employer_label.strip().lower() for r in records}
    missing = history_employers - form16_employers
    extra = form16_employers - history_employers
    if missing:
        warnings.append(
            "Form 16 missing for employer(s) from history: "
            + ", ".join(sorted(missing))
        )
    if extra:
        warnings.append(
            "Form 16 provided for employer(s) not in stated history: "
            + ", ".join(sorted(extra))
        )
    return warnings


def aggregate_form16s(records: list[Form16Record], *, regime: Regime) -> Form16Aggregation:
    """Sum multiple Form 16 Part B rows; apply one salary standard deduction.

    Does not apply Chapter VI-A, house property, or other heads — only the salary
    reconciliation an agent does before calling `compute(..., normal_income=...)`.
    """
    if not records:
        raise ValueError("at least one Form16Record is required")

    g1 = sum((r.gross_17_1 for r in records), Decimal("0"))
    g2 = sum((r.perquisites_17_2 for r in records), Decimal("0"))
    g3 = sum((r.profit_in_lieu_17_3 for r in records), Decimal("0"))
    ex = sum((r.section_10_exemptions for r in records), Decimal("0"))
    pt = sum((r.professional_tax for r in records), Decimal("0"))
    tds = sum((r.tds_192 for r in records), Decimal("0"))

    gross = g1 + g2 + g3
    before_std = gross - ex - pt
    if before_std < 0:
        raise ValueError("salary income before standard deduction is negative — check inputs")

    std = _std_deduction(regime)
    after_std = max(before_std - std, Decimal("0"))

    return Form16Aggregation(
        gross_17_1=g1,
        perquisites_17_2=g2,
        profit_in_lieu_17_3=g3,
        section_10_exemptions=ex,
        professional_tax=pt,
        total_tds_192=tds,
        income_before_standard_deduction=before_std,
        standard_deduction=std,
        income_after_standard_deduction=after_std,
        employer_count=len(records),
    )


@dataclass(frozen=True)
class NpsContributionFlag:
    """NPS 80CCD(2) verification for a single Form 16."""

    employer_label: str
    employer_nps_contribution: Decimal
    basic_salary_used: Decimal  # Inferred or supplied.
    contribution_pct: Decimal  # Actual contribution as % of basic.
    limit_pct: Decimal  # Regulatory limit (10% or 14%).
    compliant: bool  # True if contribution <= limit_pct of basic.
    warning: str = ""  # If non-compliant, a prompt for agent review.


def verify_nps_contributions(records: list[Form16Record],
                             *,
                             ay: int = 2027,
                             is_government_employee: bool = False,
                             new_regime: bool = False) -> list[NpsContributionFlag]:
    """Cross-check NPS contribution compliance u/s 80CCD(2) across all Form 16s.

    For each Form 16: verify employer's NPS contribution does not exceed limit % of basic salary.
    Rules:
    - Government employee: 14% of (basic + DA per terms of employment).
    - Non-government, old regime: 10% of basic.
    - Non-government, new regime (115BAC(1A)): 14% of basic (effective FY 2025-26).

    Args:
        records: List of Form16Records with employer_nps_contribution and optional basic_salary.
        ay: Assessment year (for future-proofing; rule limits may change).
        is_government_employee: If True, apply 14% limit; else apply 10% (old) or 14% (new, from FY2025-26).
        new_regime: If True and not govt, apply 14%; else 10%.

    Returns:
        List of NpsContributionFlag per employer. Agent should review any with compliant=False.
    """
    flags: list[NpsContributionFlag] = []
    limit = Decimal("0.14") if (is_government_employee or (new_regime and ay >= 2026)) else Decimal("0.10")

    for rec in records:
        if rec.employer_nps_contribution == Decimal("0"):
            continue

        basic = rec.basic_salary
        if basic is None:
            # Infer basic from gross minus allowances. Safe estimate: basic ≈ 60-70% of gross 17(1).
            # If user provides Form 16 salary slip breakdown, use that. For now, flag as needing clarification.
            basic = rec.gross_17_1 * Decimal("0.65")  # Conservative 65% assumed ratio.
            warning_msg = (
                f"Basic salary not provided for {rec.employer_label}; assumed 65% of gross "
                f"({basic}). Ask user for salary slip to confirm breakdown."
            )
        else:
            warning_msg = ""

        actual_pct = (rec.employer_nps_contribution / basic * Decimal("100")).quantize(Decimal("0.01"))
        limit_pct_decimal = (limit * Decimal("100")).quantize(Decimal("0.01"))
        compliant = rec.employer_nps_contribution <= basic * limit

        if not compliant:
            warning_msg = (
                f"{rec.employer_label}: employer NPS contribution ₹{rec.employer_nps_contribution} "
                f"is {actual_pct}% of basic ₹{basic} — exceeds {limit_pct_decimal}% limit "
                f"({basic * limit}). Excess {rec.employer_nps_contribution - basic * limit} is taxable perquisite. "
                f"Cross-check: (1) Form 16 Part B NPS line, (2) salary slip breakdown (basic vs allowances), "
                f"(3) whether employer communicated amended Form 16 if excess was corrected."
            )

        flags.append(NpsContributionFlag(
            employer_label=rec.employer_label,
            employer_nps_contribution=rec.employer_nps_contribution,
            basic_salary_used=basic,
            contribution_pct=actual_pct,
            limit_pct=limit_pct_decimal,
            compliant=compliant,
            warning=warning_msg,
        ))

    return flags
