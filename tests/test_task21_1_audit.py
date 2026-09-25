import os
import pandas as pd

def test_reports_exist():
    assert os.path.exists('docs/task21_1_result_audit.md')
    assert os.path.exists('data/research/task21_1_reconciliation.csv')

def test_format():
    with open('docs/task21_1_result_audit.md', 'r') as f:
        content = f.read()
        
    assert "TASK 21.1 STATUS:" in content
    assert "FINAL TASK 21 STATUS:" in content
    
    allowed = ["AUDIT_PASS", "AUDIT_FAIL", "AUDIT_PASS_WITH_LIMITATION"]
    status_line = [line for line in content.split('\n') if line in allowed]
    assert len(status_line) > 0
    
    allowed_final = ["ALPHA_SURVIVES", "PROMISING_NEEDS_DEEPER_TEST", "KILLED", "DATA_BLOCKED"]
    status_line_final = [line for line in content.split('\n') if line in allowed_final]
    assert len(status_line_final) > 0
