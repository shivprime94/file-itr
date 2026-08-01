# Deadlines, late-filing fee, and belated / revised returns

> Dates below are for **AY 2026-27 (FY 2025-26)**. Deadlines and extensions
> change every year and CBDT sometimes extends them close to the date — always
> re-confirm against incometax.gov.in before relying. This file exists because
> a return filed after the due date can cost a **s.234F fee**, **s.234A
> interest**, and — most expensively — the **right to carry forward losses**.

## The s.139(1) due dates

| Who | Due date, AY 2026-27 |
|---|---|
| Individual **not** liable to audit (ITR-1 / ITR-2, salaried, etc.) | **31 July 2026** |
| Taxpayer whose accounts require a **tax audit** (and partners of such firms) | **31 October 2026** |

- **31 July** is the long-standing statutory default for an individual not
  subject to audit — treat it as the operative date unless you have verified
  otherwise.
- **Unverified — flag, do not assume:** several secondary sources report a
  Finance Act 2026 change giving **non-audit ITR-3 / ITR-4** filers until
  **31 August 2026** (a tiered structure, with ITR-1/ITR-2 still at 31 July).
  This was **not corroborated on the Income Tax Department's own site** when this
  file was written. Per this repo's citation discipline, **do not rely on the
  31-August date until you confirm it against the actual CBDT notification or
  the gazetted Finance Act 2026 text** — assume 31 July if unsure. If the user
  is filing near the deadline, tell them plainly that this specific date needs
  checking.
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
