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

### 87A rebate vs special-rate gains (new regime, AY 2026-27 on)

The Section 87A rebate (total income ≤ ₹12L → rebate up to ₹60,000) applies
only to **slab-rate** tax — not to 111A/112A/112 special-rate tax. So non-equity
fund STCG (slab) is effectively rebateable, while even ₹1 of equity STCG u/s
111A produces tax a sub-₹12L filer must actually pay. Equity LTCG within the
112A ₹1.25L exemption is nil regardless.

### Quarterly breakup matters (for 234C interest)

Schedule CG asks for capital gains split by the quarter in which they accrued
(up to 15 Jun / 16 Jun–15 Sep / 16 Sep–15 Dec / 16 Dec–15 Mar / 16–31 Mar).
**Put the gain in the correct quarter** — the portal uses it to compute Section
234C interest for deferment of advance tax. Putting it in the wrong quarter
mis-states the interest.

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
  u/s 194 may appear in 26AS — reconcile.
- Other items (gifts > ₹50k u/s 56(2)(x), family pension, winnings u/s
  115BB/115BBJ at special rates) only if applicable.

Net "Income from Other Sources" flows into Part B-TI and is taxed at normal slab
rates (except the special-rate items, which route through Schedule SI).
