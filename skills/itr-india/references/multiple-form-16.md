# Multiple Form 16s (job change, concurrent employers)

Use this when the taxpayer has **more than one Form 16** in the same financial
year — common after a **job change**, **two employers at once** (main job +
consulting on payroll), or **part-year stints** with different TANs. Each
deductor issues its own Form 16; the return still has **one** salary head and
**one** standard deduction.

## Employment history first (agent checklist)

Do **not** ask for "your Form 16" until you know how many employers paid salary
in the FY. Walk the user through:

1. **Timeline** — for each job: employer (label), start date, end date within
   Apr–Mar.
2. **Job change?** If yes → **multiple Form 16s** (one per employer).
3. **Overlap?** Two payrolls in the same month → two Form 16s even without a
   "change" narrative.
4. **Gaps** — weeks/months with **no employer**:
   - No Form 16 is expected for gap months.
   - Ask whether any **salary-like** payment landed anyway (settlement after
     exit, advance from new employer, director sitting fees on 26AS).
   - Ask about **non-salary income** in the gap (freelance, consulting, 194J/
     194C in 26AS) — that goes to business/other heads, not a missing Form 16.
   - **HRA:** if they paid rent during a gap, old-regime HRA math may need the
     full-year rent working, not only the second employer's Form 16 exemption.
5. **Count check** — number of distinct employers in the FY should equal the
   number of Form 16 Part A/B sets you collect (use `engine.form16.analyze_employment`
   when you have dates).

```
Example — job change with gap (FY 2025-26)

  Apr 1 – Jun 30     Employer A     → Form 16 #1
  Jul 1 – Jul 31     (unemployed)   → no Form 16; ask about income / rent
  Aug 1 – Mar 31     Employer B     → Form 16 #2
```

## What to collect (per employer)

For **each** Form 16, pull from **Part B** (and cross-check Part A TDS against
Form 26AS section **192** for that deductor's TAN):

| Field | Form 16 label | Use |
|---|---|---|
| Gross salary | 17(1) | Schedule S — per employer row |
| Perquisites | 17(2) | Schedule S |
| Profit in lieu | 17(3) | Schedule S |
| Exemptions u/s 10 | Part B breakup (HRA, LTA, 10(10AA), …) | Schedule S — **per employer**; do not double-count |
| Professional tax | Deducted u/s 16(iii) if shown | Deduction u/s 16(iii) — **sum** across employers |
| TDS u/s 192 | Part A | Reconcile to 26AS; total TDS credit is **sum** of all 192 entries |
| Regime for TDS | Part B note (new vs old) | Informational only — employer TDS basis may differ from the regime you **choose** in the return (non-business filers pick regime in the ITR each year) |

Also ask for **salary slips** for months where Form 16 totals look wrong (joining/
exit month, bonus, RSU vest, leave encashment).

## Reconciliation table (build this before the portal)

```
Employer          TAN (last 4)   17(1)      17(2)   17(3)   u/s 10    PT(16iii)  TDS(192)   26AS 192
──────────────────────────────────────────────────────────────────────────────────────────────────────
Employer A        …XXXX          6,00,000   0       0       50,000    2,400      45,000     match
Employer B        …YYYY          9,00,000   20,000  0       1,20,000  2,400      1,10,000   match
──────────────────────────────────────────────────────────────────────────────────────────────────────
Totals                           15,00,000  20,000  0       1,70,000  4,800      1,55,000

Gross for salary head (Σ 17(1)+17(2)+17(3))              15,20,000
Less exemptions u/s 10 (Σ per Form 16, not re-derived)   −1,70,000
Less professional tax u/s 16(iii)                          −4,800
Income from salary before standard deduction             13,45,200

Less standard deduction (once): new ₹75,000 / old ₹50,000
Income chargeable under "Salaries" (before Chapter VI-A)   …
```

Chapter VI-A (80C, 80D, …) is **not** on Form 16 alone — collect proofs separately.
Form 16 may show **80C/80D figures the employer considered for TDS**; those do
**not** replace your own cap (e.g. combined 80C still max ₹1.5L across PF + ELSS +
LIC + …).

## Pitfalls specific to multiple employers

**1. Second employer's TDS math.** The later employer often folds the **earlier
employer's income** into its own withholding calculation, sometimes using the
earlier employer's **gross** rather than **net after u/s 10 exemptions** (e.g.
leave encashment already exempt at Employer A). That can **over-deduct TDS** — not
a portal error. Rebuild **total salary yourself** from both Form 16s; do not
trust either employer's "combined income" narrative. See
`income-reconciliation.md`.

