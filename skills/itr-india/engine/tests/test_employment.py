from datetime import date
from decimal import Decimal
import pytest
from engine.form16 import (
    EmploymentStint,
    Form16Record,
    analyze_employment,
    employment_prompts,
    fy_bounds_for_ay,
    reconcile_form16s_to_employment,
)


def test_fy_bounds_ay2027():
    start, end = fy_bounds_for_ay(2027)
    assert start == date(2025, 4, 1)
    assert end == date(2026, 3, 31)


def test_job_change_expects_two_form16s_and_detects_gap():
    stints = [
        EmploymentStint("Employer A", date(2025, 4, 1), date(2025, 6, 30)),
        EmploymentStint("Employer B", date(2025, 8, 1), date(2026, 3, 31)),
    ]
    analysis = analyze_employment(stints, ay=2027)
    assert analysis.expected_form16_count == 2
    assert analysis.changed_jobs
    assert len(analysis.gaps) == 1
    assert analysis.gaps[0].from_date == date(2025, 7, 1)
    assert analysis.gaps[0].to_date == date(2025, 7, 31)
    prompts = employment_prompts(analysis)
    assert any("separate Form 16s" in p for p in prompts)
    assert any("employment gap" in p for p in prompts)


def test_single_employer_full_year_one_form16():
    stints = [EmploymentStint("Only Co", date(2025, 4, 1), date(2026, 3, 31))]
    analysis = analyze_employment(stints, ay=2027, form16_records=[
        Form16Record("Only Co", gross_17_1=Decimal("100")),
    ])
    assert analysis.expected_form16_count == 1
    assert not analysis.changed_jobs
    assert analysis.gaps == ()
    assert analysis.missing_form16_count == 0


def test_missing_form16_prompt():
    stints = [
        EmploymentStint("A", date(2025, 4, 1), date(2025, 9, 30)),
        EmploymentStint("B", date(2025, 10, 1), date(2026, 3, 31)),
    ]
    analysis = analyze_employment(stints, ay=2027, form16_records=[
        Form16Record("A", gross_17_1=Decimal("1")),
    ])
    assert analysis.missing_form16_count == 1
    assert any("Still missing" in p for p in employment_prompts(analysis))


def test_reconcile_labels_mismatch():
    stints = [EmploymentStint("Employer A", date(2025, 4, 1), date(2026, 3, 31))]
    analysis = analyze_employment(stints, ay=2027)
    warnings = reconcile_form16s_to_employment(analysis, [
        Form16Record("Wrong Name", gross_17_1=Decimal("1")),
    ])
    assert any("missing for employer" in w for w in warnings)


def test_concurrent_employers():
    stints = [
        EmploymentStint("Main", date(2025, 4, 1), date(2026, 3, 31)),
        EmploymentStint("Side", date(2025, 6, 1), date(2026, 3, 31)),
    ]
    analysis = analyze_employment(stints, ay=2027)
    assert analysis.expected_form16_count == 2
    assert analysis.concurrent_employers
    assert any("Concurrent" in p for p in employment_prompts(analysis))


def test_nps_contribution_compliant_10_percent():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer A",
            gross_17_1=Decimal("1000000"),
            basic_salary=Decimal("700000"),
            employer_nps_contribution=Decimal("70000"),  # Exactly 10%
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027, is_government_employee=False, new_regime=False)
    assert len(flags) == 1
    assert flags[0].compliant
    assert flags[0].contribution_pct == Decimal("10.00")


def test_nps_contribution_exceeds_limit():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer B",
            gross_17_1=Decimal("1000000"),
            basic_salary=Decimal("700000"),
            employer_nps_contribution=Decimal("100000"),  # 14.3% — over 10% limit
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027, is_government_employee=False, new_regime=False)
    assert len(flags) == 1
    assert not flags[0].compliant
    assert flags[0].contribution_pct == Decimal("14.29")
    assert "exceeds" in flags[0].warning.lower()
    assert "taxable perquisite" in flags[0].warning.lower()


def test_nps_new_regime_14_percent():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer C",
            gross_17_1=Decimal("1000000"),
            basic_salary=Decimal("700000"),
            employer_nps_contribution=Decimal("98000"),  # 14% of 700k
        ),
    ]
    flags = verify_nps_contributions(records, ay=2026, is_government_employee=False, new_regime=True)
    assert len(flags) == 1
    assert flags[0].compliant
    assert flags[0].limit_pct == Decimal("14.00")


def test_nps_government_employee():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Ministry A",
            gross_17_1=Decimal("800000"),
            basic_salary=Decimal("500000"),
            employer_nps_contribution=Decimal("70000"),  # 14%
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027, is_government_employee=True)
    assert len(flags) == 1
    assert flags[0].compliant
    assert flags[0].limit_pct == Decimal("14.00")


def test_nps_multiple_employers_mixed_compliance():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer A",
            gross_17_1=Decimal("800000"),
            basic_salary=Decimal("500000"),
            employer_nps_contribution=Decimal("50000"),  # 10% — ok
        ),
        Form16Record(
            "Employer B",
            gross_17_1=Decimal("900000"),
            basic_salary=Decimal("600000"),
            employer_nps_contribution=Decimal("72000"),  # 12% — exceeds 10%
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027, is_government_employee=False, new_regime=False)
    assert len(flags) == 2
    assert flags[0].compliant
    assert not flags[1].compliant


def test_nps_no_contribution_skipped():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer A",
            gross_17_1=Decimal("1000000"),
            basic_salary=Decimal("700000"),
            employer_nps_contribution=Decimal("0"),  # No NPS
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027)
    assert len(flags) == 0  # Skipped


def test_nps_inferred_basic_when_missing():
    from engine.form16 import verify_nps_contributions
    records = [
        Form16Record(
            "Employer A",
            gross_17_1=Decimal("1000000"),
            basic_salary=None,  # Not provided — inferred as 65% of gross
            employer_nps_contribution=Decimal("65000"),  # 10% of inferred basic
        ),
    ]
    flags = verify_nps_contributions(records, ay=2027, is_government_employee=False, new_regime=False)
    assert len(flags) == 1
    # basic_salary_used should be 1000000 * 0.65 = 650000
    assert flags[0].basic_salary_used == Decimal("650000")
    assert flags[0].compliant  # 65000 is ~10% of 650000
    assert "assumed 65%" in flags[0].warning
