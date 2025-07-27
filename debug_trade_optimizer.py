#!/usr/bin/env python3
"""
Debug version of Trojan Reach Trade Optimizer
"""

import pandas as pd
import numpy as np
from pathlib import Path

def test_data_loading():
    """Test data loading and basic operations"""
    data_path = Path("Analysis/all_imperium_worlds.csv")
    if not data_path.exists():
        # Fallback to old location
        data_path = Path("output/all_imperium_worlds.csv")
        if not data_path.exists():
            print("Data file not found!")
            return
    
    df = pd.read_csv(data_path)
    print(f"Total worlds loaded: {len(df)}")
    
    # Filter for Trojan Reach
    trojan_df = df[df['Sector'] == 'Trojan Reach'].copy()
    print(f"Trojan Reach worlds: {len(trojan_df)}")
    
    if len(trojan_df) == 0:
        print("No Trojan Reach worlds found!")
        print("Available sectors:")
        print(df['Sector'].unique()[:20])
        return
    
    # Test first few rows
    print("\nFirst 3 Trojan Reach worlds:")
    for i, row in trojan_df.head(3).iterrows():
        print(f"  {row['Name']} ({row['Hex']}) - Starport: {row['Starport']}")
        print(f"    Trade Codes: {row['TradeCodes']}")
        print(f"    Resource Units: {row['ResourceUnits']}")
        print()
    
    # Test trade code parsing
    test_row = trojan_df.iloc[0]
    trade_codes_str = str(test_row['TradeCodes'])
    print(f"Testing trade codes parsing for {test_row['Name']}:")
    print(f"  Raw: {test_row['TradeCodes']}")
    print(f"  String: {trade_codes_str}")
    
    try:
        trade_codes = eval(trade_codes_str) if trade_codes_str != 'nan' else []
        print(f"  Parsed: {trade_codes}")
    except Exception as e:
        print(f"  Parse error: {e}")
    
    # Test hex distance calculation
    hex1 = str(trojan_df.iloc[0]['Hex']).zfill(4)
    hex2 = str(trojan_df.iloc[1]['Hex']).zfill(4)
    
    print(f"\nTesting hex distance:")
    print(f"  Hex1: {hex1}")
    print(f"  Hex2: {hex2}")
    
    try:
        x1, y1 = int(hex1[:2]), int(hex1[2:])
        x2, y2 = int(hex2[:2]), int(hex2[2:])
        
        dx = x2 - x1
        dy = y2 - y1
        
        if (dx >= 0 and dy >= 0) or (dx < 0 and dy < 0):
            distance = max(abs(dx), abs(dy))
        else:
            distance = abs(dx) + abs(dy)
            
        print(f"  Distance: {distance} parsecs")
    except Exception as e:
        print(f"  Distance calculation error: {e}")

if __name__ == "__main__":
    test_data_loading()
