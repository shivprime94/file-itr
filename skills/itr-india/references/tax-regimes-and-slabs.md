# Tax regimes, slabs, rebate, surcharge, cess

> Re-confirm the current assessment year's numbers from incometax.gov.in or the
> Finance Act before relying on them. Figures below are **FY 2025-26 (AY 2026-27)**
> and drift year to year. The same numbers are also hardcoded in `SKILL.md`'s
> "Verify the math" snippet and, with full citations, in
> `engine/rules/ay2026_27.py` — update all three together.

## The decision in one line

Compute total tax under **both** regimes on the person's actual numbers and pick
the lower one. The new regime wins when deductions are small; the old regime wins
when deductions are large. Don't reason from vibes — run both numbers.

## New regime (Section 115BAC) — the default

Default since FY 2023-24. Wider slabs, ₹75,000 standard deduction against salary,
but almost no other deductions/exemptions.

| Total income (FY 2025-26) | Rate |
|---|---|
| up to ₹4,00,000 | Nil |
| ₹4,00,001 – ₹8,00,000 | 5% |
| ₹8,00,001 – ₹12,00,000 | 10% |
| ₹12,00,001 – ₹16,00,000 | 15% |
| ₹16,00,001 – ₹20,00,000 | 20% |
| ₹20,00,001 – ₹24,00,000 | 25% |
| above ₹24,00,000 | 30% |

- **Standard deduction:** ₹75,000 against salary (once per person).
- **87A rebate (as amended by Finance Act 2025) — resident-only:** available
  only to a resident individual (a non-resident gets no 87A; see the old-regime
  87A note below for the source). Income chargeable at special
  rates under **111A / 112 / 112A** is excluded **both** from the ₹12,00,000
  eligibility test **and** from what the rebate can offset. So a filer with
  ₹11L slab income and ₹3L of 112A LTCG is still fully rebated on the ₹11L
  (nil slab tax), even though their *total* income is ₹14L — compare
  **slab-base** (normal + slab-rate STCG) against ₹12L, not total income.
  Marginal relief above that line uses the same slab-base figure. Sources for
  that reading address 111A/112/112A only (see `engine/rules/ay2026_27.py`
  `rebate.87a_new`). **VDA (s.115BBH)** is a separate Chapter-XII regime: this
  repo does **not** treat VDA as settled-excluded from the ₹12L test. If
  counting VDA toward the threshold would change the rebate, do not auto-
  rebate — check the portal / a primary source (the independent engine
  fails loud in that case rather than guessing).
- Slabs are the same regardless of age (no separate senior-citizen slabs in new
  regime).

## Old regime — slabs

Keeps all the popular deductions (see `deductions-old-regime.md`) but narrower
slabs and ₹50,000 standard deduction.

**Below 60 (and the default):**

| Total income | Rate |
|---|---|
| up to ₹2,50,000 | Nil |
| ₹2,50,001 – ₹5,00,000 | 5% |
| ₹5,00,001 – ₹10,00,000 | 20% |
| above ₹10,00,000 | 30% |

**Senior citizen (60–79):** first slab (nil) extends to **₹3,00,000**.
**Super senior (80+):** first slab (nil) extends to **₹5,00,000**.

> **Resident-only.** The ₹3,00,000 / ₹5,00,000 higher exemptions are available
> **only to a taxpayer resident in India**. Statutory authority is the Finance
> Act First Schedule, Part III, Paragraph A (the senior / super-senior
> paragraphs are worded for an individual *resident in India*). Verified via the
> Income Tax Department's [Non-Resident Individual, AY 2026-27](https://www.incometax.gov.in/iec/foportal/help/individual/return-applicable-0)
> page, which was fetched and states the NR rate is "same … **irrespective of
> date of birth of the taxpayer**" — i.e. a **non-resident** senior/super-senior
> gets the ordinary **₹2,50,000** exemption (old regime), whatever their age.
> (Note: the ITD's senior-citizen help page labels its slab chart "Individual
> (resident or non-resident)", which reads as a conflict; the NR page above and
> the statutory wording resolve it — the higher slab is resident-only.) This
> engine refuses non-resident computations outright (`engine/scope.py`); when
> computing by hand, don't hand an NR the senior slab.

- **Standard deduction:** ₹50,000 against salary.
- **87A rebate:** tax nil up to total income **₹5,00,000** in the old regime.
  **Resident-only** — a non-resident cannot claim the 87A rebate under either
  regime, at any income. Source: Income Tax Department,
  [Can a non-resident claim rebate under section 87A?](https://www.incometaxindia.gov.in/w/can-a-non-resident-claim-rebate-under-section-87a-)
  ("rebate under section 87A is available only to an individual who is resident
  in India, hence, non-residents cannot claim rebate under section 87A"). The
  same resident-only limit applies to the new-regime ₹60,000 rebate above.

## Common to both

- **Health & education cess:** 4% on (tax + surcharge).
- **Surcharge** (on income above thresholds): 10% above ₹50L, 15% above ₹1cr,
  25% above ₹2cr, 37% above ₹5cr — but the **new regime caps surcharge at 25%**.
  Marginal relief applies just past each threshold.
- **Special rates** (e.g., STCG 111A, LTCG 112A, lottery 115BB) apply in **both**
  regimes and sit on top of the slab tax; they don't get the 87A rebate.

## Form 10-IEA (the opt-out form for business filers)

A taxpayer with **business/profession income** is in the new regime by default and
must file **Form 10-IEA before the return due date** to choose the old regime.
Such a taxpayer can switch old→new once, but flip-flopping is restricted. A
taxpayer **without** business income simply ticks the regime in the return each
year and needs no 10-IEA. If a business filer is already past the due date with no
10-IEA on record, they're locked into the new regime for that year — say so.

## How to present the choice

Show the user two final numbers — "old regime total tax: ₹X" vs "new regime total
tax: ₹Y" — with the deductions assumed for the old-regime figure listed, so they
can see what they'd need to actually have. Then let them choose. If the gap is
small, mention that the new regime needs no deduction proofs and is simpler to
defend in scrutiny — a non-tax reason some people prefer it.
