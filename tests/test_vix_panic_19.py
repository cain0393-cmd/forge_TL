import os
import pandas as pd

def test_results_exist():
    assert os.path.exists('reports/vix_panic/vix_panic_drawdown.csv')
    assert os.path.exists('reports/vix_panic/vix_panic_vix_bands.csv')
    assert os.path.exists('reports/vix_panic/vix_panic_shock_buckets.csv')
    assert os.path.exists('reports/vix_panic/vix_panic_signal_study.md')

def test_markdown_format():
    with open('reports/vix_panic/vix_panic_signal_study.md', 'r') as f:
        content = f.read()
    
    assert "TASK 19 STATUS" in content
    assert "Hypothesis:" in content
    assert "Primary signal:" in content
    assert "Raw signal count:" in content
    assert "Independent panic episodes:" in content
    assert "Final verdict:" in content
