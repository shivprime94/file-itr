from datetime import date
from decimal import Decimal
from engine.rulebase import Rule, RuleTable

# This engine is not wired into SKILL.md (see engine/README.md). The slab,
# rebate, surcharge, and cess values below are independently duplicated in
# SKILL.md's "Verify the math" snippet and in references/tax-regimes-and-slabs.md
# (prose) — update all three together if a rate or threshold changes.

_CLEARTAX_STCG = "https://cleartax.in/s/short-term-capital-gain-on-shares"
_QUICKO_HP = "https://learn.quicko.com/capital-gains-holding-period-tax"
_CLEARTAX_50AA = "https://cleartax.in/s/section-50aa-income-tax-act"
# Deep links verified by WebFetch (2026-07-29): each page was fetched and its
# operative statutory text confirmed to state the value(s) this rule encodes.
# "Section 2 in The Income Tax Act, 1961" — contains clause (42A). CAVEAT: this
# mirror pre-dates Finance (No.2) Act 2024 (base definition still reads "36
# months"; the 2014 date-conditional proviso is unchanged). It still corroborates
# holding.listed_equity.lt_months=12 (first proviso: listed securities / equity-
# oriented-fund / UTI units / zero-coupon bond -> 12 months) — the limb the 2024
# amendment left at 12 months — and is this rule's deep, non-search primary. The
# other two holding.* rules now cite the FA (No. 2) Act 2024 eGazette directly:
# holding.other.lt_months=24 (opening portion, s.3(b)(i): "36 months" -> "24
# months") and holding.listed_nonequity.lt_months=12 (first proviso, s.3(b)(ii):
# "(other than a unit)" deleted) — neither change is present on this page.
_IK_2_42A = "https://indiankanoon.org/doc/545792/"
# Gold/listed-non-equity holding period. Finance (No. 2) Act, 2024, s.3(b)
# (eGazette) amends s.2(42A) with retrospective effect from 23-Jul-2024:
# deletes "(other than a unit)" from the first proviso so the 12-month
# long-term threshold covers listed securities including listed units
# (gold/silver ETF, REIT/InVIT/business-trust/debt-fund units, etc.). Same Act
# s.21(b) substitutes the s.50AA "specified mutual fund" definition (w.e.f.
# 1-Apr-2026 / AY 2026-27) to >65% debt and qualifying FoFs — gold/silver ETFs
# exit the always-STCG deeming for this AY and take the ordinary holding test.
# Primary: eGazette FA (No. 2) 2024 PDF. Secondary: Taxmann note
# (no acquisition-date grandfathering for the 12-month listed-unit limb).
_EGAZETTE_FA_NO2_2024 = "https://egazette.gov.in/WriteReadData/2024/256436.pdf"
_TAXMANN_CG_FA2024 = "https://www.taxmann.com/post/blog/key-amendments-to-capital-gains-provisions-under-the-finance-no-2-act"
_TAXGURU_50AA_FA2024 = "https://taxguru.in/income-tax/amendment-specified-mutual-fund-definition-section-50aa-budget-2024.html"
# "Section 24 in The Finance Act, 2023" — the enacting provision that inserts
# s.50AA into the Income-tax Act; contains "Specified Mutual Fund" and the
# "1st day of April, 2023" effective-date language, which corroborates
# s50aa.acquired_from directly. CAVEAT: the fetched text truncated before the
# deeming-as-short-term-capital-gains language, so s50aa.applies ("always
# short-term, any holding") is corroborated by inference from "Notwithstanding
# anything contained in clause (42A) of section 2 or section 48" (an explicit
# override of the normal holding-period test), not by directly-read deeming
# text. Also note (not a value/citation defect, flagged for the record): this
# section's own commencement clause reads "with effect from the 1st day of
# April, 2024" — standard Finance Act drafting for "applicable from AY
# 2024-25" (PY 2023-24, beginning 1-Apr-2023), consistent with this rule's
# effective_from=2023-04-01, but worth a second look if this rule is revisited.
_IK_50AA = "https://indiankanoon.org/doc/71017618/"
# "Section 115BBH in The Income Tax Act, 1961" — contains "virtual digital
# asset" and "thirty per cent".
_IK_115BBH = "https://indiankanoon.org/doc/4837707/"
_QUICKO_VDA = "https://learn.quicko.com/income-tax-on-cryptocurrency-nft-vda"
# Set-off & carry-forward deep links, verified by WebFetch (2026-07-29):
# "Section 70 in The Income Tax Act, 1961" — sub-s (2): STCL "set off against
# the income … in respect of any other capital asset"; sub-s (3): LTCL against
# "any other capital asset not being a short-term capital asset".
_IK_70 = "https://indiankanoon.org/doc/1628473/"
# "Section 71 in The Income Tax Act, 1961" — sub-s (3): CG loss "shall not be
# entitled to have such loss set off against income under the other head".
_IK_71 = "https://indiankanoon.org/doc/178812545/"
# "Section 74 in The Income Tax Act, 1961" — (1)(a) c/f STCL against "any other
# capital asset"; (1)(b) c/f LTCL against "any other capital asset not being a
# short-term capital asset"; (2) "not … more than eight assessment years
# immediately succeeding the assessment year for which the loss was first
# computed".
_IK_74 = "https://indiankanoon.org/doc/1129438/"
# "Section 80 in The Income Tax Act, 1961" — "no loss which has not been
# determined in pursuance of a return filed [u/s 139(3)] shall be carried
# forward and set off under … sub-section (1) or sub-section (3) of section 74".
_IK_80 = "https://indiankanoon.org/doc/1502697/"
# s.115BBH(2)(b) on the same _IK_115BBH page: "no set off of loss from transfer
# of the virtual digital asset … against income computed under any provision of
# this Act … and such loss shall not be allowed to be carried forward".
_CLEARTAX_SETOFF = "https://cleartax.in/s/set-off-carry-forward-capital-losses"
# Phase 3 rate sources, verified by WebFetch (2026-07-29):
# cleartax slab-rates page — states the FY 2025-26 new-regime slabs
# (4/8/12/16/20/24L at 0/5/10/15/20/25/30%), 87A new ₹60,000 ≤ ₹12L
# slab-income-only with marginal relief, old-regime slabs incl. senior (3L) and
# super-senior (5L) basic exemption, and 87A old ₹12,500 ≤ ₹5L. The official
# PIB Budget-2025 releases (PRID 2098352/2098353) corroborate the slabs and
# rebate via search summaries but return HTTP 403 to direct fetch — cleartax is
# the WebFetch-verified citation, PIB kept as the (unfetchable) official trail.
_CLEARTAX_SLABS = "https://cleartax.in/c/income-tax-slab-rates"
_PIB_BUDGET_2025 = "https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2098353&reg=3&lang=2"
# Finance Act 2025 inserted a proviso to s.87A excluding income chargeable at
# special rates (Chapter XII — e.g. 111A/112/112A) from BOTH the ₹12L new-regime
# threshold test and the marginal-relief computation, not just from what the
# rebate can offset. Official ITD FAQ page kept as the primary trail but, like
# the PIB pages above, returns HTTP 403 to direct fetch (2026-07-31); TaxTMI's
# note is the WebFetch-verified secondary and reads closest to the department's
# own wording ("tax on incomes chargeable at special rates ... are not included
# while determining the rebate"). See rebate.87a_new's contested_note.
_ITD_87A_FAQ_FY2526 = "https://www.incometaxindia.gov.in/w/what-is-rebate-under-section-87a-for-f.y-2025-26-and-who-can-claim-it-"
_TAXTMI_87A = "https://www.taxtmi.com/tmi_notes?id=1432"
# bajajamc Budget-2024 CG explainer — "increased from 15% to 20%" (111A),
# "risen from 10% to 12.5%" (112A), exemption "from Rs 1 lakh to Rs 1.25 lakh".
_BAJAJAMC_CG = "https://www.bajajamc.com/knowledge-centre/union-budget-2024-new-mutual-funds-capital-gains-tax-explained"
# cleartax s.112 page — 12.5% without indexation; also documents the resident
# option for immovable property: "20% with indexation OR 12.5% without".
_CLEARTAX_112 = "https://cleartax.in/s/section-112-calculate-income-tax-on-long-term-capital-gains"
# quicko s.112 page — residents "can benefit from adjusting the special rate
# income against the basic exemption limit"; non-residents excluded.
_QUICKO_112 = "https://learn.quicko.com/section-112-of-income-tax-act-capital-gain-long-term-capital-assets"
_UPSTOX_BEL = "https://upstox.com/news/personal-finance/tax/can-i-adjust-stcg-ltcg-against-the-basic-exemption-limit-under-both-old-and-new-tax-regimes/article-165394/"
# "Section 55 in The Income Tax Act, 1961" — bare Act text for clause (2)(ac).
_IK_55 = "https://indiankanoon.org/doc/1704110/"
# msassociates.pro — states the s.55(2)(ac) formula plainly: COA of an equity
# share/equity-MF-unit acquired before 1-Feb-2018 (for s.112A purposes) is the
# higher of actual cost or the lower of FMV as on 31-Jan-2018 and full value
# of consideration. Corroborates the loss-disallowed proviso (vrdnation.com,
# search-verified 2026-08-01): the formula can only shield pre-2018 gains, it
# cannot manufacture a loss beyond the actual-cost loss.
_MSASSOCIATES_55 = "https://www.msassociates.pro/articles/section-55-2-ac-cost-of-acquisition/"
# cleartax surcharge page — 10/15/25/37% at 50L/1cr/2cr/5cr, new-regime cap
# 25%, "Surcharge has been capped at 15% on dividend income and Capital gains
# covered under section 111A, 112 and 112A", marginal-relief principle.
_CLEARTAX_SURCHARGE = "https://cleartax.in/s/marginal-relief-surcharge"
# mstock.com — "surcharge must be computed income-wise" when dividend or
# specified CG is present; corroborates the 15% cap reaching dividend tax
# specifically (search-verified 2026-08-01; the attribution *method* for
# dividend commingled in progressive slab income is not stated by any fetched
# source — see engine.dividend_surcharge_attribution's contested_note).
_MSTOCK_SURCHARGE = "https://www.mstock.com/articles/surcharge-on-tax-explained"
_CLEARTAX_CESS = "https://cleartax.in/s/cess-on-income-tax"
# charteredclub 288A/288B page — both round to nearest ₹10, paise ignored,
# last digit >= 5 up, < 5 down.
_CC_288 = "https://www.charteredclub.com/rounding-off-in-income-tax-section-288a-288b/"
# Phase 4 interest sources, verified by WebFetch (2026-07-29):
# cleartax 234B page — 1% pm part-month-as-full, 90% assessed-tax trigger,
# runs from 1 Apr of the AY until paid, base "rounded off in such a way that
# any fraction of a hundred is ignored" (Rule 119A), and the ₹10,000
# advance-tax obligation floor. cleartax 234C page — 15/45/75/100 schedule,
# 1% pm for 3 months (1 for March), the could-not-estimate carve-out for
# capital gains, and the resident-senior-without-PGBP exemption. The 12%/36%
# safe harbors corroborated by myitreturn/indiafilings (search-verified).
_CLEARTAX_234B = "https://cleartax.in/s/interest-imposed-by-income-tax-department-under-section-234b"
_CLEARTAX_234C = "https://cleartax.in/s/interest-imposed-by-income-tax-department-under-section-234c"
_MYITR_234C = "https://help.myitreturn.com/hc/en-us/articles/219731327-Interest-payable-for-deferment-of-Advance-tax-installments-Section-234C"
_ITD_ADVANCE_TAX_PRESUMPTIVE = (
    "https://www.incometaxindia.gov.in/w/"
    "who-is-not-required-to-pay-advance-tax-"
)
_ITD_FINANCE_ACT_2017_S75 = "https://www.incometaxindia.gov.in/w/section-75-86"
# CBDT Circular No. 2/2015 (10-Feb-2015), issued to give effect to the Supreme
# Court's ruling in CIT v. Pranoy Roy [2009] 309 ITR 231, holds that s.234A
# interest is compensatory and is not chargeable on self-assessment tax paid
# before the due date of filing the return, even where the return itself is
# filed late. Primary is the CBDT circular hosted on indiacode.nic.in — the
# PDF is genuine but did not extract cleanly via WebFetch's text conversion
# (2026-08-01); abcaus.in (fetched cleanly) and multiple independent
# secondaries (taxguru, bcajonline, taxscan reporting a following ITAT ruling)
# converge on the same circular number and holding.
_CBDT_CIRCULAR_2_2015 = (
    "https://upload.indiacode.nic.in/showfile?actid=AC_CEN_2_2_00039_196143_"
    "1524045010860&type=circular&filename=ita-circulars-section-234a-"
    "circular-no-2-2015-dated-10-2-2015.pdf"
)
_ABCAUS_PRANOY_ROY = (
    "https://abcaus.in/income-tax/interest-us-234a-cant-be-levied-self-"
    "assessment-tax-paid-before-due-date-filing-itr.html"
)

