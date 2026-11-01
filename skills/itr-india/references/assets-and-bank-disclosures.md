# Assets and bank disclosures

Build this inventory early, alongside income collection. There are three
separate checks: individual bank-account disclosure, annual taxable/exempt
income, and year-end asset/liability values. Passing one does not pass the others.
Use [collection-and-coverage.md](collection-and-coverage.md) for source selection.

## Confirm the applicable form and year

Read the actual year's notified form and instructions before deciding whether
Schedule AL applies or which valuation/category to use. Do not roll forward an
older threshold or assume business balance-sheet assets must be entered again.
For example, the [notified ITR-3 for AY 2026-27](https://www.incometax.gov.in/iec/foportal/sites/default/files/2026-04/Notification_No_47_2026.pdf)
PDF page 54, Schedule AL, states its applicability threshold, specifies year-end
assets other than those in Part A-BS, and labels the asset amounts as cost.
Recheck these requirements for another AY/form; use
[form-selection-ay2026-27.md](form-selection-ay2026-27.md) for that year's form
selection.

## Bank list: collect before filling

The same [notified ITR-3](https://www.incometax.gov.in/iec/foportal/sites/default/files/2026-04/Notification_No_47_2026.pdf),
PDF page 58, Part B-TTI item 13, requires all Indian bank accounts held at any time
during the previous year except dormant accounts. It asks for IFSC, bank name,
account number and type, with refund nomination. Do not omit an account merely
because its balance or interest is small. Verify any claimed dormant exception
against the applicable instructions and actual account status.

1. Build a private account list from the taxpayer's inventory, bank documents,
   AIS and prior return. Check additions and closures during the year; last
   year's prefill is a starting point, not a completeness certificate.
2. Verify full account number, IFSC, type, ownership and applicable refund
   nomination. A customer identifier, folio, masked suffix or reporting-system
   prefix is not automatically the bank account number. Establish any
   normalization from bank evidence; do not strip characters or guess an IFSC
   merely to pass validation.
3. Keep savings, deposit principal, PPF/exempt income and bank-held investments
   distinct in the working inventory. Choose final form categories from the
   applicable instructions and avoid adding a composite statement total again.
4. Compare the expected account list with the **actual exported return JSON or
   preview**, including accounts whose balances already contribute to AL. A
   correct aggregate bank value cannot substitute for individual disclosure.

Profile bank validation, refund eligibility and the return's bank list are
separate states. A return's “Add another” action may open profile bank addition
and require a separate user verification. Follow the actual UI, let the user
handle credentials/OTP, and verify the outcome. Do not call a profile update ITR
e-verification or assume it refreshed an existing draft. Reopen/refresh the
return as supported, export again, and compare accounts before calling the gap
closed. See [portal-workflow.md](portal-workflow.md) for recovery and handoff.

## Remaining holdings require their own cost inventory

Create an owner/date/category inventory for property, vehicles, deposits,
securities, portfolio cash, receivables, gold and other applicable assets and
related liabilities. Link each value to evidence or a clearly labelled estimate.

- Reconcile **remaining held units and cost** separately from realized gains.
  Correct disposed-lot gains do not prove complete year-end holdings.
- Deduplicate direct, broker, registrar and portfolio-manager holdings. Where a
  consolidated held-cost inventory replaces overlapping portfolio investments,
  remove those subtotals rather than adding both. Keep unrelated portfolio cash
  and bonds separate.
- Review transferred units, corporate actions, reinvested units and zero-cost
  entries. Portfolio transfer book value or market NAV is not automatically the
  acquisition basis required by the form. Do not invent zero basis for missing
  opening history.
- Broker ledger credit is not automatically cash in hand. Establish its nature
  and applicable category; distinguish refundable balances from securities cost.
  Profit, presumptive income and taxable income are not evidence of physical
  cash. Genuine zero balances must not become invented positive assets to make
  validation pass.
- Use a dated liability balance. Annual loan interest/principal payments and
  the closing outstanding loan answer different questions. Do not copy an old
  loan amount or today's balance into year-end disclosure.

## Date bridges and reasonable estimates

A statement generated in April may include April transactions in its headline
balance. Reconstruct the balance at the required year-end from transaction
dates. Likewise, separate earned interest, credited cash/units and receivables;
bridge a subsequent posting without adding the same income or asset twice.
Check prior-year inclusion before adding a boundary-date dividend or interest
credit. Its legal recognition belongs in the income analysis, not a guessed
cash-date rule.

For gold or other holdings, current-year purchases alone do not establish total
closing cost. Bridge opening cost, purchases, supported rewards/in-kind receipts
and disposals to held quantities and cost. Leasing existing units is not another
purchase. Income earned by year-end but credited as units afterward must not be
silently counted as units already held. Establish the acquisition basis and any
separate receivable consistently with the supported tax treatment; do not
promote one platform's payout policy into a universal rule.

When precision is unavailable, use a reasonable estimate only with an identified
source or taxpayer-provided basis, the applicable form instructions, explicit
ownership/date/category and a recorded limitation. A historical-price estimate
is not current market revaluation; a user estimate is not statement verification.
Never infer a year-end balance from annual interest, assume missing opening
holdings are zero, or invent physical jewellery. Clarify what an ambiguous amount
refers to before applying it. Stop precision-only document requests once evidence
is adequate for the material disclosure, while retaining unresolved material gaps
for review.

Before final declaration, compare category totals, no-double-count controls,
held-cost estimates and account-list completeness with the export. Reconfirm
impacted schedules after correction. Preserve adjusted costs, taxed receivables
and estimate limitations privately for the next filing; final review still needs
both numerical agreement and evidence completeness.
