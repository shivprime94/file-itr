---
name: itr-india
description: >-
  Assist a resident Indian individual with preparing and e-filing an Income Tax
  Return (ITR-1/2/3/4) on the e-filing portal (eportal.incometax.gov.in), under
  EITHER the old or new tax regime (non-resident / RNOR returns are out of
  scope). Use WHENEVER the user mentions filing taxes in India,
  ITR, income tax return, 26AS, AIS, Form 16, employment history, job change,
  multiple employers, old vs new regime, 115BAC, Form
  10-IEA, 80C/80D/HRA/home-loan/NPS/80G deductions, 44ADA/44AD presumptive,
  self-assessment/advance tax/234B/234C, TDS reconciliation, capital gains on
  Indian shares/mutual funds/property, or crypto/VDA (115BBH/194S) — even if they
  don't name the form or regime. Covers gathering and reconciling income documents, comparing both
  regimes to pick the cheaper one, choosing the form, computing tax, filling the
  portal schedule-by-schedule, fixing validation defects, and guiding payment and
  e-verification. India personal income tax only — not US/UK/other-country tax,
  GST, TDS-return (24Q/26Q), or company returns.
---

# Filing an Indian Income Tax Return (ITR)

## What this skill does and its boundaries

This skill turns Claude into a careful, methodical preparer for a **resident**
Indian individual's income tax return — salaried, freelancer/creator, small
business, investor, pensioner — under **either the old or the new regime**
(non-resident / RNOR returns, with their DTAA / Form 67 / Schedule FSI-TR
machinery, are out of scope — see step 1). The goal is a
return where **every rupee of income is reconciled to a source document**, the
**cheaper regime is chosen by actual computation (not guesswork)**, the tax math
is independently verified, and the user is walked cleanly through the portal up
to (but not including) the actions only they may legally perform.

Read this whole file first, then pull in the reference files under `references/`
as each phase demands. The references hold the detail; this file holds the
workflow and judgment.

**Hard boundaries — Claude must NOT do these; direct the user to do them:**

- Enter or handle the user's portal password, bank credentials, card numbers,
  OTPs, or any secret. Logging in is the user's job.
- Make the tax **payment** (e-Pay Tax / net-banking / UPI / card). State the
  exact amount and head; the user pays.
- Click the final **Submit** / **Proceed to e-Verify**, or enter the Aadhaar
  OTP / EVC. Submission and verification are the user's legal acts.
- Give a confident "you should buy this policy / invest in X to save tax"
  recommendation. Claude is not a chartered accountant or financial adviser —
  lay out the factual options and trade-offs and let the user decide. Say this
  plainly when it matters.

**Always tell the user up front:** rules change every assessment year, AIS/26AS
can be incomplete or wrong, and they remain responsible for the figures. This
skill makes the return *accurate and defensible*, and picks the regime that is
*cheaper for them on their actual numbers* — it does not minimise tax by claiming
things that aren't real.

## The workflow at a glance

1. **Establish the year and the person.** Confirm the Assessment Year (AY) and
   Financial Year (FY), residential status, age (senior-citizen slabs differ),
   and a rough picture of income sources. AY = FY + 1 (FY 2025-26 → AY 2026-27).
   **Check the due date now** (`references/deadlines-and-late-filing.md`): if it
   has passed, or is about to, the return is belated — flag the s.234F fee,
   s.234A interest, and especially that **any loss carry-forward is lost** on a
   late return. This is resident-individual India tax only — a **non-resident**
   return (NR/RNOR, DTAA relief, Form 67 foreign tax credit, Schedule FSI/TR) is
   **out of scope** here; the residency call in this step is a gate, not a
   formality.
2. **Employment history (if any salary).** Before asking for "the Form 16", build
   an FY timeline — see **Employment history** below and
   `references/multiple-form-16.md`. Job change, overlapping jobs, or mid-year
   join/exit → **one Form 16 per employer**; employment **gaps** do not need a
   Form 16 but may need other income questions.
3. **Gather every income document and every deduction proof.** Collect the Form
   16 count implied by step 2, Form 26AS, AIS/TIS, bank statements,
   broker/capital-gains statements, platform payout files — and, if old regime is
   in play, 80C/80D/home-loan/HRA/donation proofs.
