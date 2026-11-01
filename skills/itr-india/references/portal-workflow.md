# Portal entry, recovery and filing handoff

Portal: <https://eportal.incometax.gov.in>. Use the live UI and the current
assessment year's official instructions. These observations are fallbacks, not
permanent screen layouts. Read this before entering or resuming a return.

## Before entry

- Read [collection-and-coverage.md](collection-and-coverage.md). Batch report
  downloads while logged in, reconcile locally, then start the next portal batch.
- Use the user's chosen browser and profile. In-app and Chrome sessions are
  separate; a connected extension may represent a different profile. Check the
  intended surface before requesting another login.
- The user handles passwords and OTPs. Follow the environment's authorization
  rules for declarations, draft replacement and other consequential actions.
- Have the computation and source/account inventory ready. Check required bank
  disclosures early; see [assets-and-bank-disclosures.md](assets-and-bank-disclosures.md).
- Use supported browser/computer tools and fresh observations. Prefer exact
  semantic controls. Do not execute arbitrary page-mutation JavaScript, bypass
  UI validation, or retain indices/coordinates across page updates.

## Fill and verify persistence

1. Select AY, mode and the supported form; resume the existing draft when
   continuing. Starting new filing can replace it. Verify its form and preserve
   useful entries before an authorized replacement.
2. Reconcile prefill against sources. Prefill or schedule selection does not
   establish income, correct classification or completeness.
3. Fill a coherent batch, blur numeric fields, inspect calculated totals and
   save/confirm immediately. Record the form, schedule and verified save state.
4. Verify the summary confirmation or reopened values. An accepted import, a
   clicked Save button and an active countdown do not prove server persistence.
5. Recheck dependent loss, special-rate and Part B-TI/TTI schedules after edits.
   Earlier confirmations can silently become stale.

Evidence and portal status are separate. A technically confirmed schedule may
still contain an unresolved estimate. Do not count old-form confirmations as
new-form saves or call a known material gap final.

### Recovery and input issues

| Observation | Response and verification |
|---|---|
| Unauthorized despite an active countdown | Stop entry, preserve controls, ask the user to log in, resume and inspect saved values before repeating work. |
| Resume lands on schedule selection/questions | Inspect retained selections and use the visible route to keep existing answers. Do not blindly redo a questionnaire that can change applicability. |
| Navigation triggers a logout warning | Prefer breadcrumbs and Back to Summary. Distinguish browser Back from the page's Back; handle the actual visible warning. |
| Dropdown click has no effect | Inspect the opened list; use its actual option or supported keyboard selection. Verify the selected value. |
| Old zero remains or setting a value clears the field | Select the existing text, replace, blur and read it back. Visible triple-click selection is a fallback after bringing the field into view. |
| Wide timing table scrolls when focus changes | Focus/scroll to the cell, observe again, then edit. Verify the whole row: an incorrect period can preserve the annual total. |
| Save appears unchanged immediately | Observe the settled page before retrying; repeated clicks can duplicate rows. |
| Irrelevant schedule has mandatory blanks | Recheck applicability and remove it through supported controls. Do not fabricate identifiers to satisfy it. |

## Schedule 112A CSV imports

