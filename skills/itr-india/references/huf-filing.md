# HUF (Hindu Undivided Family) filing

An HUF is a **separate assessee** under s.2(31) of the Income Tax Act, with its
own PAN, its own return, and — for the most part — the same computational
machinery as an individual, with a handful of important exceptions below. Use
this file when the user is filing *for* an HUF (as Karta), not for themselves
as an individual who happens to also be a coparcener.

This is a real but minority use case relative to this skill's typical
salaried/freelancer/investor user — mainly families with ancestral property or
pooled investments held in the HUF's name. The clubbing and partition rules
below have genuine legal consequences beyond a simple return error, so lean on
asking questions over assuming.

## What's the same as an individual

- Same income heads (salary is uncommon for an HUF since it has no employer —
  see below — but house property, business/profession, capital gains, and
  other sources all apply the same way).
- Same slab rates, old vs new regime choice, and standard deduction structure.
- 80C, 80D (for HUF members), home-loan interest, and most Chapter VI-A
  deductions are available to an HUF the same way they are to an individual.

## What's different — and the ones most likely to be missed

- **No Section 87A rebate.** The rebate under s.87A is available only to a
  **resident individual** — an HUF gets none, regardless of total income. If
  the skill's usual tax-calc logic is reused unmodified for an HUF, it will
  wrongly apply a rebate the HUF isn't entitled to. This is the single biggest
  silent-error risk in treating an HUF like an individual.
  - Source: Income Tax Department FAQ on rebate u/s 87A (rebate scoped to
    resident individuals).
- **No 80CCD(2) employer NPS contribution.** An HUF has no "employer," so the
  employer-NPS-contribution deduction doesn't apply. (This follows directly
  from the provision's structure — it requires an employer contributing to an
  employee's NPS account — rather than from a specific HUF-targeted
  clarification; flag this to the user as a logical consequence, not a cited
  rule.)
- **No senior/super-senior slabs.** An HUF has no age, so it always uses the
  standard slab, never the senior-citizen ones — even if the Karta is a senior
  citizen.
- **Clubbing (s.64(2)).** Income from a **self-acquired property an individual
  converts or transfers into HUF property** (a common way people try to move
  income into the lower-taxed or more-deduction-friendly HUF) is **clubbed back
  into that individual's own income**, not taxed in the HUF's hands. This is an
  anti-avoidance rule and continues even after a subsequent partition of the
  property. Ask, specifically: did any HUF asset originate as an individual
  member's self-acquired property transferred into the HUF? If so, that
  income likely belongs on the transferring individual's own return, not the
  HUF's.
- **Partition (s.171).** An HUF continues to be assessed as an HUF **until the
  Assessing Officer records a total partition** — and **partial partitions
  after 31 December 1978 are not recognised at all** (s.171(9)). A family that
  believes it has informally split HUF property is still one taxable unit for
  return purposes unless there's a recorded total partition. Ask before
  assuming a "family settlement" or informal split changes who files what.

## Which ITR form

- **ITR-1 (Sahaj) is individual-only** — never applies to an HUF.
- **ITR-4 (Sugam), AY 2026-27:** available to a resident HUF with presumptive
  business/profession income (44AD/44ADA/44AE), total income ≤ ₹50L, and no
  other disqualifiers (same disqualifier checklist as for individuals — see
  `form-selection-ay2026-27.md`). HUF **is** eligible here — don't assume it's
  excluded.
  - Source: Income Tax Department, "Individual having Income from
    Business/Profession for AY 2026-2027"
    ([incometax.gov.in](https://www.incometax.gov.in/iec/foportal/help/individual-business-profession)),
    which scopes ITR-4 to "an Individual or Hindu Undivided Family (HUF)...
    having Income from Business and Profession which is computed on a
    presumptive basis."
- **ITR-2:** salary/other-source/capital-gains/house-property income, no
  business/profession income, or business income that doesn't fit ITR-4's
  presumptive/₹50L conditions.
- **ITR-3:** business/profession income that doesn't qualify for presumptive
  treatment or exceeds the ITR-4 conditions.

## Who signs

The **Karta** (or, in the Karta's absence, another adult coparecener with
authority) signs and verifies the return on the HUF's behalf. Confirm who is
acting as Karta for this filing before proceeding.

## What this file doesn't cover yet

- Partition mechanics and how to split carried-forward losses/depreciation
  between the pre- and post-partition units — not verified to this repo's
  citation standard yet; escalate to a professional if a partition (recognised
  or otherwise) is in play.
- Coparcener rights under the Hindu Succession Act as they interact with s.171
  — out of scope here; this file is about the *return*, not property law.
