# Presumptive taxation for creators & freelancers (44ADA / 44AD)

Content creators, freelancers, consultants, and independent professionals can
usually declare income **presumptively**, avoiding books of account and audit if
they stay within the limits. This is almost always the right choice for a
small/medium creator.

## 44ADA vs 44AD — pick the right one

- **Section 44ADA (profession):** for *specified professions* and, importantly,
  the CBDT notified-profession codes that include creators. Presumptive income =
  **50%** of gross receipts. Limit: gross receipts up to **₹50L** (₹75L if ≤5%
  of receipts are in cash). The relevant business code for online creators is
  **16021 – "Social media influencers"** (a *profession* code). 44ADA is not
  limited to creators — other notified professions each have their own code,
  e.g. **16005** (engineering and technical consultancy), **16002** (accounting,
  book-keeping and auditing), **16003** (tax consultancy), **14002** (other
  software consultancy), **16013** (business and management consultancy). Match
  the code to the actual nature of the work rather than the nearest-sounding
  option; the Description field takes free text if no notified code fits.
- **Section 44AD (business):** for eligible businesses (traders, small biz).
  Presumptive income = **8%** of receipts, or **6%** for receipts via banking/
  digital channels. Limit: turnover up to ₹2cr (₹3cr if ≤5% cash).

**Critical gotcha:** code **16021 is a profession code and appears only under the
44ADA dropdown**, not the 44AD one. If you start under 44AD you will not find
16021 and will be tempted to mis-classify. For a social-media creator, choose
**44ADA + 16021** and declare 50%. It is the cleaner, lower-audit-risk fit for
profession income, even though 44AD's 6% would show a lower number — don't pick a
section just because its percentage is smaller; pick the one that legally fits.

## Building gross receipts

Gross receipts = every rupee earned from the activity in the FY:

- platform payouts (Stripe/YouTube/X/PayPal/brand deals), summed from the payout
  files **and** confirmed against bank credits, plus
- any TDS-deducted contract/professional receipts visible in 26AS (194C/194J).

Avoid double counting: a payout already captured inside a 26AS entry counts once.

```
# Illustrative figures only.
Contract receipt (26AS 194C)      20,000
Platform payouts (bank-confirmed) 30,000
Gross receipts (44ADA 62i)        50,000
Presumptive income @ 50% (62ii)   25,000
```

## Where it goes in ITR-3

- **Part A – P&L, item 62** (44ADA): enter business code 16021, gross receipts
  (62i, split by mode a/b/c), and presumptive income 62ii (50%, or higher if the
  user genuinely earned more — 50% is the floor, not a cap).
- **On ITR-4 (Sugam):** the presumptive block lives under Gross Total Income →
  B1 Income from Business & Profession → Presumptive Income from Profession
  u/s 44ADA. The Name of Business/Profession, Business Code, and Description
  fields aren't visible by default there — see the hidden-field quirk in
  `portal-workflow.md`.
- **Schedule BP**: the presumptive income flows to BP item 35ii (44ADA) → A37 →
  D ("Income chargeable under PGBP"). It should equal the 50% figure.
- **Part A – Balance Sheet, item 6 (no-account case):** because income is
  declared presumptively with no books, you **must** fill the "no books of
  account" block — sundry debtors, sundry creditors, stock-in-trade, and **cash
  balance**. Leaving all four at zero triggers a **validation defect** that
  blocks the return (see `portal-workflow.md`). For a service creator with no
  inventory: debtors/creditors/stock = 0, and put a sensible positive **cash
  balance** (the net profit retained is a clean, defensible figure). This is a
  disclosure field; it does not change the tax.

## If receipts exceed the presumptive limit, or profit is genuinely below the %

- Above ₹50L (44ADA) / ₹2cr (44AD): presumptive is unavailable; the user needs
  regular books and possibly a 44AB tax audit — escalate, this is beyond a quick
  self-file.
- If the user's real profit is **below** 50% / 8%, declaring the lower actual
  profit requires maintaining books and a tax audit. Most small creators simply
  declare the presumptive % and move on.

## Advance tax: one instalment for 44AD / 44ADA

A taxpayer declaring profits under **section 44AD(1) or 44ADA(1)** does not use
the ordinary June/September/December/March advance-tax percentages. The whole
advance-tax liability is due by **15 March**. A shortfall at that date attracts
section 234C interest for one month; section 234B can still apply after year-end.

This concession is specific to 44AD and 44ADA. Do not extend it to section 44AE
merely because 44AE is also a presumptive scheme used in ITR-4.

Sources: Income Tax Department,
[advance-tax FAQ](https://www.incometaxindia.gov.in/w/who-is-not-required-to-pay-advance-tax-)
and [Finance Act 2017 amendment of section 234C](https://www.incometaxindia.gov.in/w/section-75-86).