4. **Reconcile income to sources.** The heart of the job — see
   `references/income-reconciliation.md`. One number per income head, each tied
   to a document.
5. **Compare both regimes and choose.** Compute total tax under **both** the old
   and new regimes on the actual numbers and pick the lower — subject to the
   Form 10-IEA constraint for business filers. See "Choosing the regime" below
   and `references/tax-regimes-and-slabs.md` + `references/deductions-old-regime.md`.
6. **Pick the ITR form.** See "Choosing the ITR form" below and
   `references/form-selection-ay2026-27.md`.
7. **Compute total income and tax independently** (a script — see "Verify the
   math") *before* trusting the portal, so you catch portal mistakes rather than
   the reverse.
8. **Fill the portal schedule-by-schedule**, confirming each. See
   `references/portal-workflow.md` for the quirks that otherwise cost hours.
9. **Resolve validation defects**, re-validate to zero errors.
10. **Hand off** payment, submission, and e-verification to the user, with the
    exact amount and the exact clicks.
11. **Verify the final preview / JSON** against your independent computation
    before the user submits.

Use a task list and a final verification step — a wrong ITR has real penalties.

## Employment history (ask before Form 16)

Whenever the user mentions **salary, payroll, employer, or Form 16**, ask for
**FY employment history** before assuming a single document. Users often mention
only their current employer and forget an earlier stint or a gap month.

**Ask:**

1. How many employers paid you salary in this FY (Apr–Mar)?
2. For each: employer name (no need for legal entity detail), **from** and **to**
   dates or months (joining, resignation, last working day).
3. Any period with **no salary** (between jobs, sabbatical, notice without pay,
   startup gap)? How long?
4. During any gap: freelance/consulting receipts, **full-and-final / settlement**
   from the old employer, or pension?
5. Any **two jobs at the same time** (main job + part-time on payroll)?

**Then:**

| Situation | Form 16 action |
|---|---|
| One employer, full FY | Ask for **one** Form 16 |
| Job change (sequential employers) | Ask for **one Form 16 per employer** |
| Two jobs at once | **Two Form 16s** (two TANs / two 192 entries in 26AS) |
| Mid-year join or exit (single employer) | Still usually **one** Form 16 from that employer for the part-year |
| Gap with no salary | **No** Form 16 for gap months — confirm no missing employer; ask about other income in the gap |

If they **changed jobs** or had **multiple employers**, explicitly say: *"Please
upload or paste Part A + Part B from **each** Form 16 — we need all of them, not
just the latest job."*

Optional engine check (after you have dates + Form 16 count):

```python
from datetime import date
from engine.form16 import (
    EmploymentStint, analyze_employment, employment_prompts,
    reconcile_form16s_to_employment, Form16Record,
)

stints = [
    EmploymentStint("Employer A", date(2025, 4, 1), date(2025, 6, 30)),
    EmploymentStint("Employer B", date(2025, 8, 1), date(2026, 3, 31)),
]
analysis = analyze_employment(stints, ay=2027, form16_records=[...])
for q in employment_prompts(analysis):
    print(q)
print(analysis.render_timeline())
print(reconcile_form16s_to_employment(analysis, [...]))
```

Gaps affect **HRA** (rent without HRA component), **80C** (EPF from two jobs),
and whether **AIS salary** matches only part of the year — not whether a second
Form 16 exists. See `references/multiple-form-16.md`.

## Aim: the lowest *legal* tax — claim everything they're entitled to

The objective is to minimise the user's tax **within the law** — never to invent
or inflate anything. Two things drive this, and the skill should pursue both
actively rather than passively accepting whatever the portal pre-fills:

1. **Pick the cheaper regime** by computing both (above).
2. **Claim every deduction/exemption the user genuinely has.** People routinely
   overpay because they don't realise an expense was deductible, or they forget a
   proof. So **proactively ask** what they have — don't wait for them to mention
   it. Walk them through the checklist below; for each item they have, get the
   number and the proof, and feed it into the old-regime comparison. If a claim
   isn't real or can't be substantiated, leave it out and tell them why.

### Documents / proofs to ask the user for

Always ask for the income documents after **employment history** (see above):
**all Form 16s** matching every employer in the FY, 26AS, AIS/TIS, bank statements,
broker statement, platform payouts). Then, to reduce tax, **ask specifically whether they have any
of these** (each can lower taxable income under the old regime — see
`references/deductions-old-regime.md`):

