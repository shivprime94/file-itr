# Truthful-filing safeguards

This skill's mandate is the **lowest legal tax**, not the lowest possible number.
The two are usually the same request in different words, but occasionally a user
asks for something that only works by mis-stating a fact — the nature of a
payment, a date, a relationship, or an amount. This file is the checklist for
those moments: how to recognise them, and how to respond in a way that still
helps the user (explain the real exposure, offer the legitimate alternative)
without producing a return built on a false premise.

**Default posture: flag and ask, not refuse outright.** Most of these patterns
have a genuine version (a real consultant, a real rented flat, a real long
holding period) and a manufactured one, and the facts — not the user's
label — decide which. Ask the clarifying question, look at the source document,
and let the answer decide. Two patterns below are close to a hard line because
the "fact" is either a specific date on a broker statement or a specific entry
on 26AS/AIS — there's no legitimate ambiguity to ask about.

## 1. Salary dressed as consulting/professional income

**The ask:** "Can we file this as professional income under 44ADA instead of
salary?" — usually to avoid s.192 TDS visibility or to get the 50% presumptive
deduction 44ADA gives that salary doesn't.

**Why it matters:** s.15 charges salary income to tax on the basis of the
employer-employee relationship, not the label on the invoice or the TDS section
the payer used. Whether a relationship is employment or a professional
engagement is a **facts test** (control over hours/method, exclusivity, who
bears the business risk, whether the person can substitute someone else to do
the work) — not something either party gets to elect by choosing a TDS section.
Misclassifying it exposes the return to reassessment and a s.270A under-
reporting penalty (50% of the tax, 200% if the department treats it as
misreporting).

**What to check:** if the employment-history interview (see "Employment history"
above) already established a single payer with a fixed monthly amount and
employer-like language ("my company", "my manager"), but 26AS shows 194J/194C
instead of 192 for that payer — that's a salary-shaped fact pattern with a
non-salary TDS code. Ask: is there a written contract, does the payer set fixed
hours, is this the person's only client, can they send someone else to do the
work. If the facts say employment, file it as salary — explain why, and note
that the 44ADA presumptive rate doesn't apply to disguised employment even if
the payer's TDS entry says otherwise.

## 2. An AIS/26AS entry the user wants left off

**The ask:** "AIS shows this transaction — can we just not include it?" / "leave
that one out, it's not really income."

**Why it matters:** an entry with income and TDS attached (192/194C/194J/194-IB
etc.) is direct evidence of a payment to the PAN. A return that omits a
documented entry without any correction to the AIS record itself is filing
against known facts, not making a defensible income-classification judgment.
This is a **higher bar than the other items here** — SKILL.md already requires
declaring income *AIS is missing* (see "Declare income even when AIS doesn't
show it"); this is the mirror case, income AIS *has*, and it deserves the same
treatment.

**What to do:** don't drop it. If the user says the entry is wrong (duplicate,
joint-account mix-up, someone else's transaction under a shared PAN-linked
instrument), that's a real possibility — walk through `income-reconciliation.md`'s
mismatch section, and if it genuinely doesn't belong to them, that's a
correction to raise with the reporting entity / dispute on the AIS portal, not
a silent omission from the return. If the facts don't support "this isn't
mine," include it and explain the s.270A exposure of leaving it out.

## 3. HRA without a genuine landlord

**The ask:** claiming HRA exemption where the "landlord" is a spouse, parent, or
other family member living in the same household, often with no rent receipts
or bank trail.

**Why it matters:** s.10(13A) / Rule 2A exemption requires the rent to actually
be paid, and CBDT requires the landlord's PAN once annual rent exceeds ₹1L —
partly *because* rent-to-relative arrangements without a real payment trail are
a known abuse pattern. A same-household arrangement with no bank transfer and
no enforceable tenancy is thin on commercial substance, and it's the kind of
claim that surfaces on scrutiny.

**What to check:** who is the landlord, and is there an actual traceable
payment (bank transfer, not cash)? If rent > ₹1L/yr and there's no landlord PAN,
the exemption is deniable on the portal itself — say so before they claim it. If
the "landlord" is a spouse or parent who lives with the user (not a genuinely
separate household), ask more before including it: is there a real, ongoing
rent arrangement with its own paper trail, or is this being constructed for the
return? A family member can be a genuine landlord (e.g. a parent who owns the
flat and doesn't live there) — the test is the real arrangement, not the
relationship label.

## 4. Capital-gains holding period

**The ask:** "It's close to a year — can we call it long-term?" (or the
converse, dressing a genuine long holding as short-term to use a loss
differently).

**Why it matters:** the LTCG/STCG line is a **fact** — the buy date and sell
date on the broker statement, compared against the statutory holding period
(12 months for listed equity/equity MF, 24 months for unlisted shares/property,
36 months for most other assets pre-Finance-Act-2023 changes) — not a judgment
call the return can round in either direction. It changes the rate (111A/112A
vs slab) and the exemption (₹1.25L u/s 112A).

**What to do:** this is the closer of the two hard lines here. Always derive the
holding-period classification from the broker statement's transaction dates,
never from what the user says they'd prefer it to be. If the dates put it one
day short of the threshold, it's short-term — explain that, don't round it.

## 5. Inflated or undocumented 80G donations

**The ask:** a round-number donation claim, or a donation to a trust the user
can't otherwise describe, sometimes paired with a "cash-back" arrangement where
part of the donated amount effectively returns to the donor.

**Why it matters:** 80G requires an actual payment to a registered 80G entity,
with the donee's PAN and 80G approval reference — CBDT has cancelled 12A/80G
registration for a number of shell/bogus-donation trusts and reopened donor
assessments in those cases. A donation that comes back to the donor in cash
isn't a donation for tax purposes regardless of the receipt.

**What to check:** does the user have the donee's PAN and 80G registration
reference (not just a receipt)? Is any part of the amount returning to them?
80G also splits into 50%/100% and with/without a qualifying-limit categories
depending on the donee — don't assume full deduction without checking which
bucket the specific donee falls into (see `deductions-old-regime.md` for the
80G limits already documented there).

## What this file does not (yet) cover

These are real patterns too, but this skill doesn't currently collect the data
needed to check them, or the citation isn't yet verified to this repo's
standard — noted here so a future pass has a starting point, not implemented:

- **Agricultural-income exemption misuse** to shelter non-agricultural income —
  real CBDT enforcement target, but needs a verified section citation beyond
  s.10(1)/Rule 8 before it goes further than a mention.
- **Gift-clubbing avoidance** (s.56(2)(x), s.64) beyond what
  `income-reconciliation.md` already covers for minors/spouses — the relative-
  exemption list needs to be checked against current law before adding specific
  guidance here.
- **Cash-transaction structuring** to stay under SFT/26AS reporting thresholds,
  and **round-tripping losses** between related parties — both require
  cash-ledger or related-party transaction data this skill doesn't currently
  gather; not implementable without a data-collection change first.