TABLE = RuleTable([
    Rule(key="holding.listed_equity.lt_months", value=12,
         authority="s.2(42A) proviso — listed securities / equity-oriented units",
         source_primary=_IK_2_42A, source_secondary=_CLEARTAX_STCG,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="holding.listed_nonequity.lt_months", value=12,
         authority="s.2(42A) first proviso as amended by Finance (No. 2) Act, 2024, "
                   "s.3(b) — deletes '(other than a unit)'; listed units (gold/silver "
                   "ETF, listed debt/hybrid/REIT/InVIT/AIF/business-trust units) are "
                   "long-term after more than 12 months, no acquisition-date "
                   "grandfathering. Retrospective from 23-Jul-2024. For AY 2026-27 "
                   "gold/silver ETFs are also outside s.50AA (s.21(b) of the same Act, "
                   "w.e.f. 1-Apr-2026 — SMF = >65% debt / qualifying FoF), so the "
                   "ordinary holding-period test governs",
         source_primary=_EGAZETTE_FA_NO2_2024, source_secondary=_TAXMANN_CG_FA2024,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="holding.other.lt_months", value=24,
         authority="s.2(42A) opening portion as amended by Finance (No. 2) Act, 2024, "
                   "s.3(b)(i) — 'thirty-six months' -> 'twenty-four months', w.e.f. "
                   "23-Jul-2024 (the same amendment whose first-proviso limb sets the "
                   "12-month listed threshold). 24-month long-term threshold for capital "
                   "assets outside the 12-month listed limb (unlisted shares, immovable "
                   "property, physical gold, etc.)",
         source_primary=_EGAZETTE_FA_NO2_2024, source_secondary=_QUICKO_HP,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="s50aa.acquired_from", value=date(2023, 4, 1),
         authority="s.50AA — specified mutual fund; units acquired on/after 1-Apr-2023",
         source_primary=_IK_50AA, source_secondary=_CLEARTAX_50AA,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s50aa.applies", value=True,
         authority="s.50AA — gains on units of a specified mutual fund always short-term "
                   "(slab), any holding. AY 2026-27 SMF definition (Finance (No. 2) Act, "
                   "2024, s.21(b), w.e.f. 1-Apr-2026): fund investing >65% in debt/"
                   "money-market (or FoF into such) — not ordinary gold ETFs",
         source_primary=_EGAZETTE_FA_NO2_2024, source_secondary=_TAXGURU_50AA_FA2024,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s115bbh.applies", value=Decimal("0.30"),
         authority="s.115BBH — VDA gains taxed at flat 30%, any holding period",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="settled"),
    # --- Phase 2: set-off & carry-forward ---
    Rule(key="s70.stcl_setoff_any_cg", value=True,
         authority="s.70(2) — current-year STCL sets off against ST and LT capital gains",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s70.ltcl_setoff_ltcg_only", value=True,
         authority="s.70(3) — current-year LTCL sets off against LTCG only",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s71.capital_loss_no_interhead", value=True,
         authority="s.71(3) — capital loss never sets off against any other head",
         source_primary=_IK_71, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_stcl_setoff_any_cg", value=True,
         authority="s.74(1)(a) — b/f STCL sets off against ST and LT capital gains",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_ltcl_setoff_ltcg_only", value=True,
         authority="s.74(1)(b) — b/f LTCL sets off against LTCG only",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_years", value=8,
         authority="s.74(2) — capital losses carried forward max 8 AYs after the loss AY",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s80.timely_return_required", value=True,
         authority="s.80 r/w s.139(3) — loss not determined in a timely loss-year return "
                   "cannot be carried forward under s.74",
         source_primary=_IK_80, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s115bbh.loss_setoff_disallowed", value=True,
         authority="s.115BBH(2)(b) — VDA loss: no set-off against any income, no carry-forward",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="contested",
         contested_note="Applied per item: loss on one VDA is not netted against gain on "
                        "another (enacted 'any provision of this Act' wording + the "
                        "government's Mar-2022 clarification dropping 'other'; early "
                        "practitioner debate existed on intra-VDA netting)."),
    Rule(key="engine.cg_setoff_order", value=("stcg_slab", "stcg_111a", "ltcg_112", "ltcg_112a"),
         authority="engine policy — statute prescribes no absorption order across buckets",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Ordering changes per-bucket totals that Phase 3 taxes at different "
                        "rates. Policy: within each term, slab buckets before concession "
                        "buckets; LTCL (restricted, s.70(3)) gets first claim on LTCG before "
                        "STCL spillover. Revisit against the ITD utility in Phase 3+."),
    # --- Phase 3: rate application ---
    # Slab tuples: (upper_bound_or_None, rate_str), cumulative from 0.
    Rule(key="slab.new_regime",
         value=((400000, "0"), (800000, "0.05"), (1200000, "0.10"), (1600000, "0.15"),
                (2000000, "0.20"), (2400000, "0.25"), (None, "0.30")),
         authority="s.115BAC(1A) as amended by Finance Act 2025 — FY 2025-26 slabs",
         source_primary=_CLEARTAX_SLABS, source_secondary=_PIB_BUDGET_2025,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="slab.old_below60",
         value=((250000, "0"), (500000, "0.05"), (1000000, "0.20"), (None, "0.30")),
         authority="Finance Act rates, old regime, individual below 60",
         source_primary=_CLEARTAX_SLABS, source_secondary=_PIB_BUDGET_2025,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="slab.old_senior",
         value=((300000, "0"), (500000, "0.05"), (1000000, "0.20"), (None, "0.30")),
         authority="Finance Act rates, old regime, senior citizen (60-79)",
         source_primary=_CLEARTAX_SLABS, source_secondary=_PIB_BUDGET_2025,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="slab.old_super_senior",
         value=((500000, "0"), (1000000, "0.20"), (None, "0.30")),
         authority="Finance Act rates, old regime, super senior (80+)",
         source_primary=_CLEARTAX_SLABS, source_secondary=_PIB_BUDGET_2025,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rebate.87a_new", value={"threshold": 1200000, "max": 60000},
         authority="s.87A (as amended by Finance Act 2025) — new regime: rebate up to "
                   "₹60,000 where slab_base (normal + slab-rate-STCG income, after the "
                   "s.288A rounding delta, before basic-exemption adjustment — i.e. "
                   "excluding 111A/112/112A) is ≤ ₹12L; offsets slab-rate tax only; "
                   "marginal relief above ₹12L is computed on that same slab_base",
         source_primary=_ITD_87A_FAQ_FY2526, source_secondary=_TAXTMI_87A,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Finance Act 2025 inserted a proviso taking 111A/112/112A income "
                        "out of s.87A's scope entirely — both the ₹12L eligibility test and "
                        "marginal relief use slab_base, not total income (ti). Multiple "
                        "secondary sources (TaxGuru, TaxTMI, A2Z Taxcorp) converge on this "
                        "reading for 111A/112/112A specifically; kept 'contested' rather "
                        "than 'settled' because the primary incometaxindia.gov.in FAQ 403s "
                        "to direct fetch and the bare gazetted proviso text itself was not "
                        "independently read here. None of those sources address VDA "
                        "(s.115BBH, a separate Chapter-XII regime) — rates.py refuses "
                        "rather than extends this exclusion to VDA on its own inference "
                        "whenever doing so would change the computed rebate."),
    Rule(key="rebate.87a_old", value={"threshold": 500000, "max": 12500},
         authority="s.87A — old regime: rebate up to ₹12,500 where total income ≤ ₹5L",
         source_primary=_CLEARTAX_SLABS, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rate.stcg_111a", value=Decimal("0.20"),
         authority="s.111A — 20% for transfers on/after 23-Jul-2024 (Finance (No.2) Act 2024)",
         source_primary=_BAJAJAMC_CG, source_secondary=_CLEARTAX_STCG,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="rate.ltcg_112a", value=Decimal("0.125"),
         authority="s.112A — 12.5% for transfers on/after 23-Jul-2024",
         source_primary=_BAJAJAMC_CG, source_secondary=_CLEARTAX_112,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="exemption.ltcg_112a", value=125000,
         authority="s.112A — first ₹1.25L of 112A LTCG exempt (aggregate, per AY)",
         source_primary=_BAJAJAMC_CG, source_secondary=_CLEARTAX_112,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="s55.grandfather_112a_coa", value=True,
         authority="s.55(2)(ac) — COA of an equity share/equity-MF unit acquired "
                   "before 1-Feb-2018, for s.112A purposes, is the higher of actual "
                   "cost or the lower of FMV as on 31-Jan-2018 and the full value of "
                   "consideration on transfer",
         source_primary=_IK_55, source_secondary=_MSASSOCIATES_55,
         effective_from=date(2018, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rate.ltcg_112", value=Decimal("0.125"),
         authority="s.112 — 12.5% without indexation for transfers on/after 23-Jul-2024",
         source_primary=_CLEARTAX_112, source_secondary=_QUICKO_112,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="s112.land_indexation_option_before", value=date(2024, 7, 23),
         authority="s.112 proviso — resident's land/building acquired before 23-Jul-2024 may "
                   "opt 20% with indexation instead of 12.5% without",
         source_primary=_CLEARTAX_112, source_secondary=_QUICKO_112,
         effective_from=date(2024, 7, 23), effective_to=None, confidence="settled"),
    Rule(key="basic_exemption.adjust_against_special_cg", value=True,
         authority="provisos to s.111A(1)/s.112(1)/s.112A(2) — RESIDENT individuals set "
                   "unexhausted basic exemption against 111A/112/112A gains (both regimes)",
         source_primary=_QUICKO_112, source_secondary=_UPSTOX_BEL,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="engine.basic_exemption_adjust_order", value=("stcg_111a", "ltcg_112", "ltcg_112a"),
         authority="engine policy — absorption order across special buckets is statute-silent",
         source_primary=_QUICKO_112, source_secondary=_UPSTOX_BEL,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Highest-rate-first (20% 111A before 12.5% 112/112A) is the "
                        "taxpayer-favorable order; the ITD utility's order has not been "
                        "independently verified."),
    Rule(key="s115bbh.no_basic_exemption", value=True,
         authority="s.115BBH — flat 30% on VDA income; no basic-exemption adjustment, "
                   "no slab benefit",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="settled"),
    # Surcharge bands: (lower_exclusive, upper_inclusive_or_None, rate_str) on total income.
    Rule(key="surcharge.bands",
         value=((5000000, 10000000, "0.10"), (10000000, 20000000, "0.15"),
                (20000000, 50000000, "0.25"), (50000000, None, "0.37")),
         authority="Finance Act — surcharge on individuals: 10%>50L, 15%>1cr, 25%>2cr, 37%>5cr",
         source_primary=_CLEARTAX_SURCHARGE, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="surcharge.new_regime_cap", value=Decimal("0.25"),
         authority="s.115BAC — surcharge capped at 25% under the new regime",
         source_primary=_CLEARTAX_SURCHARGE, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="surcharge.cg_dividend_cap", value=Decimal("0.15"),
         authority="surcharge on tax on s.111A/112/112A gains (and dividend) capped at 15%",
         source_primary=_CLEARTAX_SURCHARGE, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="engine.dividend_surcharge_attribution", value=True,
         authority="engine policy — surcharge.cg_dividend_cap's 15% cap on dividend "
                   "tax is settled, but the Act doesn't prescribe how to compute tax "
                   "'attributable to' dividend when it's commingled in progressive "
                   "slab income (unlike 111A/112/112A, which are already separately "
                   "rate-bucketed); engine attributes it as the marginal top slice "
                   "of slab_base, consistent with the existing marginal-relief "
                   "shave-slab-first policy (see surcharge.marginal_relief)",
         source_primary=_CLEARTAX_SURCHARGE, source_secondary=_MSTOCK_SURCHARGE,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Attribution order matters when both dividend and CG are "
                        "present with a surcharge-rate step in between. Policy: "
                        "dividend attributed against the marginal slab-rate slice; "
                        "CG buckets keep their own already-settled flat-rate tax as "
                        "the capped amount. Revisit against the ITD utility if this "
                        "engine is ever validated against real portal output."),
    Rule(key="surcharge.marginal_relief", value=True,
         authority="proviso to surcharge — tax+surcharge capped at tax-at-threshold plus "
                   "income in excess of the threshold",
         source_primary=_CLEARTAX_SURCHARGE, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="With mixed slab/special income the threshold-income recomputation "
                        "shaves slab income first (engine policy); refuses if slab income "
                        "cannot absorb the shave."),
    Rule(key="cess.health_education", value=Decimal("0.04"),
         authority="4% health & education cess on income-tax plus surcharge",
         source_primary=_CLEARTAX_CESS, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rounding.income_288a", value=10,
         authority="s.288A — total income rounded to nearest ₹10 (paise ignored; last digit "
                   "≥5 up, <5 down)",
         source_primary=_CC_288, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rounding.tax_288b", value=10,
         authority="s.288B — tax payable/refund rounded to nearest ₹10",
         source_primary=_CC_288, source_secondary=_CLEARTAX_SLABS,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    # --- Phase 4: advance-tax interest ---
    Rule(key="interest.rate_pm", value=Decimal("0.01"),
         authority="s.234A/234B/234C — simple interest 1% per month or part thereof",
         source_primary=_CLEARTAX_234B, source_secondary=_CLEARTAX_234C,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="rule119a.interest_base_round_down", value=100,
         authority="Rule 119A — interest base rounded to ₹100 with any fraction "
                   "of one hundred rupees ignored (i.e. rounded down)",
         source_primary=_CLEARTAX_234B, source_secondary=_CC_288,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s208.advance_tax_threshold", value=10000,
         authority="s.208 — advance tax payable only if net liability exceeds ₹10,000",
         source_primary=_CLEARTAX_234B, source_secondary=_CLEARTAX_234C,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s207.senior_no_advance_tax", value=True,
         authority="s.207(2) — resident individual 60+ with no business/profession "
                   "income owes no advance tax (so no 234B/234C)",
         source_primary=_CLEARTAX_234C, source_secondary=_CLEARTAX_234B,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s234b.advance_shortfall_trigger", value=Decimal("0.90"),
         authority="s.234B — applies when advance tax paid is below 90% of assessed tax",
         source_primary=_CLEARTAX_234B, source_secondary=_CLEARTAX_234C,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s234a.sat_before_due_date_reduces_base", value=True,
         authority="CIT v. Pranoy Roy [2009] 309 ITR 231 (SC); CBDT Circular No. 2/2015 "
                   "(10-Feb-2015) — s.234A interest is compensatory and not chargeable on "
                   "self-assessment/other tax paid on or before the return due date, even "
                   "if the return itself is filed late",
         source_primary=_CBDT_CIRCULAR_2_2015, source_secondary=_ABCAUS_PRANOY_ROY,
         effective_from=date(2009, 1, 1), effective_to=None, confidence="settled"),
    # (month, day, cumulative %, safe-harbor % or "", months of interest);
    # month 3 falls in the FY's closing calendar year, the rest in its opening.
    Rule(key="s234c.schedule",
         value=((6, 15, "0.15", "0.12", 3), (9, 15, "0.45", "0.36", 3),
                (12, 15, "0.75", "", 3), (3, 15, "1.00", "", 1)),
         authority="s.234C(1) — instalments 15%/45%/75%/100% due 15 Jun/Sep/Dec/Mar; "
                   "1% pm for 3 months (1 month for March); 12%/36% safe harbors for "
                   "the first two instalments",
         source_primary=_CLEARTAX_234C, source_secondary=_MYITR_234C,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s234c.schedule_presumptive_44ad_44ada",
         value=((3, 15, "1.00", "", 1),),
         authority="s.234C(1)(b) — assessee declaring profits u/s 44AD(1) or "
                   "44ADA(1) pays 100% advance tax by 15 Mar; 1% for one month "
                   "on any shortfall",
         source_primary=_ITD_FINANCE_ACT_2017_S75,
         source_secondary=_ITD_ADVANCE_TAX_PRESUMPTIVE,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s234c.cg_carveout", value=True,
         authority="proviso to s.234C(1) — no 234C interest on shortfall attributable to "
                   "capital gains (incl. VDA) accruing after an instalment date, provided "
                   "the tax is paid in the remaining instalments / by 31 Mar",
         source_primary=_CLEARTAX_234C, source_secondary=_MYITR_234C,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Engine attributes tax to a late-accruing item proportionally to "
                        "its share of the bucket's gains (post-112A-exemption, plus cess); "
                        "refuses when surcharge applies, when a special item is a loss, or "
                        "when slab-rate CG is sold after the first instalment — those "
                        "attributions are not statute-determined."),
])
