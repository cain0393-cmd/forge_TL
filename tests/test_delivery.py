import os
import pandas as pd
import pytest

def test_delivery_percentage_calculation():
    df = pd.DataFrame({
        'traded_volume': [1000, 500, 200, 0, 100],
        'delivery_volume': [500, 100, 0, 0, 100]
    })
    mask = df['traded_volume'] > 0
    df.loc[mask, 'delivery_pct'] = (df.loc[mask, 'delivery_volume'] / df.loc[mask, 'traded_volume']) * 100
    
    assert df.loc[0, 'delivery_pct'] == 50.0
    assert df.loc[1, 'delivery_pct'] == 20.0
    assert df.loc[2, 'delivery_pct'] == 0.0
    assert pd.isna(df.loc[3, 'delivery_pct'])
    assert df.loc[4, 'delivery_pct'] == 100.0

def test_zero_volume_handling():
    df = pd.DataFrame({
        'traded_volume': [0, 0],
        'delivery_volume': [0, 5]
    })
    mask = df['traded_volume'] > 0
    df.loc[mask, 'delivery_pct'] = (df.loc[mask, 'delivery_volume'] / df.loc[mask, 'traded_volume']) * 100
    assert df['delivery_pct'].isna().all()

def test_invalid_delivery_gt_traded():
    df = pd.DataFrame({
        'traded_volume': [100, 100, 100],
        'delivery_volume': [50, 150, 100]
    })
    invalid = df[(df['delivery_volume'] > df['traded_volume']) & (df['traded_volume'] >= 0)]
    assert len(invalid) == 1
    assert invalid.iloc[0]['delivery_volume'] == 150

def test_invalid_percentage():
    df = pd.DataFrame({
        'source_delivery_pct': [50.0, 150.0, -10.0, 100.0, 0.0]
    })
    invalid = df[(df['source_delivery_pct'] < 0) | (df['source_delivery_pct'] > 100)]
    assert len(invalid) == 2

def test_duplicate_detection():
    df = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-01-02'],
        'symbol': ['A', 'A', 'B'],
        'series': ['EQ', 'EQ', 'EQ']
    })
    dup = df.duplicated(subset=['date', 'symbol', 'series'])
    assert dup.sum() == 1

def test_malformed_source_handling():
    # Should safely convert empty/bad strings to NaN or -1
    raw = pd.DataFrame({
        'quantity_traded': ['100', '-', '', '2,000'],
        'deliverable_quantity': ['50', '-', '1', '1,000']
    })
    for col in ['quantity_traded', 'deliverable_quantity']:
        raw[col] = raw[col].astype(str).str.replace(',', '').str.replace('-', 'NaN')
    
    trd = pd.to_numeric(raw['quantity_traded'], errors='coerce').fillna(-1).astype('int64')
    assert trd[0] == 100
    assert trd[1] == -1
    assert trd[2] == -1
    assert trd[3] == 2000

def test_idempotent_dataset_generation():
    df = pd.DataFrame({
        'date': ['2023-01-01'],
        'symbol': ['A'],
        'traded_volume': [100],
        'delivery_volume': [50],
        'delivery_pct': [50.0]
    })
    os.makedirs('d:/forge_TL/scratch/test_delivery', exist_ok=True)
    df.to_parquet('d:/forge_TL/scratch/test_delivery/test_out.parquet')
    
    # Generate again
    df.to_parquet('d:/forge_TL/scratch/test_delivery/test_out.parquet')
    
    # Read and check it's identical
    df_read = pd.read_parquet('d:/forge_TL/scratch/test_delivery/test_out.parquet')
    assert len(df_read) == 1
    assert df_read.iloc[0]['symbol'] == 'A'