**2. HRA across employers.** HRA exemption uses **salary defined u/s 17** for the
period you paid rent. If only Employer B paid HRA but Employer A paid most of
salary, you still need **rent receipts**, **landlord PAN** (if rent > ₹1L/yr), and
a **manual HRA working** for the full year — do not assume Employer B's Form 16
exemption alone covers the whole year unless the math says so.

**3. Duplicate 80C.** EPF from both jobs counts toward the **single** ₹1.5L 80C
limit. ELSS/LIC outside payroll is added on top until the cap is hit.

**4. 80CCD(2).** Employer NPS from **each** job counts within its own limit
(10% / 14% of salary from that employer); aggregate for return + new-regime
eligibility.

**5. AIS/26AS salary lines.** Expect **multiple** salary/TDS rows — one per TAN.
AIS may show one consolidated salary figure; always tie to **each** Form 16 + 192
entry.

**6. Section 89(1) / Form 10E.** If **any** employer paid **arrears**, advance
salary, or large leave encashment, ask about **89(1) relief** and **Form 10E**
(file **before** the return). See `income-reconciliation.md`.

## Portal — Schedule S (Salary)

1. Open **Schedule S** (or salary section in ITR-1 wizard).
2. **Add one row per employer** (name, TAN, address/nature of employer as required).
3. Enter **17(1), 17(2), 17(3)** and **exemptions u/s 10** exactly as on that
   Form 16 — do not merge employers into one row.
4. Enter **professional tax** u/s 16(iii) per row if the portal splits it; otherwise
   one combined figure matching the sum of Form 16s.
5. Confirm the portal's **total salary** matches your reconciliation table before
   standard deduction.
6. **Standard deduction** applies **once** at the salary schedule total — do not
   enter ₹75k/₹50k on each employer row.
7. Reconcile **Schedule TDS/TCS** (or TDS summary): each 192 entry → correct
   employer TAN and amount from 26AS.
8. After any edit to Schedule S, **re-confirm** downstream schedules (Part B-TI /
   Part B-TTI) — see `portal-workflow.md`.

## Independent check (optional helper)

The repo includes a small aggregator for reconciliation (not wired into
`compute()` — pass its `income_before_standard_deduction` into `normal_income`
after you add interest, business income, etc.):

```python
from decimal import Decimal
from datetime import date
from engine.form16 import (
    Form16Record, aggregate_form16s, EmploymentStint, analyze_employment,
    employment_prompts, reconcile_form16s_to_employment,
)
from engine.model import Regime

stints = [
    EmploymentStint("Employer A", date(2025, 4, 1), date(2025, 6, 30)),
    EmploymentStint("Employer B", date(2025, 8, 1), date(2026, 3, 31)),
]
records = [
    Form16Record("Employer A", gross_17_1=Decimal("600000"), ...),
    Form16Record("Employer B", gross_17_1=Decimal("900000"), ...),
]
analysis = analyze_employment(stints, ay=2027, form16_records=records)
employment_prompts(analysis)
reconcile_form16s_to_employment(analysis, records)
agg = aggregate_form16s(records, regime=Regime.NEW)
```

Run tests: `pytest skills/itr-india/engine/tests/test_form16.py skills/itr-india/engine/tests/test_employment.py -v`.
