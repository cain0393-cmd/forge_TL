import os
import pandas as pd
import pytest

def test_results_exist():
    assert os.path.exists('reports/vix_rv/vix_rv_results.csv')
    assert os.path.exists('reports/vix_rv/vix_rv_yearly.csv')
    assert os.path.exists('reports/vix_rv/vix_rv_regime.csv')
    assert os.path.exists('reports/vix_rv/vix_rv_quantiles.csv')
    assert os.path.exists('reports/vix_rv/vix_rv_vix_bands.csv')
    assert os.path.exists('reports/vix_rv/vix_rv_signal_study.md')

def test_primary_threshold_results():
    df = pd.read_csv('reports/vix_rv/vix_rv_results.csv')
    primary = df[(df['threshold'] == 1.50) & (df['horizon'] == 5)]
    assert not primary.empty
    assert primary.iloc[0]['N_IS'] >= 0

def test_lookahead_columns():
    df = pd.read_csv('reports/vix_rv/vix_rv_results.csv')
    assert 'hit_is' in df.columns
    assert 'excess_is' in df.columns
    assert 'hit_oos' in df.columns
    assert 'excess_oos' in df.columns

def test_markdown_format():
    with open('reports/vix_rv/vix_rv_signal_study.md', 'r') as f:
        content = f.read()
    assert "TASK 18 STATUS" in content
    assert "Hypothesis:" in content
    assert "Primary threshold:" in content
    assert "Primary horizon:" in content
    assert "Final verdict:" in content
