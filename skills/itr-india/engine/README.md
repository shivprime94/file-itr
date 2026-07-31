# itr-india tax engine

Deterministic, auditable Indian ITR computation engine for **AY 2026-27**
(individual, resident, both regimes). Every statutory value is a `Rule` with a
verified citation; every gray area is either a **contested-flagged** rule
(surfaces in traces) or a fail-loud `OutOfScopeError` — never a silent guess.

Pipeline (`compute.compute()` runs all of it):

1. **Scope** (`scope.py`) — refuses what the engine cannot faithfully handle
   (wrong AY, non-residents, unknown asset classes, pre-s.50AA debt funds,
   pre-23-Jul-2024 land/building LTCG with the 20%-indexation option, …).
2. **Bucketing** (`buckets.py`) — classifies each CG/VDA item into its
   tax-treatment bucket (111A / 112 / 112A / slab / VDA), transaction-date
   keyed through the rule table.
3. **Set-off & carry-forward** (`setoff.py`) — s.70/71(3)/74/80 capital-loss
   machinery; per-item VDA loss quarantine (s.115BBH(2)(b)); brought-forward
   losses with the 8-AY window and timely-return gate.
4. **Rates** (`rates.py`) — FY 2025-26 slabs (both regimes), s.87A rebate with
   marginal relief, special rates (111A 20%, 112/112A 12.5%, ₹1.25L 112A
   exemption, VDA 30%), resident basic-exemption adjustment, surcharge with
   the 15% CG cap / 25% new-regime cap and marginal relief, 4% cess,
   s.288A/288B rounding.
5. **Interest** (`interest.py`) — s.234A/234B/234C with Rule 119A rounding,
   the s.234C capital-gains carve-out, s.208 ₹10k floor, s.207(2) senior
   exemption, and the single 15-March instalment for presumptive income under
   s.44AD/s.44ADA.

`compute.render_report()` prints the full audit trail (income lines, set-off
steps, carry-forwards, lapsed losses, tax build-up, interest, tax credits, net
amount payable, and refund due) for verification against the portal's Part
B-TTI.

For Section 207(2), set `Taxpayer.has_business_or_profession_income=True` for
an ITR-3/4 taxpayer with PGBP income. Resident seniors receive the advance-tax
exemption only when this flag is false. The default is false for compatibility
with existing non-business callers.

Set `Taxpayer.presumptive_scheme` to `SECTION_44AD`, `SECTION_44ADA`, or
`SECTION_44AE` for a presumptive filer. Sections 44AD and 44ADA select the
statutory single-instalment Section 234C schedule (100% by 15 March); Section
44AE intentionally remains on the ordinary quarterly schedule. Any non-`NONE`
scheme also counts as PGBP income for the Section 207(2) senior exemption gate.

Structurally out of scope (inputs cannot express them): business/HP/foreign
income, Chapter VI-A deductions, AMT, clubbing, s.89 relief. `normal_income`
is the caller's already-reconciled slab-rate total.

Run tests: `pytest skills/itr-india/engine/tests -v` (108 tests)
