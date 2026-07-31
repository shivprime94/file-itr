# file-itr

An agent **skill** that helps **any** Indian individual taxpayer prepare and
e-file an Income Tax Return (ITR-1/2/3/4) on the official portal — under **either
the old or the new tax regime**. It reconciles salary + freelance/creator/business
income + capital gains + interest into a correct, fully-verified return,
**compares both regimes and proactively asks for the deduction proofs that lower
tax legally**, fills the portal schedule-by-schedule, fixes validation defects,
and guides the user through payment and e-verification.

Its aim is the **lowest legal tax** — claim every deduction the user genuinely
has and pick the cheaper regime — never to fabricate or inflate anything.

The skill is `skills/itr-india/`. It was distilled from a real end-to-end ITR-3
filing (salaried + content-creator under 44ADA + listed-share STCG + bank
interest) and generalised to cover both regimes and all common filer types.

> ⚠️ **Not professional tax advice.** This skill makes a return *accurate and
> defensible*, not minimised at any cost. Indian tax rules change every
> assessment year — always re-confirm current-year slabs, limits, and forms. The
> taxpayer remains responsible for the figures filed. The agent will never enter
> your password/OTP, make the payment, or submit/e-verify on your behalf — those
> are your actions by design.

## What it covers

- Picking the right form (ITR-1/2/3/4) and **comparing old vs new regime**
  (115BAC / Form 10-IEA) on the user's real numbers to choose the cheaper one.
- **Old-regime deduction catalogue** (80C, 80D, 80CCD/NPS, HRA, home-loan
  interest, 80G, 80E, 80TTA/TTB, …) and a **proactive checklist of documents to
  ask for** so no legitimate deduction is missed.
- Reconciling income to source documents (Form 16, 26AS, AIS, bank statements,
  platform payout files) — one number per head, each tied to a document.
- Presumptive taxation for creators/freelancers/small business (44ADA/44AD,
  CBDT code 16021).
- Capital gains on listed equity/MF/property (111A/112A special rates, quarterly
  breakup for 234C) and interest/dividends in Schedule OS.
- Independent tax computation (both regimes) to verify the portal's math.
- Driving the e-filing portal, with workarounds for its known quirks
  (logout pop-ups, mat-select dropdowns, the trailing-zero bug, silent
  schedule un-confirmation, and the no-account balance-sheet validation defect).
- Handing off payment, submission, and e-verification cleanly.

## Repo layout

```
file-itr/
├── README.md
├── LICENSE
├── itr-india.skill                 # zipped skill — one-click install
└── skills/
    └── itr-india/
        ├── SKILL.md                # workflow + judgment (read first)
        └── references/
            ├── tax-regimes-and-slabs.md
            ├── form-selection-ay2026-27.md
            ├── deductions-old-regime.md
            ├── income-reconciliation.md
            ├── creator-44ada.md
            ├── capital-gains-other-sources.md
            └── portal-workflow.md
```

## Install

### Claude Cowork (desktop)

1. Download `itr-india.skill` from this repo.
2. In Cowork, open the chat and use the **"Save skill"** button that appears when
   a `.skill` file is shared, **or** go to **Settings → Capabilities → Skills**
   and add it. (You can also drag the `.skill` file into the chat and click
   *Save skill*.)
3. The skill now appears in your skills list and triggers automatically when you
   talk about filing Indian taxes.

### Claude Code (CLI)

Skills live under a `skills/` directory that Claude Code reads. Either:

**A) Clone into your project's skills folder**
```bash
git clone https://github.com/shivprime94/file-itr.git
mkdir -p .claude/skills
cp -r file-itr/skills/itr-india .claude/skills/
```

**B) Install for all projects (user-level)**
```bash
git clone https://github.com/shivprime94/file-itr.git
mkdir -p ~/.claude/skills
cp -r file-itr/skills/itr-india ~/.claude/skills/
```

Restart Claude Code (or start a new session) and confirm with `/skills` (or
however your version lists skills). The skill triggers on ITR/tax-filing
requests.

### Any other Claude Agent SDK / custom agent

Place the `skills/itr-india/` folder wherever your agent loads skills from (the
directory containing per-skill folders, each with a `SKILL.md`). The agent reads
the YAML frontmatter `description` to decide when to trigger, and loads
`SKILL.md` + the `references/` files as needed.

## Use

Once installed, just talk to your agent naturally, e.g.:

- "Help me file my ITR for FY 2025-26 — I'm salaried and also do freelance
  content work, and I sold some shares this year."
- "I'm a YouTuber, new tax regime, can you do my income tax return in India?"
- "Reconcile my 26AS and AIS and tell me my total income and tax."
- "I'm stuck on a validation error on the income tax portal for my 44ADA return."
- "I traded crypto on an Indian exchange — made profit on some coins, lost on
  others, 1% TDS was deducted. How is it taxed and which ITR form?"
- "My father is 67, gets pension + FD interest, paid health insurance — old or new
  regime, and how much tax?"
- "I have 80C, a home loan and HRA — is the old or new regime cheaper for me?"

The agent will gather your documents, reconcile income, compute tax, walk the
portal with you, and stop at the payment/submit/e-verify steps for you to
complete.

### What you'll need to provide

Form 16(s), Form 26AS, AIS/TIS, bank statements for the financial year, any
broker/capital-gains statement, and any platform payout files (Stripe/YouTube/
X/etc.). For the portal steps, you log in yourself and the agent drives the form.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is provided "as is", without warranty of any kind. It is not a
substitute for a chartered accountant or a registered tax practitioner. Verify
every figure before filing. The authors are not liable for any filing made using
this skill.
