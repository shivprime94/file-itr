# Reconciling income to source documents

The single most important discipline: **one number per income head, each tied to
a document**. Build a small reconciliation table and don't move on until every
figure has a source and the figures cross-tie. AIS/26AS are starting points, not
gospel — they can miss income (under-threshold banks, foreign platforms) and can
double-count (e.g., the same payout seen by two reporters).

## The documents and what each gives you

- **Form 16** (from each employer): gross salary 17(1), perquisites 17(2),
  TDS deducted, regime opted. The Part B has the breakup.
- **Form 26AS**: tax credit statement — every TDS/TCS entry against the PAN,
  plus the deductor (TAN) and section (192 salary, 194C contract, 194J
  professional, 194-IB rent, etc.). Use it to confirm TDS and to discover payers.
- **AIS / TIS** (Annual Information Statement): a wider feed — interest,
  dividends, securities transactions, mutual-fund purchases, salary, etc. Often
  has OCR-only PDFs; extract carefully.
- **Bank statements**: the ground truth for interest credited and for tracing
  platform payouts. Search for the interest credit lines and total them per bank.
- **Broker / capital-gains statement**: realised STCG/LTCG with buy/sell dates,
  cost, and STT flag.
- **Platform payout files** (Stripe/PayPal/YouTube/X/etc.): the creator/freelance
  gross receipts. Sum them and **cross-check the total against the bank credits**
  so you know the money actually landed.

## How to reconcile each head

**Salary:** Sum gross 17(1) across all Form 16s = total gross salary. Confirm
each against the 26AS salary (192) entries. Subtract the single ₹75,000 standard
deduction (new regime). The result is income chargeable under "Salaries". If the
employee had more than one employer in the year, the later employer's own TDS
computation often aggregates the earlier employer's income for its own
withholding — but may use the earlier employer's **gross** figure rather than
its **net-of-exemption** figure (e.g. a 10(10AA) leave-encashment exemption the
earlier employer already applied), silently overstating the combined income
used for withholding. This isn't an error the portal or either Form 16 will
flag — it just shows up as extra TDS. Don't take either employer's combined-
income figure at face value; rebuild the combined salary yourself from both
Form 16s and each one's exemptions, and trust only your own total.

**Salary arrears / advance — Section 89(1) relief (ask for it).** If the salary
includes **arrears** (a pay revision, or a pending increment for earlier years
paid this year), **advance salary**, gratuity, commuted pension, or leave
encashment that bunches several years' income into one, the taxpayer can claim
**s.89(1) relief** — the tax is refigured as if each arrear had been taxed in the
year it related to, and the difference is a **reduction from the tax payable**
(not a deduction from income). It requires **Form 10E filed on the portal
*before* the return** — if 10E isn't filed, the department disallows the relief
and raises a demand. Ask explicitly whether any arrears were received; the
relief can be large and is routinely missed. Source:
[ClearTax, s.89(1) / Form 10E](https://cleartax.in/s/get-help-with-salary-arrears).

**Business/profession receipts:** Add every professional/contract receipt: 26AS
194C/194J entries **plus** platform payouts that weren't subject to TDS. Watch
for overlap — a payout already inside a 26AS entry must not be counted twice.
The sum is gross receipts; the presumptive income is a % of it
(see `creator-44ada.md`).

**Interest:** Total the interest credits from **every** bank statement, not just
the ones in AIS. Add HDFC + SBI + PNB + … = total savings-bank interest. In the
new regime there is no 80TTA, so the whole amount is taxable. If a small bank's
interest is absent from AIS, it still goes in — flag it to the user.

**Capital gains:** From the broker statement, per scrip: sale value − cost =
gain, with the dates (for holding period) and STT flag (for 111A/112A special
rates). Cross-check the sale proceeds credit in the bank.

**Dividends:** From AIS / broker; taxable at slab rate in Schedule OS.

## Worked reconciliation pattern (illustrative)

```
# Illustrative figures only — not anyone's real return.
SALARY
  Employer A (Form 16 / 26AS-192)             6,00,000
  Employer B (Form 16 / 26AS-192)             9,00,000
  Gross salary                               15,00,000
  − standard deduction                         −75,000
  Income from Salary                         14,25,000

BUSINESS (profession, presumptive 44ADA)
  Contract receipt (26AS 194C)                  20,000
  Platform payouts (bank-confirmed)             30,000   ← Σ payouts = bank credits
  Gross receipts                                50,000
  Presumptive income @ 50%                      25,000

CAPITAL GAINS (STCG, listed equity, STT paid)
  Sale 40,000 − cost 25,000                     15,000

OTHER SOURCES (interest)
  Bank A 3,000 + Bank B 2,000 + Bank C 5,000    10,000   ← a bank below the AIS threshold → still declared

TOTAL INCOME                                 14,75,000
```

The point of the table is that an auditor (or the user) can follow every rupee
back to a document. If a number can't be sourced, stop and find the source.

## Mismatches — what to do

- **AIS shows income you can't trace:** ask the user; it may be a duplicate, a
  joint-account entry, or genuinely theirs. Don't silently drop it.
- **Income you have but AIS doesn't:** declare it anyway (see SKILL.md).
- **TDS in 26AS but no matching income:** find the income — TDS implies a
  payment was made to the PAN.
- **Foreign-platform money received in INR in India:** generally Indian-source
  business income for a resident; it is not "foreign income" merely because the
  payer is abroad. Treat the foreign-asset/foreign-income questions on their
  own facts and flag any genuine foreign asset for Schedule FA.
- **Clubbing (s.64) — whose income is it really:** income of a **minor child**
  (beyond a small ₹1,500/child exemption u/s 10(32)) and income from assets
  **transferred to a spouse or minor without adequate consideration** is
  **clubbed in the transferor's hands**, not the child's/spouse's. So interest
  or capital gains sitting in a minor's or a non-earning spouse's account may
  belong on *this* return. Ask; don't assume an account in another name is off
  the return.

## Schedule AL — assets & liabilities disclosure (high income)

If **total income exceeds ₹1 crore** (ITR-2/ITR-3), Schedule AL must disclose
cost of specified assets (immovable property, jewellery, vehicles, shares/
securities, cash, bank balances) and related liabilities at year-end. It is a
**disclosure only — it does not change the tax**. Secondary sources report the
threshold was **raised from ₹50 lakh to ₹1 crore for AY 2026-27**; that change
is **not yet confirmed against the notified return / validation rules here**, so
**verify the current-year threshold** before telling a ₹50L–₹1cr taxpayer they
can skip it. Source (to verify): [Income Tax Department, Schedule AL](https://www.incometaxindia.gov.in/w/8schedule_al).
