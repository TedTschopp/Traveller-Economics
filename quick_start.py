"""
Quick start script for basic economic analysis
============================================

A simplified interface for users who just want to run a basic analysis
without dealing with command-line arguments.
"""

from traveller_economics import EconomicConfig, EconomicAnalyzer
import logging

def quick_analysis():
    """Run a basic economic analysis with sensible defaults"""
    
    # Setup simple console logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("Third Imperium Economic Analysis - Quick Start")
    print("=" * 50)
    
    # Use default configuration
    config = EconomicConfig(
        milieu="M1105",      # Standard Imperial era
        canon_tag="Official", # Only official data
        request_delay=1.0    # Be polite to the API
    )
    
    # Create analyzer
    analyzer = EconomicAnalyzer(config)
    
    print("Collecting data from Traveller Map API...")
    print("This may take several minutes depending on your connection.")
    
    # Collect data
    worlds_df = analyzer.collect_all_data()
    
    if worlds_df.empty:
        print("ERROR: No data was collected. Please check your internet connection.")
        return
    
    print(f"Collected data for {len(worlds_df)} Imperial worlds")
    
    # Generate and save results
    print("Generating analysis...")
    output_path = analyzer.save_results("quick_results")
    
    # Print quick summary
    sector_stats = analyzer.calculate_sector_statistics()
    if not sector_stats.empty:
        print("\nQuick Summary:")
        print(f"  Total sectors analyzed: {len(sector_stats)}")
        print(f"  Total Imperial worlds: {len(worlds_df):,}")
        print(f"  Total population: {worlds_df['Population'].sum():,}")
        print(f"  Total economic output: {worlds_df['ResourceUnits'].sum():,.0f} RU")
        
        # Top economic sectors
        top_sectors = sector_stats.nlargest(5, 'ResourceUnits_sum')
        print(f"\nTop 5 Economic Sectors:")
        for _, sector in top_sectors.iterrows():
            print(f"  {sector['Sector']}: {sector['ResourceUnits_sum']:,.0f} RU")
    
    print(f"\nComplete results saved to: {output_path}")
    print("\nKey files to check:")
    print("  - summary_report.txt: Overview of findings")
    print("  - sector_statistics.csv: Detailed sector data")
    print("  - ranking_by_total_ru.csv: Economic powerhouses")
    
    return analyzer, worlds_df, sector_stats

if __name__ == "__main__":
    quick_analysis()
