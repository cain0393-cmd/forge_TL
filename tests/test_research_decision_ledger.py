import os
import pandas as pd
import pytest

def test_ledger_exists():
    assert os.path.exists('data/research_decision_ledger.csv')

def test_ledger_schema():
    df = pd.read_csv('data/research_decision_ledger.csv')
    required_cols = [
        'strategy_id', 'strategy_name', 'research_task', 'verdict',
        'failure_reason', 'evidence_quality'
    ]
    for col in required_cols:
        assert col in df.columns

def test_verdict_vocabulary():
    df = pd.read_csv('data/research_decision_ledger.csv')
    valid_verdicts = {'KILLED', 'BLOCKED', 'SURVIVING', 'NOT_TESTED'}
    assert set(df['verdict'].unique()).issubset(valid_verdicts)

def test_no_contradictory_verdicts():
    df = pd.read_csv('data/research_decision_ledger.csv')
    for _, row in df.iterrows():
        # It's either KILLED or SURVIVING or BLOCKED, only one primary verdict allowed.
        assert row['verdict'] in ['KILLED', 'BLOCKED', 'SURVIVING', 'NOT_TESTED']

def test_blocked_have_reason():
    df = pd.read_csv('data/research_decision_ledger.csv')
    blocked = df[df['verdict'] == 'BLOCKED']
    for _, row in blocked.iterrows():
        assert pd.notna(row['failure_reason'])
        assert row['failure_reason'] != ""

def test_reports_exist():
    assert os.path.exists('docs/research_decision_audit.md')
    assert os.path.exists('docs/research_next_step.md')

