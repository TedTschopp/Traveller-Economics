#!/usr/bin/env python3
"""
Debug script to check API response structure
"""

import requests
import json

# Test the API directly
def debug_api():
    print("Testing Traveller Map API structure...")
    
    # Test universe endpoint
    url = "https://travellermap.com/api/universe"
    params = {
        "requireData": 1,
        "milieu": "M1105",
        "tag": "Official"
    }
    
    print(f"Requesting: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response type: {type(data)}")
        print(f"Response length: {len(data) if isinstance(data, list) else 'Not a list'}")
        
        if isinstance(data, list) and len(data) > 0:
            print("\nFirst sector structure:")
            first_sector = data[0]
            print(f"Type: {type(first_sector)}")
            print(f"Keys: {first_sector.keys() if isinstance(first_sector, dict) else 'Not a dict'}")
            print(f"Full structure: {json.dumps(first_sector, indent=2)}")
        else:
            print(f"Unexpected response: {data}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
