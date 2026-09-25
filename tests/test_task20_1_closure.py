import os
import pandas as pd

def test_reports_exist():
    assert os.path.exists('docs/task20_1_closure_audit.md')
    assert os.path.exists('data/research/task20_1_closure.csv')

def test_markdown_format():
    with open('docs/task20_1_closure_audit.md', 'r') as f:
        content = f.read()
    
    assert "TASK 20.1 STATUS:" in content
    assert "MOMENTUM BRANCH:" in content
    assert "REVERSAL BRANCH:" in content
    assert "MARKET-ADJUSTED ALPHA:" in content
    assert "CORPORATE-ACTION SENSITIVITY:" in content
    assert "NEXT RESEARCH ACTION:" in content
    assert "TESTS:" in content
    
    # Must use allowed statuses
    allowed_statuses = ["KILLED", "PROVISIONALLY_KILLED", "PROMISING_NEEDS_DEEPER_TEST", "DATA_BLOCKED"]
    status_line = [line for line in content.split('\n') if line in allowed_statuses]
    assert len(status_line) > 0
