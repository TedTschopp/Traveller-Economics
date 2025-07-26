#!/usr/bin/env python3
"""Debug TSV data structure from Traveller Map API"""

import requests
import sys

def check_tsv_structure():
    # Test with a known sector
    sector_name = "Spinward Marches"
    url = f"https://travellermap.com/data/{sector_name}/tab"
    params = {"milieu": "M1105"}
    
    print(f"Requesting TSV data for {sector_name}...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.text
    lines = data.strip().split('\n')
    
    print(f"Total lines: {len(lines)}")
    print("\nFirst 10 lines:")
    for i, line in enumerate(lines[:10]):
        print(f"{i+1:2}: {line}")
    
    # Find first non-comment line (headers)
    data_lines = [line for line in lines if not line.startswith('#')]
    if data_lines:
        headers = data_lines[0].split('\t')
        print(f"\nFound {len(headers)} columns:")
        for i, header in enumerate(headers):
            print(f"{i+1:2}: {header}")
        
        if len(data_lines) > 1:
            first_data_row = data_lines[1].split('\t')
            print(f"\nFirst data row has {len(first_data_row)} columns:")
            for i, value in enumerate(first_data_row):
                print(f"{i+1:2}: {value}")

if __name__ == "__main__":
    check_tsv_structure()
