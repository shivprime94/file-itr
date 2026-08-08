# Driving the e-filing portal (and its quirks)

Portal: `https://eportal.incometax.gov.in`. The return-filing UI is a single-page
Angular app. It is functional but has several repeatable traps that will waste
hours if you don't know them. This file is the field guide.

## Ground rules

- **The user logs in.** Never handle their password or OTP. Ask them to log in
  and reach the dashboard, then take over the form-filling.
- **Two browsers / extension issues:** if more than one browser is connected,
  ask the user which one to use before acting (don't guess which tab is theirs).
- **Compute first, then fill.** Have your independent tax number ready so you can
  catch the portal, not the reverse.
- **Confirm every schedule**, and after editing any schedule, **re-confirm every
  schedule downstream of it** — editing an upstream schedule silently flips
  Part B-TI / Part B-TTI back to "Provide your confirmation".

## High-level filing flow

1. e-File → Income Tax Returns → File Income Tax Return → select AY → select
   "Online" → select ITR-3 (or correct form) → reason for filing.
2. The portal pre-fills from AIS/26AS. **Verify the pre-fill against your
   reconciliation** — accept what's right, fix what's wrong, add what's missing.
3. Go through "Return Summary": open each schedule, fill, **Confirm**.
4. **Proceed to Verification** → preview → upload-level **Validation**.
5. Fix any defects, re-validate to **0 errors**.
6. Hand off: Pay → Submit → e-Verify (all user actions).

## The quirks, each with its workaround

**Logout pop-up on navigation.** Navigating by URL throws "Are you sure you want
to Logout?". Click **No** to stay. (Breadcrumb links usually navigate without the
pop-up — prefer them.)

**Coordinate clicks land on the wrong row.** The page scroll position shifts
between the screenshot and the click, so a click aimed at row Y often hits a
different row (e.g., aiming at "Part B-TTI / Provide your confirmation"
repeatedly opened Schedule AMTC instead). **Workaround: click the exact element
via DOM/JS, not coordinates.** Find the row's container (each schedule is an
`<li class="list-group-item">`), then click its confirmation/label element
directly. Example:

```js
// Confirm Part B-TTI reliably:
const li = [...document.querySelectorAll('li.list-group-item')]
  .find(x => /Tax Liability on Total Income/.test(x.textContent)
          && /Provide your confirmation/.test(x.textContent));
(li.querySelector('p.provide_confirm_label') || li).click();
```

Also dismiss the logout modal via JS when it blocks:
`[...document.querySelectorAll('button,span,div')].find(b=>b.textContent.trim()==='No')?.click();`

**mat-select dropdowns ignore clicks.** The Angular Material dropdowns (nature of
employer, business code, etc.) often don't register a coordinate click on an
option. **Workaround:** focus the control, then use keyboard — `ArrowDown` to the
option, `Return` to select; or scroll the option list and click the option text.

**Trailing-zero typing bug.** Amount fields are pre-filled with `0`. Typing
`22930` into them yields `229300` (the old 0 sticks). **Workaround:**
triple-click the field (and/or Ctrl+A, Delete) to clear it *before* typing.

**Schedules silently un-confirm.** Editing Part A-BS, Salary, etc. flips
Part B-TI/Part B-TTI back to unconfirmed. After any edit, walk back down and
re-confirm. Part B-TTI confirmation also routes through Schedule AMT/AMTC
recompute — confirm AMTC if asked, then confirm Part B-TTI.

**Auto-added schedules with mandatory blanks.** The portal may auto-add ESOP /
other schedules with mandatory fields (PAN/DPIIT) that don't apply. Remove them
via "Select Schedule" if not applicable; use "Skip Questions" to stop the
questionnaire from re-adding them and from resetting answers like
"income from business = Yes".

**Session timeout.** Long sessions log out mid-fill. The user re-logs in and
clicks "Resume Filing"; confirm the in-progress data survived.

