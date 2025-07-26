#!/usr/bin/env python3
"""
Run complete economic analysis for ALL political factions in the Traveller universe
"""

import argparse
import logging
from all_factions_analysis import AllFactionsAnalyzer
from traveller_economics import EconomicConfig

def main():
    parser = argparse.ArgumentParser(description='Analyze economic activity for ALL political factions')
    parser.add_argument('--milieu', default='M1105', help='Milieu code (default: M1105)')
    parser.add_argument('--canon', default='Official', help='Canon level (default: Official)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=" * 60)
    print("TRAVELLER UNIVERSE: ALL FACTIONS ECONOMIC ANALYSIS")
    print("=" * 60)
    print(f"Milieu: {args.milieu}")
    print(f"Canon Level: {args.canon}")
    print(f"Output Directory: {args.output_dir}")
    print("=" * 60)
    
    try:
        # Configure analysis
        config = EconomicConfig(
            milieu=args.milieu,
            canon_tag=args.canon
        )
        
        # Run all factions analysis
        analyzer = AllFactionsAnalyzer(config, output_dir=args.output_dir)
        results = analyzer.run_all_factions_analysis()
        
        print("\n" + "=" * 60)
        print("ALL FACTIONS ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total worlds processed: {results['total_worlds']:,}")
        print(f"Political entities: {results['total_factions']:,}")  
        print(f"Major factions: {results['major_factions']:,}")
        print(f"\nCheck the '{args.output_dir}' directory for results:")
        print("- all_factions_worlds.csv - Complete world database")
        print("- faction_statistics.csv - Detailed faction statistics")
        print("- major_faction_statistics.csv - Major faction summaries")
        print("- all_factions_summary.txt - Executive summary")
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
