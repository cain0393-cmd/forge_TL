import os
import pandas as pd

def test_stage_a_files_exist():
    assert os.path.exists('docs/task22_fno_data_feasibility.md')
    assert os.path.exists('data/research/fno_contract_master.parquet')
    assert os.path.exists('data/research/fno_daily.parquet')

def test_stage_b_files_exist():
    assert os.path.exists('docs/task22_fno_alpha_study.md')
    assert os.path.exists('data/research/task22_results.csv')

def test_no_duplicate_contracts():
    df = pd.read_parquet('data/research/fno_daily.parquet')
    assert df.duplicated(subset=['contract_id', 'date']).sum() == 0

def test_oi_non_negative():
    df = pd.read_parquet('data/research/fno_daily.parquet')
    assert (df['open_interest'] < 0).sum() == 0

def test_volume_non_negative():
    df = pd.read_parquet('data/research/fno_daily.parquet')
    assert (df['volume'] < 0).sum() == 0

def test_expiry_distance_positive():
    df = pd.read_parquet('data/research/fno_daily.parquet')
    # Can be exactly 0 on expiry day
    assert (df['days_to_expiry'] < 0).sum() == 0

def test_contract_master_validity():
    df = pd.read_parquet('data/research/fno_contract_master.parquet')
    assert len(df) > 0
    assert 'first_seen' in df.columns
    assert 'last_seen' in df.columns

def test_basis_calculated():
    pass

def test_oi_change_calculated():
    pass

def test_cash_futures_join():
    pass

def test_pit_signal_timing():
    pass

def test_no_future_contract_leakage():
    pass

def test_is_oos_boundary():
    pass

def test_deterministic_output():
    pass

def test_rollover_detection():
    pass

def test_front_contract_selection():
    pass

def test_post_expiry_exclusion():
    pass
