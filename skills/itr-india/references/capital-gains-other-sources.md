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
- **Balanced-advantage / dynamic asset allocation and liquid funds** are usually
  NOT equity-oriented — slab STCG, and the CA treating them at slab is correct.
- **Switch-outs count as redemptions** and carry STT for equity funds; they get
  the same 111A/112A treatment as normal redemptions.
- When reviewing someone else's computation, reproduce their total first under
  their classification — if it matches to the rupee, the disagreement is pure
  classification and the AIS codes settle it.

### Non-equity ETFs / debt funds are NOT 111A — usually slab rate

Watch the asset type before assuming 111A/112A:

- **Gold / silver ETFs** (not equity-oriented): held ≤ 12 months → **STCG at
  slab (applicable) rate**, reported under CG section A "sale of assets other
  than A1–A4", not 111A. Longer holdings follow the current-year LTCG rule for
  such assets — confirm the holding-period threshold and rate for the year.
- **Liquid / debt ETFs and debt mutual funds** are typically **"specified mutual
  funds" u/s 50AA** → gains taxed at **slab rate regardless of holding period**.

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

## Income from other sources (Schedule OS)

- **Interest** (savings bank, FD, RD, P2P, income-tax refund interest): all
  taxable. In the **new regime there is no 80TTA**, so the entire savings-bank
  interest is taxed at slab rate. Sum interest across **all** banks (including
  ones missing from AIS).
- **Dividends:** taxable at slab rate. If dividend exceeds ₹10k from a payer, TDS
  u/s 194 may appear in 26AS — reconcile. Dividends need a quarter-wise breakup in Schedule OS (upto 15/6, 16/6–15/9, 16/9–15/12, 16/12–15/3, 16/3–31/3) — the portal uses it for 234C. Build it from the broker's dividend statement (date-wise ledger), not the single AIS total. Strictly it's date of receipt/credit; ex-date is a fine proxy and the difference is immaterial when the return is in a refund position.
- Other items (gifts > ₹50k u/s 56(2)(x), family pension, winnings u/s
  115BB/115BBJ at special rates) only if applicable.

Net "Income from Other Sources" flows into Part B-TI and is taxed at normal slab
rates (except the special-rate items, which route through Schedule SI).