## The validation-defect catalogue (and fixes)

When "Proceed to Verification" runs the **Upload Level Validation**, it lists
"Category of Defect A" errors that *block* upload. The common ones:

- **"Income under section 44AD/44ADA/44AE is greater than zero → fill Sl.No 6 of
  Part-A BS."** The presumptive no-account balance sheet (item 6) is empty.
  **Fix:** open Part A – Balance Sheet → expand item 6 (no books of account) →
  enter a positive **cash balance** (debtors/creditors/stock can be 0) → Confirm.
  A clean, defensible cash-balance figure is the net presumptive profit. This is
  disclosure only and does not change the tax.
- **"Kindly enter the respective business code for the income declared u/s
  44ADA/44AD."** The Name of Business/Profession, Business Code, and Description
  fields aren't shown by default on the presumptive-income screen — they sit in
  a sub-form that only appears after clicking **"Add Another"** under the
  44AD/44ADA/44AE computation block, which reads like "register a second
  business" rather than "the required field is hidden here." **Fix:** click
  **Add Another** even when there is only one business/profession, fill Name,
  Business Code (see `creator-44ada.md` for the code list), and Description,
  then Save — the presumptive amount is unaffected. Confirmed on ITR-4 (Sugam);
  check whether the ITR-3 Schedule BP screen has the same pattern before relying
  on this there.
- **Secondary address / employer-nature dropdowns blank.** Set "Nature of
  employer = Others" for non-government salary; fill the secondary address if the
  user has one different from the primary.

## Schedule S — more than one Form 16

When the user has **multiple employers** in the year, Schedule S needs **one
employer block per Form 16/TAN** — not one combined row.

1. Reconcile on paper first (`references/multiple-form-16.md`).
2. Add each employer with TAN, 17(1)/17(2)/17(3), and that employer's u/s 10
   exemptions exactly as on its Form 16.
3. Apply **standard deduction once** on the salary total (portal usually does this
   at the schedule level — do not duplicate per row).
4. Match **each** 26AS section-192 entry to the same TAN in the TDS schedule.
5. After saving Schedule S, re-confirm Part B-TI and Part B-TTI (silent
   un-confirmation — see above).
- **Empty mandatory breakup rows.** Delete blank ₹0 perquisite (17(2)) /
  profit-in-lieu (17(3)) rows that carry blank mandatory dropdowns.

After fixing, re-run validation until it reports **0 errors**. The portal will
then offer **Pay Now / Pay Later**, then the **Complete your Verification**
screen.

## Verifying the final return

Before the user submits, read the **PDF preview** (or the downloadable **JSON**)
and reconcile every key figure against your independent computation:

- total income, income per head;
- gross tax, cess, special-rate tax;
- 234B + 234C interest;
- TDS + self-assessment challan = total taxes paid;
- each TDS entry's **Head of Income** tag matches the income head it's actually
  credited against (e.g. 194J TDS feeding presumptive business income should be
  tagged "Business/Profession," not left on the portal's "Other Sources"
  default) — this doesn't necessarily block Upload Level Validation, but a
  mismatched tag misaligns the credit from the income it belongs to;
- amount payable should be **₹0** after payment (a few-rupee gap is just the
  nearest-₹10 rounding under Section 288B);
- regime flag, residential status, bank accounts, foreign-asset flag,
  verification name/PAN.

The downloadable JSON is the authoritative artifact — if it matches your numbers,
the return is correct. Only then hand off to the user for Pay / Submit / e-Verify.

## After payment — recording the challan

When the user pays self-assessment tax, the challan must land in **Schedule IT**
("Advance Tax and Self Assessment Tax"): BSR code, date of deposit, challan
serial, amount. If paid via the portal's "Pay Now" it auto-populates; if paid
separately, add it manually, then confirm Tax Paid. Verify Part B-TTI "Amount
payable" then reads ₹0.
