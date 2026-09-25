import pytest
import os
import csv
from datetime import datetime

from forge_tl.universe.nifty50 import Nifty50UniverseProvider

@pytest.fixture
def provider():
    # Use the actual ledger in data/universe/nifty50_event_ledger.csv
    return Nifty50UniverseProvider(ledger_path="data/universe/nifty50_event_ledger.csv")

def test_anchor_membership(provider):
    # 2016-03-31 -> 50 members
    members = provider.get_membership("2016-03-31")
    assert len(members) == 50
    assert "ACC" in members
    assert "YESBANK" in members

def test_date_before_first_event(provider):
    # Tata Motors DVR added on 2016-04-01. Anchor is 2016-03-31.
    with pytest.raises(ValueError, match="Pre-anchor dates are not supported"):
        provider.get_membership("2016-01-01")

def test_exact_effective_date_boundary(provider):
    # TATAMTRDVR included effective 2016-04-01
    assert "TATAMTRDVR" not in provider.get_membership("2016-03-31")
    assert "TATAMTRDVR" in provider.get_membership("2016-04-01")

def test_day_before_effective_date(provider):
    # Grasim removed 2017-05-26
    assert "GRASIM" in provider.get_membership("2017-05-25")

def test_day_after_effective_date(provider):
    assert "GRASIM" not in provider.get_membership("2017-05-26")
    assert "GRASIM" not in provider.get_membership("2017-05-27")

def test_tata_motors_dvr_51_member_period(provider):
    members = provider.get_membership("2017-03-31")
    assert len(members) == 51
    assert "TATAMTRDVR" in members

def test_tata_motors_dvr_removal(provider):
    # Removed 2017-09-29
    assert "TATAMTRDVR" in provider.get_membership("2017-09-28")
    assert "TATAMTRDVR" not in provider.get_membership("2017-09-29")
    assert len(provider.get_membership("2017-09-29")) == 50

def test_grasim_removal(provider):
    assert "GRASIM" not in provider.get_membership("2017-05-26")

def test_grasim_re_entry(provider):
    # Re-included 2018-04-02
    assert "GRASIM" not in provider.get_membership("2018-04-01")
    assert "GRASIM" in provider.get_membership("2018-04-02")

def test_yes_bank_accelerated_removal(provider):
    # Removed 2020-03-19
    assert "YESBANK" in provider.get_membership("2020-03-18")
    assert "YESBANK" not in provider.get_membership("2020-03-19")
    
def test_jio_financial_inclusion_removal(provider):
    # JIOFIN included 2023-07-20
    assert "JIOFIN" not in provider.get_membership("2023-07-19")
    members_incl = provider.get_membership("2023-07-20")
    assert "JIOFIN" in members_incl
    assert len(members_incl) == 51
    
    # Excluded 2023-09-07
    assert "JIOFIN" in provider.get_membership("2023-09-06")
    members_excl = provider.get_membership("2023-09-07")
    assert "JIOFIN" not in members_excl
    assert len(members_excl) == 50

def test_future_event_cannot_affect_past_membership(provider):
    # 2024-03-28 UPL excluded
    assert "UPL" in provider.get_membership("2024-03-27")
    assert "UPL" not in provider.get_membership("2024-03-28")
    # check past again
    assert "UPL" in provider.get_membership("2018-03-31")

def test_deterministic_repeated_calls(provider):
    res1 = provider.get_membership("2021-06-15")
    res2 = provider.get_membership("2021-06-15")
    assert res1 == res2
    assert res1 is not res2 # should be copies to prevent mutation

import tempfile

def test_malformed_ledger_rejection():
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("event_id,canonical_symbol\n1,AAPL\n")
        temp_name = f.name
    
    try:
        with pytest.raises(ValueError, match="Ledger missing required columns"):
            Nifty50UniverseProvider(temp_name)
    finally:
        import os
        os.remove(temp_name)

def test_unknown_unsupported_pre_anchor_date_behavior(provider):
    with pytest.raises(ValueError, match="Dates beyond 2024-12-31 are not supported"):
        provider.get_membership("2025-01-01")

def test_datetime_and_string_inputs(provider):
    res_str = provider.get_membership("2018-03-31")
    res_dt = provider.get_membership(datetime(2018, 3, 31))
    assert res_str == res_dt

def test_checkpoints(provider):
    # Checkpoints pass
    assert len(provider.get_membership("2016-03-31")) == 50
    assert len(provider.get_membership("2017-03-31")) == 51
    assert len(provider.get_membership("2018-03-31")) == 50
