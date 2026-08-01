# Capital gains and other sources

## Capital gains on listed equity & equity mutual funds (Schedule CG)

The two special-rate buckets you'll meet most often:

- **STCG u/s 111A** — listed equity / equity-MF held ≤ 12 months, STT paid.
  Taxed at a **flat special rate** (confirm the current-year rate; for transfers
  **on/after 23 July 2024** it is **20%**; before that it was 15%). Report under
  CG section A → "111A (for others)": full sale value, cost (no indexation),
  gain.
- **LTCG u/s 112A** — same assets held > 12 months, STT paid. Taxed at the 112A
  rate with the annual exemption (confirm current-year threshold/rate). Report
  under the 112A section.

Per scrip: sale value − cost of acquisition = gain; record buy/sell dates (for
holding period) and confirm STT was paid (makes it 111A/112A rather than the
slab/other rate). Cross-check the sale proceeds against the bank credit.

### Equity-oriented or not? Let the AIS decide

The single most consequential classification call for mutual-fund gains is
equity-oriented (111A/112A special rates, 112A's annual exemption — ₹1.25L for
AY 2025-26/2026-27) vs non-equity (slab STCG, 12.5% no-indexation LTCG after
24 months, or always-slab u/s 50AA for post-Apr-2023 "specified" debt funds).
Tax software and even CA computations get this wrong routinely — typically by
dumping equity-fund LTCG into "other than 112A" (losing the ₹1.25L exemption)
or equity-fund STCG into slab income (30% instead of the 111A rate).

Don't classify by fund name or gut feel — the **AIS information code is
authoritative evidence**:

- **SFT-18-EMF "Sale of unit of equity oriented mutual fund"** (with an STT
  amount on each row) → 111A/112A applies.
- **SFT-18-OTU "Sale of other unit"** (STT column zero) → non-equity rules.
- **SFT-17-LES "Sale of listed equity share"** → 111A/112A applies.

Traps to check explicitly:

- **Arbitrage funds** (Nippon/PPFAS/WhiteOak Arbitrage etc.) are equity-oriented
  despite behaving like debt — 111A/112A, not slab.
- **Balanced-advantage / dynamic asset allocation funds** usually ARE
  equity-oriented — most maintain **gross equity ≥ 65%** (often via arbitrage/
  hedged positions) specifically to qualify, so they get 111A/112A, not slab.
  Don't assume "balanced/hybrid ⇒ non-equity"; **check the AIS code / the fund's
  equity-oriented declaration** for the year. **Liquid / money-market funds**,
  by contrast, are NOT equity-oriented (slab), and a CA treating those at slab
  is correct. A fund that drops below 65% equity loses equity-oriented status
  and its gains go to slab regardless of holding period.
- **Switch-outs count as redemptions** and carry STT for equity funds; they get
  the same 111A/112A treatment as normal redemptions.
- When reviewing someone else's computation, reproduce their total first under
  their classification — if it matches to the rupee, the disagreement is pure
  classification and the AIS codes settle it.

### Non-equity ETFs / debt funds are NOT 111A — usually slab rate

Watch the asset type before assuming 111A/112A:

- **Gold / silver ETFs** (listed, not equity-oriented): **long-term at
  > 12 months → 12.5% without indexation u/s 112**; **≤ 12 months → STCG at the
  slab (applicable) rate**, reported under CG section A "sale of assets other
  than A1–A4" (not 111A). The threshold is a **flat 12 months** — there is **no**
  acquisition-date "transitional" and **no** 24-month variant. Two Finance
  (No.2) Act 2024 changes combine to give this for AY 2026-27:
  - **s.2(42A) (w.e.f. 23 Jul 2024)** makes a *listed* unit other than an
    equity-oriented-fund unit long-term at **> 12 months**, with **no
    grandfathering by acquisition date**; and
  - **s.50AA's** "specified mutual fund" definition was narrowed to *> 65% in
    debt/money-market* **from AY 2026-27**, so gold/silver ETFs are **no longer**
    always-short-term "specified mutual funds" and follow the ordinary
    holding-period test.

  So a gold ETF **acquired 1 Sep 2024 and sold 1 Dec 2025 (15 months)** is
  **long-term u/s 112**, *not* slab STCG; and one **bought before 23 Jul 2024**
  and held > 12 months is an ordinary LTCG, *not* out of scope. (In the **prior**
  year, FY 2024-25, gold ETFs were still s.50AA "specified mutual funds" →
  always short-term regardless of holding — a different AY; don't carry that
  back.) Unlisted gold-fund units still use the general **24-month** period
  under s.2(42A). Matches `engine/buckets.py` /
  `holding.listed_nonequity.lt_months`.

  **Primary:** [Finance (No. 2) Act, 2024, eGazette](https://egazette.gov.in/WriteReadData/2024/256436.pdf)
  s.3(b) (s.2(42A) — removes “other than a unit”; retrospective from 23 Jul 2024)
  and s.21(b) (s.50AA SMF definition, w.e.f. 1 Apr 2026 / AY 2026-27). Budget
  2024 memorandum notes gold ETFs/MFs among funds previously caught by the old
  SMF test. **Secondary:** Taxmann / ClearTax gold-ETF notes; TaxGuru on the
  s.50AA commencement.
- **Liquid / debt ETFs and debt mutual funds** that meet the **>65% debt** SMF
  test u/s **50AA** (AY 2026-27) → gains taxed at **slab rate regardless of
  holding period**.

These slab-rate STCG amounts add to normal income (not Schedule SI) and are taxed
at the taxpayer's slab — which can be *higher* than the 111A rate for high
earners.

### Deduct Section 48 transfer expenses — but never STT

The gain is **net of transfer expenses** under Section 48: brokerage, exchange /
clearing charges, SEBI turnover fees, stamp duty, and GST on brokerage are all
deductible. **STT is specifically NOT deductible** (barred by the proviso to
Section 48) — leave it out of the cost/expense figure. Broker "Tax P&L" reports
list these charges per segment (equity and non-equity separately); subtract them
(ex-STT) from each bucket. A raw *sale − buy* figure that ignores these charges
**overstates the gain** and the tax. This matters for **every** bucket — 111A,
112A, and slab-rate/non-equity STCG alike.

### Set-off ordering (do it in this sequence)

1. **Current-year losses first.** A current-year 111A loss (or LTCG loss) is set
   off intra-head against current-year capital gains — e.g. a 111A loss can
   reduce slab-rate STCG. A **LTCG loss sets off only against LTCG**.
2. **Brought-forward capital losses next**, via Schedule BFLA. A brought-forward
   **short-term** loss sets off against **any** current-year capital gain — STCG
   (any rate) *or* LTCG; a brought-forward **long-term** loss sets off against
   **LTCG only** (Section 74).
3. **Carry forward the excess.** If the brought-forward loss exceeds this year's
   gain, the balance carries forward (Schedule CFL) for up to 8 AYs. Confirm the
   residual STCG/LTCG loss actually appears in Schedule CFL for next year.

Set-off of a brought-forward loss is **mandatory** to the extent gains exist —
you can't choose to carry it forward while showing taxable gains.

### 87A rebate vs special-rate gains (new regime, AY 2026-27 on)

Finance Act 2025: the Section 87A rebate (up to ₹60,000) uses **slab-base
income** — normal + slab-rate STCG, **excluding** 111A/112/112A special-rate
income — for both the ₹12L eligibility test and marginal relief. It never
offsets special-rate tax. So:

- ~₹11L salary + large 112A LTCG can still get a full slab rebate even though
  *total* income exceeds ₹12L (only the slab portion is tested).
- Non-equity fund STCG (slab) counts toward the ₹12L test and is rebateable;
  even ₹1 of equity STCG u/s 111A produces special-rate tax a sub-₹12L filer
  must actually pay.
- Equity LTCG within the 112A ₹1.25L exemption is nil regardless.

Whether VDA (s.115BBH) is excluded from the ₹12L test like 111A/112/112A is
**not** treated as settled here — see `tax-regimes-and-slabs.md`.

### Quarterly breakup matters (for 234C interest)

Schedule CG asks for capital gains split by the quarter in which they accrued
(up to 15 Jun / 16 Jun–15 Sep / 16 Sep–15 Dec / 16 Dec–15 Mar / 16–31 Mar).
**Put the gain in the correct quarter** — the portal uses it to compute Section
234C interest for deferment of advance tax. Putting it in the wrong quarter
mis-states the interest. **234C relief (proviso to s.234C(1)):** where the
shortfall is because a capital gain (or dividend) could not be foreseen, no 234C
interest applies to it **provided** the whole tax on that income is paid in the
advance-tax instalments falling due after it accrued (or by 31 Mar) — which is
exactly why putting the gain in the correct quarter matters.

### Flow downstream

STCG/LTCG → Schedule SI (special income) where the special-rate tax is computed
→ Part B-TI item for capital gains → Part B-TTI "tax at special rates". Verify
the special-rate tax equals gain × the special rate.

## Capital gains on immovable property (land / building)

SKILL.md advertises "capital gains on … property," so know these — they route
differently from listed equity and are **not** in the tested engine's scope for
the indexation-option case (`engine/scope.py` refuses pre-23-Jul-2024
land/building LTCG). Re-confirm every figure for the year; work these by hand.

- **Holding period:** long-term at **> 24 months** (s.2(42A)); otherwise
  short-term at the **slab rate** (no 111A for property).
- **Rate on LTCG (s.112):** **12.5% without indexation** for transfers on/after
  23 Jul 2024. For land/building **acquired before 23 Jul 2024**, a **resident**
  may instead opt **20% with indexation** and pay the lower of the two (proviso
  to s.112) — you need the CII table to evaluate it. Source: [ClearTax, s.112](https://cleartax.in/s/section-112-calculate-income-tax-on-long-term-capital-gains).
- **Section 50C — stamp-duty-value floor:** the full value of consideration is
  **deemed to be the stamp-duty value** if that value **exceeds 110%** of the
  actual consideration (a 10% tolerance band, AY 2021-22 onward); within 10%,
  the actual consideration stands. So check the sale deed's SDV against the
  agreed price before computing the gain. Source: [ClearTax, s.50C](https://cleartax.in/s/taxability-sale-land-building-section-50c).
- **Cost / FMV-as-on-1-Apr-2001:** for property acquired **before 1 Apr 2001**,
  the taxpayer may substitute the **FMV as on 1 Apr 2001** for actual cost
  (s.55(2)(b)) — get a registered valuer's report; the SDV as on 1 Apr 2001 caps
  it.
- **Reinvestment exemptions (claim if the facts fit):**
  - **s.54** — LTCG on a **residential house** reinvested in another residential
    house (buy 1 yr before / 2 yr after, or construct within 3 yr).
  - **s.54F** — LTCG on **any other** long-term asset, where the **net sale
    consideration** is reinvested in one residential house (assessee must not
    own more than one other house).
  - **s.54EC** — LTCG on **land/building** invested in **REC / PFC / IRFC / NHAI
    bonds within 6 months**, capped at **₹50 lakh** (across the two FYs of the
    same transfer), 5-year lock-in.
  - s.54 and s.54F reinvestment exemption is **capped at ₹10 crore** (FY 2023-24
    onward). Sources: [ClearTax, s.54EC](https://cleartax.in/s/section-54ec-bonds);
    [AllIndiaITR, s.54/54F/54EC](https://www.allindiaitr.com/capital-gains-exemption-section-54-54f-54ec).
- **Section 194-IA TDS (reconciliation):** on a sale where consideration **or**
  SDV is **≥ ₹50 lakh**, the **buyer** deducts **1% TDS** (higher of the two) and
  files Form 26QB. For the **seller's** return, that 1% shows up in 26AS/AIS and
  is claimed as a TDS credit like any other; for a taxpayer who **bought**
  property, flag the Form 26QB obligation. From 1 Oct 2024 the ₹50 lakh test is
  on the **aggregate** across all buyers/sellers. Source: [Income Tax
  Department, TDS on purchase of immovable property](https://www.incometaxindia.gov.in/w/tds-from-sum-paid-to-buy-an-immovable-property).

Property gains that qualify for the 20%-with-indexation option, or that need CII
computation, are **beyond the quick self-file / the tested engine** — escalate
rather than guess the indexed cost.

## Income from other sources (Schedule OS)

- **Interest** (savings bank, FD, RD, P2P, income-tax refund interest): all
  taxable. In the **new regime there is no 80TTA**, so the entire savings-bank
  interest is taxed at slab rate. Sum interest across **all** banks (including
  ones missing from AIS).
- **Dividends:** taxable at slab rate. If dividend exceeds ₹10k from a payer, TDS
  u/s 194 may appear in 26AS — reconcile. Dividends need a quarter-wise breakup in Schedule OS (upto 15/6, 16/6–15/9, 16/9–15/12, 16/12–15/3, 16/3–31/3) — the portal uses it for 234C. Build it from the broker's dividend statement (date-wise ledger), not the single AIS total. Strictly it's date of receipt/credit; ex-date is a fine proxy and the difference is immaterial when the return is in a refund position.
- **Family pension** (pension to a deceased employee's family) is taxable under
  "other sources", but a **standard deduction u/s 57(iia)** applies: the **lower
  of one-third of the family pension or ₹15,000** (old regime) / **₹25,000**
  (new regime, raised by Finance (No.2) Act 2024, AY 2025-26 onward). This is
  distinct from the salary standard deduction and easy to miss. Source:
  [ClearTax, s.57](https://cleartax.in/s/section-57-of-the-income-tax).
- Other items (gifts > ₹50k u/s 56(2)(x), winnings u/s 115BB/115BBJ at special
  rates) only if applicable.

Net "Income from Other Sources" flows into Part B-TI and is taxed at normal slab
rates (except the special-rate items, which route through Schedule SI).