- **80C (up to ₹1.5L):** EPF/PF statement, PPF passbook, ELSS / mutual-fund tax
  saver, LIC/term-insurance premium receipts, children's school tuition fee
  receipts, home-loan principal certificate, NSC / 5-yr tax-saver FD, Sukanya
  Samriddhi.
- **NPS:** 80CCD(1B) extra ₹50k (own contribution) and 80CCD(2) (employer NPS —
  works in new regime too) — NPS statement.
- **80D health insurance:** premium receipts for self/family and for parents
  (higher limit if senior); preventive health check-up.
- **Home loan:** interest certificate from the lender (up to ₹2L self-occupied,
  Section 24(b)).
- **HRA / rent:** rent receipts and landlord PAN (if rent > ₹1L/yr), and the HRA
  component from the salary slip / Form 16.
- **80E:** education-loan interest certificate.
- **80G:** donation receipts with the donee's PAN and 80G reference.
- **80TTA/80TTB:** savings/FD interest (₹10k / ₹50k for seniors).
- **80EEB:** electric-vehicle loan interest. **80DD/80DDB/80U:** disability /
  specified-illness certificates.
- **Capital-loss / carry-forward statements:** prior-year losses can set off this
  year's gains and cut tax — ask if any exist.

After collecting, total the substantiated deductions, run the old-vs-new
comparison, and show the user the cheaper outcome with the assumptions listed. The
forward-looking "you should go buy X to save more next year" advice stays out of
scope (not financial-adviser territory) — but for *this* return, leave nothing
legitimate unclaimed.

## Choosing the regime (do the comparison, don't guess)

The **new regime (Section 115BAC) is the default** since FY 2023-24. It has wider
slabs and a ₹75,000 standard deduction but **removes almost all deductions/
exemptions** (80C, 80D, 80TTA, HRA, LTA, home-loan interest on self-occupied,
most of Chapter VI-A). The **old regime** keeps all those deductions but has
narrower slabs and a lower standard deduction (₹50,000).

There is no universal winner — it depends entirely on how much the person can
genuinely deduct:

- Little to claim (no big 80C/80D/HRA/home loan) → the new regime almost always
  wins.
- Substantial genuine deductions (full 80C + 80D + HRA + home-loan interest, NPS,
  etc.) → the old regime can win, sometimes by a lot.

So **compute both and show the user the two totals.** Two constraints to respect:

- A taxpayer with **business/profession income** must file **Form 10-IEA** before
  the due date to *opt out* to the old regime, and can switch back to new only
  once. If they're past the due date without 10-IEA, they're in the new regime by
  default — the choice may already be made.
- A taxpayer with **no business income** chooses the regime directly in the return
  each year, freely.

Slab tables, rebate, surcharge, and cess for both regimes are in
`references/tax-regimes-and-slabs.md`. The old-regime deduction catalogue (what to
collect and the limits) is in `references/deductions-old-regime.md`.

## Choosing the ITR form

Pick the simplest form that legally fits. Ask what applies; don't assume.

- **ITR-1 (Sahaj), AY 2026-27:** resident individual, total income ≤ ₹50L,
  salary/pension + up to two house properties + permitted other sources +
  agricultural income ≤ ₹5k. Aggregate LTCG u/s 112A up to ₹1.25L is permitted;
  STCG and other capital gains are not. No business income.
- **ITR-2:** salary + capital gains + multiple house properties + foreign assets,
  but **no** business/profession income.
- **ITR-4 (Sugam), AY 2026-27:** eligible resident with presumptive business/
  profession (44AD/44ADA/44AE), total income ≤ ₹50L, permitted salary/pension,
  up to two house properties and other sources. Aggregate LTCG u/s 112A up to
  ₹1.25L is permitted; STCG and other capital gains are not. Check all other
  disqualifiers.
