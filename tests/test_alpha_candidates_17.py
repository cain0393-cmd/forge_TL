import os
import pandas as pd
import pytest

def test_ledger_exists():
    assert os.path.exists('data/alpha_candidate_ledger.csv')

def test_candidate_count():
    df = pd.read_csv('data/alpha_candidate_ledger.csv')
    assert 15 <= len(df) <= 20

def test_ledger_schema():
    df = pd.read_csv('data/alpha_candidate_ledger.csv')
    required_cols = [
        'candidate_id', 'alpha_family', 'candidate_name', 'mechanism', 
        'economic_rationale', 'indian_market_relevance', 'required_data',
        'data_status', 'pit_status', 'execution_feasibility', 'cost_sensitivity',
        'capacity_assessment', 'holding_period', 'competition', 'research_complexity',
        'failure_modes', 'economic_priority_score', 'research_priority'
    ]
    for col in required_cols:
        assert col in df.columns

def test_score_range():
    df = pd.read_csv('data/alpha_candidate_ledger.csv')
    for score in df['economic_priority_score']:
        assert 0 <= score <= 100

def test_valid_classifications():
    df = pd.read_csv('data/alpha_candidate_ledger.csv')
    valid_priorities = {'RESEARCH_READY', 'RESEARCH_PRIORITY', 'DATA_BLOCKED', 'ALPHA_KILLED'}
    assert set(df['research_priority'].unique()).issubset(valid_priorities)

def test_reports_exist():
    assert os.path.exists('docs/alpha_source_map.md')
    assert os.path.exists('docs/task17_decision.md')
