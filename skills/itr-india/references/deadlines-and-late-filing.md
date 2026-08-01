# Deadlines, late-filing fee, and belated / revised returns

> Dates below are for **AY 2026-27 (FY 2025-26)**. Deadlines and extensions
> change every year and CBDT sometimes extends them close to the date — always
> re-confirm against incometax.gov.in before relying. This file exists because
> a return filed after the due date can cost a **s.234F fee**, **s.234A
> interest**, and — most expensively — the **right to carry forward losses**.

## The s.139(1) due dates

The **Finance Act 2026 substituted Explanation 2 to s.139(1)** to add a new
**31 August** tier. The date turns on the **type of income, not the ITR form**:

| Assessee (AY 2026-27) | Due date |
|---|---|
| **No** business/profession income — salaried, pensioner, investor (ITR-1/ITR-2, and an ITR-3 filed for a non-business reason) | **31 July 2026** |
| **Non-audit** business/profession income, and specified **partners** of such firms | **31 August 2026** |
| Accounts **require a tax audit** (s.44AB), and their partners | **31 October 2026** |
| Transfer-pricing (s.92E) cases | 30 November 2026 |

- **Verified (moved from "flag before relying").** This is a **permanent
  statutory change, not a departmental extension** — a substituted Explanation 2,
  effective for **AY 2026-27** (which is still governed by the Income-tax Act
  1961; the new Income-tax Act 2025 applies from FY 2026-27). Confirmed on the
  **Income Tax Department's own e-filing FAQ**: "For AY 2026-27 … the due date is
  31st July, 2026 or 31st August for non-audit cases" ([ITD, Income Tax Returns
  FAQ](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/%20income%20tax%20returns-faq)).
  The amended four-tier Explanation 2 is reproduced at [TaxGuru, AY 2026-27 ITR
  due dates under Finance Act 2026](https://taxguru.in/income-tax/ay-2026-27-itr-due-dates-finance-act-2026.html).
  The ultimate primary — the gazetted Finance Act 2026 / the Memorandum to the
  Finance Bill on [indiabudget.gov.in](https://www.indiabudget.gov.in/doc/memo.pdf) —
  is the enacting text but returns HTTP 403 to automated fetch; the ITD FAQ above
  is the fetched authority.
- **Watch the trigger — it is the income, not the form.** The 31 August tier is
  for someone who *has* non-audit business/profession income — **not** anyone who
  merely files ITR-3. A **director** or an **unlisted-share holder** with only
  salary/capital gains files ITR-3 but has **no** business income → their date is
  **31 July**. Conversely a **44ADA creator** or **44AD trader** (ITR-4/ITR-3)
  gets **31 August**. When in doubt, ask "does this person have business or
  profession income?" — that, not the form, sets the date.
- **s.234A follows the due date.** For a non-audit business filer the return-
  filing interest clock (below) now starts **1 September**, not 1 August — pass
  the correct `due_date` when computing s.234A (the engine takes it as input, it
  does not assume 31 July). CBDT can still extend any of these by circular near
  the date — re-confirm at filing time.
- A **resident and ordinarily resident with foreign assets/income** (or signing
  authority in a foreign account) must file a return **regardless of income
  level** — the seventh proviso to s.139(1) makes filing mandatory even below
  the taxable threshold (Schedule FA obligation). Source: [ClearTax, who must
  file an ITR](https://cleartax.in/s/who-should-file-itr).

## Section 234F — fee for late filing

If the return is filed **after** the s.139(1) due date:

- **₹5,000** if total income exceeds **₹5,00,000**;
- **₹1,000** if total income is **₹5,00,000 or less**;
- **no fee** if gross total income does not exceed the **basic exemption limit**
  (and the person is not otherwise required to file).

This fee is separate from, and on top of, any s.234A/B/C interest. Source:
[ClearTax, s.234F](https://cleartax.in/s/late-tax-return).

## Belated (s.139(4)) and revised (s.139(5)) returns

- **Belated return (s.139(4)):** if the due date is missed, the return can still
  be filed **up to 31 December 2026** (three months before the end of the AY),
  with the s.234F fee and s.234A interest.
- **Revised return (s.139(5)):** a return already filed can be revised, also up
  to **31 December 2026**. There is no fee to revise, but interest can change if
  the tax changes.
- After 31 December 2026 the ordinary window closes; only an **updated return
  (s.139(8A), ITR-U)** may remain, with additional tax — beyond a normal
  self-file; escalate.

## s.234A interest (late-filing interest)

s.234A charges **1% per month (or part month)** on the **unpaid** self-assessment
tax, from the day after the due date until the return is filed. **Tax already
paid on or before the due date does not attract 234A** even if the return is
filed late — the self-assessment tax paid by the due date reduces the base
(CIT v. Pranoy Roy (SC); CBDT Circular No. 2/2015). The tested engine encodes
this at `s234a.sat_before_due_date_reduces_base`. So: **pay the tax by the due
date even if the return itself will be a few days late** — it stops 234A.

## Losses die if the return is late — the carry-forward gate

This is the costly one. Under **s.80 read with s.139(3)**, a loss can be carried
forward to future years **only if the return claiming it is filed by the
s.139(1) due date**. Miss the due date and you lose the carry-forward of:

- **capital losses** (s.74 — STCL/LTCL),
- **business/profession loss** (s.72),
- **speculation loss** (s.73), and specified-business loss (s.73A).

**Exceptions that survive a belated return:**

- **house-property loss** (s.71B) — carries forward even if filed late;
- **unabsorbed depreciation** (s.32(2)) — governed by s.32, not s.80, so it
  carries forward regardless.

The engine models this gate at `s80.timely_return_required` /
`BroughtForwardLoss.return_filed_by_due_date`: a loss whose loss-year return was
**not** timely is treated as dead (no set-off, no carry-forward). Source:
[Income Tax Department, Set-off / carry-forward of losses](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/set-offcarry-forward-losses);
[TaxGuru, s.80 / 139(3)](https://taxguru.in/income-tax/loss-carried-forward-set-off-roi-filed-due-date.html).

> Practical upshot: if the user has a **capital loss or business loss to carry
> forward**, filing by the due date is not optional — a late return silently
> forfeits it. Surface this early, before the deadline, not after.
