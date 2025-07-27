#!/usr/bin/env python3
"""
Usage Examples for Universal Trade Circuit Optimizer
"""

import subprocess
import sys

def run_example(command, description):
    """Run an example command and show results"""
    print("=" * 80)
    print(f"EXAMPLE: {description}")
    print("=" * 80)
    print(f"Command: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Failed to run example: {e}")
    
    print("\n")

def main():
    """Run usage examples"""
    print("UNIVERSAL TRADE CIRCUIT OPTIMIZER - USAGE EXAMPLES")
    print("=" * 60)
    
    examples = [
        (
            'python3 universal_trade_circuit_optimizer.py "Trojan Reach"',
            "Default Analysis (Jump-2, 64 tons cargo)"
        ),
        (
            'python3 universal_trade_circuit_optimizer.py "Trojan Reach" -j 3 -c 100',
            "Jump-3 Ship with 100 Tons Cargo"
        ),
        (
            'python3 universal_trade_circuit_optimizer.py "Spinward Marches" -j 2 -c 50 -n 3',
            "Small Ship in Spinward Marches (Top 3 circuits only)"
        ),
        (
            'python3 universal_trade_circuit_optimizer.py "Core" -j 1 -c 200 --save',
            "Jump-1 Bulk Trader in Core Sector (Save Results)"
        )
    ]
    
    for command, description in examples:
        run_example(command, description)
    
    print("=" * 80)
    print("AVAILABLE PARAMETERS:")
    print("=" * 80)
    print("Sectors: Any sector name from the Traveller universe")
    print("Jump Range (-j): 1-6 parsecs (default: 2)")
    print("Cargo (-c): Any tonnage (default: 64)")
    print("Circuits (-n): Number to display (default: 10)")
    print("--save: Save results to CSV files")
    print("--min-stops, --max-stops: Circuit length limits")
    print()
    print("For help: python3 universal_trade_circuit_optimizer.py --help")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        main()
    else:
        print("Usage Examples for Universal Trade Circuit Optimizer")
        print("=" * 60)
        print()
        print("BASIC USAGE:")
        print('python3 universal_trade_circuit_optimizer.py "Trojan Reach"')
        print()
        print("CUSTOM SHIP:")
        print('python3 universal_trade_circuit_optimizer.py "Spinward Marches" -j 3 -c 100')
        print()
        print("MULTIPLE PARAMETERS:")
        print('python3 universal_trade_circuit_optimizer.py "Core" -j 1 -c 200 -n 5 --save')
        print()
        print("AVAILABLE SECTORS (examples):")
        print("- Spinward Marches")  
        print("- Trojan Reach")
        print("- Core")
        print("- Reft")
        print("- Deneb")
        print("- Vland")
        print("- And many more...")
        print()
        print("For full examples: python3 usage_examples.py run")
        print("For help: python3 universal_trade_circuit_optimizer.py --help")

if __name__ == "__main__":
    main()
