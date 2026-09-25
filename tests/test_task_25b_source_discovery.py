import pandas as pd
import pytest
import os

def get_synthetic_ledger():
    return pd.DataFrame([
        {
            'candidate_id': 'C1',
            'source_name': 'Test Source',
            'url': 'http://test.com',
            'provider': 'Test',
            'data_type': 'OHLCV',
            'granularity': '1-minute',
            'first_date': '2024-04-01',
            'last_date': '2026-04-30',
            'estimated_size_gb': 0.46,
            'equity_coverage': True,
            'futures_coverage': False,
            'options_coverage': False,
            'oi_available': False,
            'bid_ask_available': False,
            'tick_available': False,
            'contract_identifier': False,
            'expiry_identifier': False,
            'continuous_contract': False,
            'pit_suitability': 'Low',
            'survivorship_risk': 'High',
            'corporate_action_risk': 'High',
            'timestamp_quality': 'Medium',
            'provenance_quality': 'Low',
            'license_status': 'UNKNOWN',
            'access_method': 'API',
            'classification': 'REJECTED',
            'rejection_reason': 'Bias',
            'notes': 'None'
        }
    ])

def test_ledger_schema():
    df = get_synthetic_ledger()
    required_cols = [
        'candidate_id', 'source_name', 'url', 'provider', 'data_type', 'granularity',
        'first_date', 'last_date', 'estimated_size_gb', 'equity_coverage', 'futures_coverage',
        'options_coverage', 'oi_available', 'bid_ask_available', 'tick_available',
        'contract_identifier', 'expiry_identifier', 'continuous_contract', 'pit_suitability',
        'survivorship_risk', 'corporate_action_risk', 'timestamp_quality', 'provenance_quality',
        'license_status', 'access_method', 'classification', 'rejection_reason', 'notes'
    ]
    assert all(col in df.columns for col in required_cols)

def test_no_duplicate_candidate_ids():
    df = get_synthetic_ledger()
    assert df['candidate_id'].is_unique

def test_valid_classification_values():
    df = get_synthetic_ledger()
    valid_classes = ['RESEARCH_CANDIDATE', 'PARTIAL_CANDIDATE', 'REJECTED']
    assert df['classification'].isin(valid_classes).all()

def test_required_fields_not_null():
    df = get_synthetic_ledger()
    assert df['candidate_id'].notna().all()
    assert df['source_name'].notna().all()
    assert df['url'].notna().all()

def test_deterministic_output():
    df1 = get_synthetic_ledger()
    df2 = get_synthetic_ledger()
    pd.testing.assert_frame_equal(df1, df2)

def test_valid_date_fields():
    df = get_synthetic_ledger()
    assert len(df['first_date'].iloc[0]) > 0
    assert len(df['last_date'].iloc[0]) > 0