- **ITR-3:** anyone with business/profession income who can't use ITR-4 — e.g.,
  presumptive income plus STCG/other disqualifying capital gains, 112A LTCG above
  ₹1.25L, actual books, or director/partner/unlisted-share holdings.

Common cases: a pure salaried person with up to two houses and some FD interest
may use **ITR-1**; add STCG or a disqualifying capital gain and they become
**ITR-2**; add freelance/creator/business income and they become **ITR-3** (or
ITR-4 when all simplified-form conditions hold). The common "salaried + creator
income + listed-share STCG" case is **ITR-3**. Do not generalise that result to
eligible 112A LTCG up to ₹1.25L, which AY 2026-27 ITR-4 permits.

## Income heads and where each goes

| Income | Schedule | Notes |
|---|---|---|
| Salary (each employer) | Schedule S | Gross 17(1); std deduction ₹75,000 (new) / ₹50,000 (old), once |
| House property | Schedule HP | Rent, municipal tax, 30% std deduction, home-loan interest (old regime) |
| Business/profession (presumptive) | Schedule BP + P&L item 62 (44ADA) / 61 (44AD) | See `references/creator-44ada.md` |
| Capital gains | Schedule CG | STCG/LTCG; STT-paid listed equity special-rated — `references/capital-gains-other-sources.md` |
| Interest, dividends | Schedule OS | 80TTA/80TTB only in old regime |
| Crypto / NFT (VDA) | Schedule VDA | Flat 30% u/s 115BBH, 1% TDS u/s 194S — `references/virtual-digital-assets.md` |
| Chapter VI-A deductions | Schedule VI-A | Mostly active only in old regime — `references/deductions-old-regime.md` |

## Verify the math (do this, every time)

After reconciliation, compute total income and tax **in a script** under both
regimes before and after the portal fills itself. The portal's auto-computation is
usually right, but you want an independent number to catch data-entry errors, to
choose the regime, and to explain every rupee to the user.

```python
# Slabs FY 2025-26 (AY 2026-27). Re-confirm the current year's slabs first.
# These numbers are also carried in references/tax-regimes-and-slabs.md (prose,
# for explaining the choice to the user) and, with full citations, in
# engine/rules/ay2026_27.py (a separate tested engine, not loaded by this
# skill). Update all three if a slab or rate changes.
def tax_new(x):
    slabs=[(400000,0),(800000,.05),(1200000,.10),(1600000,.15),
           (2000000,.20),(2400000,.25)]
    t=p=0
    for cap,r in slabs:
        if x>cap: t+=(cap-p)*r; p=cap
        else: return t+(x-p)*r
    return t+(x-2400000)*.30

def tax_old(x, age="below_60"):
    # age: "below_60" | "senior" (60-79, nil to 3L) | "super_senior" (80+, nil to 5L)
    # RESIDENT-ONLY: the ₹3L/₹5L senior/super-senior exemptions require the
    # taxpayer to be *resident in India* (Finance Act First Schedule Part III
    # Para A: "being a resident in India"). A NON-RESIDENT of any age gets the
    # ₹2,50,000 exemption — call this with age="below_60" for a non-resident
    # senior, and do NOT apply the 87A rebate (resident-only, see below).
    base = {"below_60": 250000, "senior": 300000, "super_senior": 500000}[age]
    if age == "super_senior":
        slabs = [(base, 0), (1000000, .20)]
    else:
        slabs = [(base, 0), (500000, .05), (1000000, .20)]
    t = p = 0
    for cap, r in slabs:
        cap = max(cap, p)
        if x > cap:
            t += (cap - p) * r
            p = cap
        else:
            return t + (x - p) * r
    return t + (x - 1000000) * .30

# Compute taxable income SEPARATELY per regime: old allows std ded 50k + Ch-VIA
# deductions; new allows std ded 75k and almost no deductions.
# Add special-rate items (e.g. STCG u/s 111A @ its rate) on TOP of slab tax,
# then add 4% health & education cess. Apply 87A rebate where eligible — the
# rebate is RESIDENT-ONLY (a non-resident gets no 87A at all, regardless of
# income) — new regime (Finance Act 2025): compare SLAB-ONLY income (excl.
# 111A/112/112A) to 12L, not total income; special-rate tax is never rebated.
# Whether VDA
# (s.115BBH) counts toward the 12L test is not settled here — if including
# VDA would change the rebate, do not auto-rebate; verify against the portal
# or a primary source. See tax-regimes-and-slabs.md.
```

