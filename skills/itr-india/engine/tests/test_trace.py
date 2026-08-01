from datetime import date
from decimal import Decimal
import pytest
from engine.model import AssetClass, CapitalGainItem, VdaItem
from engine.rulebase import RuleTable
from engine.rules.ay2026_27 import TABLE
from engine.trace import trace_bucketing

REF = date(2025, 6, 1)


def test_trace_records_rule_key_and_source():
    item = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1),
                           Decimal("30000"), Decimal("0"), stt_paid=True)
    tr = trace_bucketing([item], TABLE, REF)
    line = tr.lines[0]
    assert line.rule_key == "holding.listed_equity.lt_months"
    assert line.source.startswith("http")
    assert "http" in tr.render()


def test_trace_flags_contested_lines():
    # trace_bucketing flags a line iff its classify rule is 'contested'. Build a
    # table where the gold-ETF path rule is contested and assert the line is
    # flagged. (Tests the flagging behaviour itself, not which production rule
    # happens to be contested — holding.listed_nonequity.lt_months is settled.)
    from dataclasses import replace
    base = TABLE.get("holding.listed_nonequity.lt_months", REF)
    contested = replace(base, confidence="contested",
                        contested_note="synthetic — exercises contested flagging")
    tbl = RuleTable([r for r in TABLE.all()
                     if r.key != "holding.listed_nonequity.lt_months"] + [contested])
    item = CapitalGainItem(AssetClass.GOLD_ETF_LISTED, date(2025, 4, 1), date(2026, 5, 1),
                           Decimal("20000"), Decimal("0"))
    tr = trace_bucketing([item], tbl, REF)
    assert len(tr.contested()) == 1


def test_trace_raises_when_rule_key_unresolvable():
    # VDA-path citation invariant: classify() returns "s115bbh.applies" for VdaItem
    # without consulting the table itself. If that key is missing from the table,
    # trace_bucketing's own table.get(rule_key, ...) lookup must raise rather than
    # silently produce a trace line with no citation.
    table_missing_vda_rule = RuleTable(
        [r for r in TABLE.all() if r.key != "s115bbh.applies"])
    item = VdaItem(Decimal("100000"), Decimal("60000"))
    with pytest.raises(KeyError):
        trace_bucketing([item], table_missing_vda_rule, REF)