Download the current official template and instructions. Verify acquisition
codes, column count, quoting, precision, mandatory fields and name restrictions.
The [Department CSV instructions](https://static.incometax.gov.in/iec/foservices/assets/itr-shared/documents/112A_115AD_CSV_Instructions.pdf)
are a starting point; check applicability to the active AY/importer.

Some versions rejected an extra trailing empty template column or treated quoted
data literally. Diagnose the actual error with a minimal synthetic example;
do not universally strip columns or quotes from future templates. Record the
version/context with any workaround.

Retain source lots even if consolidation is permitted. Verify grandfathering and
effective-cost calculations survive aggregation. Compare accepted rows and gain
totals; explain portal rounding separately from source-exact amounts. Confirm
and verify persistence: an import may not survive a subsequent Unauthorized.

## Validation defects without invented facts

- **No-books balance sheet incomplete:** enter actual year-end business debtors,
  creditors, stock and cash. Profit is not cash; personal bank/investment assets
  do not automatically belong here. Never invent positive cash to pass a rule.
  If genuine zero balances fail, check applicability, required fields, the
  current form/schema and saved state. Preserve the facts and investigate or
  escalate the defect. See the no-books block in the
  [notified ITR-3, AY 2026-27](https://www.incometax.gov.in/iec/foportal/sites/default/files/2026-04/Notification_No_47_2026.pdf);
  recheck the actual form in other years.
- **Presumptive business code missing:** some versions hide description/code
  behind Add Another in the presumptive block, even for a single business.
  Inspect that subform, fill applicable fields, save and verify income did not
  duplicate. See [creator-44ada.md](creator-44ada.md).
- **Employer nature/address blanks:** use the actual employer category and
  communication address. Remove genuinely empty optional salary-breakup rows
  rather than inventing a perquisite. See [multiple-form-16.md](multiple-form-16.md)
  for per-employer/TAN entry and one annual standard deduction.

## Declaration, validation and exported-return review

The order and labels can vary. Identify each actual stage:

1. Applicable schedules saved and confirmations current.
2. Declaration reviewed and authorized as required. Do not affirm completeness
   while a known material gap remains.
3. Internal validation passed, with its actual result recorded.
4. Exported JSON/PDF reviewed for completeness and arithmetic.
5. Any separate upload-level validation passed after corrections.
6. Payment credit checked, return regenerated/revalidated, then user-only
   submission and e-verification.

Internal success does not establish upload-level success. Matching totals do not
establish that every account, receipt or required disclosure is present. Compare:

- form, AY, regime/election, residency, addresses and verification details;
- employer rows, income by head, setoffs, carry-forwards and gain/dividend timing;
- normal/special-rate tax, surcharge, cess, applicable interest and fees;
- payer-level TDS deducted/claimed and income-head tags, not just the total;
- required bank accounts/refund selection independently of AL asset totals;
- held-asset costs, related liabilities, exempt income and relevant flags;
- current-AY credits and payable/refund against the independent computation.

Before labeling a download, check completion, form/year and actual content. An
old tax statement can share a taxpayer/year filename with another report. Keep
originals private. If supported readers recover a prefixed PDF, verify content
and render key pages; neither reject every wrapper nor ignore all parser warnings.

After corrections, regenerate the export and repeat affected checks. JSON records
what will be filed; it does not prove correct inputs or legal treatment. State
which review and validation stages actually passed.

## Payment preparation and user handoff

Use the [Department challan manual](https://www.incometax.gov.in/iec/foportal/help/generate-challan-form)
and the live flow. Verify Act, FY/AY, taxpayer, payment head and existing payments.
For self-assessment tax the applicable minor head is 300; check the selection
rather than using the calendar year of payment as the AY.

Reconcile the balance after credits to tax, surcharge, cess, interest, penalty
and fee/other fields actually shown. Do not add gross tax to the unpaid balance
or count TDS twice. A fee is not automatically a penalty; verify current field
mapping. Make any rounding adjustment explicit and check components sum to the
return payable. See [Department computation guidance](https://wm.incometaxindia.gov.in/w/computation-of-tax-for-individual-1)
and [interest guidance](https://incometaxindia.gov.in/Tutorials/6-Interest%20payable%20by%20the%20taxpayer.pdf).
Recompute for actual payment/filing dates; do not reuse an illustrative amount
after income, credits, form or dates change.

Explain a large balance as tax less credits plus interest/fees. Asset disclosure
is different from taxable income. State whether the next blocker affects correct
payment, final filing, or neither; explain any change in readiness.

The user pays. Selecting a mode, saving a draft or generating a CRN does not prove
payment. Verify the paid receipt, AY, amount, date and available challan identifiers.
Check whether it populated the return; otherwise enter the paid challan in the
applicable tax-paid schedule. Confirm credit, recompute and investigate any
residual balance instead of dismissing it as rounding. Regenerate and revalidate.

The user submits and e-verifies. Retain the acknowledgement/verification outcome
and a private next-year handover of held costs, taxed receivables, adjustments and
estimates. Do not report filing from a draft, preview or payment receipt alone.