Then reconcile against the portal's Part B-TTI line by line: gross tax, cess,
234B/234C interest, TDS, self-assessment tax, and the final amount payable. They
should match to the rupee (allowing the portal's nearest-₹10 rounding under
Section 288B).

## Declare income even when AIS doesn't show it

If a bank, platform, or payer did not report something to AIS/26AS (common with
smaller banks below the reporting threshold, or foreign platforms), the income is
**still taxable and still must be declared**. Omitting it is under-reporting and
exposes the user to a Section 270A penalty later. Surface the gap, explain it, and
include the income. Being thorough here protects them.

## The portal: fill, confirm, validate

The e-filing SPA has specific, repeatable quirks (logout pop-ups on navigation,
mat-select dropdowns that ignore coordinate clicks, a trailing-zero typing bug,
schedules that silently un-confirm when an upstream schedule is edited, and a
no-account-case balance-sheet defect that blocks presumptive returns). Each has a
known workaround. Before driving the portal, read `references/portal-workflow.md`
in full — it will save hours and prevent mis-clicks that corrupt a schedule.

Golden rule for browser automation here: **prefer a precise DOM/JS click on the
exact element over coordinate clicks**, because the page scroll position shifts
between screenshot and click. Confirm each schedule, and after editing any
schedule re-confirm everything downstream of it (especially Part B-TTI).

## Handing off — the user's three final acts

When the return validates with zero errors, stop and hand off clearly:

1. **Pay** the self-assessment tax (state exact amount + "Minor Head:
   Self-Assessment Tax (300)", AY). After payment the challan (BSR code, challan
   serial, date, amount) must appear in Schedule IT under "Advance Tax and Self
   Assessment Tax"; verify the amount payable then reads ₹0.
2. **Submit** the return (Proceed to Verification).
3. **e-Verify** — E-Verify Now via Aadhaar OTP / pre-validated bank is best; if
   "e-Verify Later", it must be verified within **30 days** or the filing is void.

Then have the user download the **ITR-V / acknowledgement** and keep it with the
challan and source documents.

## Reference files

- `references/tax-regimes-and-slabs.md` — old & new slabs, rebate, surcharge,
  cess, the regime decision, Form 10-IEA, senior-citizen slabs.
- `references/deductions-old-regime.md` — the old-regime deduction catalogue
  (80C, 80D, 80CCD/NPS, 80G, 80E, 80TTA/TTB, HRA, home-loan interest) with limits
  and what proof to collect.
- `references/income-reconciliation.md` — tying each income head to 26AS / AIS /
  bank statements / payout files, and handling mismatches.
- `references/multiple-form-16.md` — employment history, gaps, job change /
  concurrent employers: per-employer extraction, reconciliation table, TDS
  pitfalls, Schedule S portal rows, optional `engine/form16.py` helpers.
- `references/creator-44ada.md` — presumptive taxation for creators/freelancers
  /small business (44ADA vs 44AD), CBDT business codes, gross-receipts build,
  BP schedule, the no-account balance sheet.
- `references/capital-gains-other-sources.md` — STCG/LTCG on listed equity & MF
  & property, 111A/112A rates, quarterly breakup for 234C, interest/dividend.
- `references/virtual-digital-assets.md` — crypto/NFT (VDA) taxation: flat 30%
  u/s 115BBH, no loss set-off, 1% TDS u/s 194S, Schedule VDA reporting.
- `references/form-selection-ay2026-27.md` — AY-specific ITR-1/2/3/4 eligibility,
  including the ₹1.25L section 112A and two-house-property boundaries.
- `references/deadlines-and-late-filing.md` — s.139(1) due dates, s.234F late
  fee, belated/revised returns, s.234A interest, and the loss-carry-forward
  timely-return gate.
- `references/portal-workflow.md` — step-by-step portal navigation, every known
  quirk with its workaround, and the validation-defect catalogue.
