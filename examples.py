#!/usr/bin/env python3
"""
Example analysis scripts for Traveller Economic Analysis
========================================================

Demonstrates common use cases and analysis patterns.
"""

from traveller_economics import EconomicConfig, EconomicAnalyzer
import pandas as pd
import logging

def example_1_basic_analysis():
    """Example 1: Basic economic analysis of the Third Imperium"""
    print("Example 1: Basic Third Imperium Economic Analysis")
    print("=" * 50)
    
    # Configure for standard Imperial era
    config = EconomicConfig(milieu="M1105", canon_tag="Official")
    analyzer = EconomicAnalyzer(config)
    
    # Collect data (this may take several minutes)
    print("Collecting sector data from Traveller Map API...")
    worlds_df = analyzer.collect_all_data()
    
    if worlds_df.empty:
        print("No data collected. Check network connection.")
        return
    
    # Basic statistics
    print(f"\nCollected data for {len(worlds_df):,} Imperial worlds")
    print(f"Total population: {worlds_df['Population'].sum():,}")
    print(f"Total economic output: {worlds_df['ResourceUnits'].sum():,.0f} RU")
    
    # Top economic worlds
    print("\nTop 10 Economic Worlds:")
    top_worlds = worlds_df.nlargest(10, 'ResourceUnits')
    for _, world in top_worlds.iterrows():
        print(f"  {world['Name']} ({world['Sector']}): {world['ResourceUnits']:,.0f} RU")
    
    # Save results
    analyzer.save_results("example_1_output")
    print("\nResults saved to example_1_output/")

def example_2_sector_comparison():
    """Example 2: Compare specific sectors"""
    print("\nExample 2: Sector Comparison Analysis")
    print("=" * 40)
    
    # Use cached data if available
    config = EconomicConfig(milieu="M1105", request_delay=0.5)
    analyzer = EconomicAnalyzer(config)
    
    worlds_df = analyzer.collect_all_data()
    if worlds_df.empty:
        return
    
    # Focus on key sectors
    key_sectors = ['Core', 'Spinward Marches', 'Solomani Rim', 'Deneb', 'Vland']
    sector_data = worlds_df[worlds_df['Sector'].isin(key_sectors)]
    
    if sector_data.empty:
        print("Key sectors not found in data")
        return
    
    # Calculate sector statistics
    sector_stats = sector_data.groupby('Sector').agg({
        'Name': 'count',
        'ResourceUnits': ['sum', 'mean'],
        'Population': 'sum',
        'IsRi': 'sum',
        'IsIn': 'sum',
        'IsAg': 'sum'
    }).round(2)
    
    sector_stats.columns = ['Worlds', 'Total_RU', 'Avg_RU', 'Population', 'Rich', 'Industrial', 'Agricultural']
    
    print("\nSector Comparison:")
    print(sector_stats)
    
    # Find most efficient sector
    sector_stats['RU_per_capita'] = sector_stats['Total_RU'] / sector_stats['Population']
    most_efficient = sector_stats['RU_per_capita'].idxmax()
    print(f"\nMost economically efficient sector: {most_efficient}")

def example_3_trade_analysis():
    """Example 3: Trade pattern analysis"""
    print("\nExample 3: Trade Pattern Analysis")
    print("=" * 35)
    
    config = EconomicConfig(milieu="M1105")
    analyzer = EconomicAnalyzer(config)
    
    worlds_df = analyzer.collect_all_data()
    if worlds_df.empty:
        return
    
    # Analyze trade patterns
    print(f"Trade Code Distribution across {len(worlds_df)} Imperial worlds:")
    
    trade_codes = ['Ag', 'In', 'Ri', 'Hi', 'Po', 'Na']
    for code in trade_codes:
        count = worlds_df[f'Is{code}'].sum()
        percentage = (count / len(worlds_df)) * 100
        print(f"  {code}: {count:,} worlds ({percentage:.1f}%)")
    
    # Economic output by trade type
    print("\nAverage Economic Output by Trade Code:")
    for code in trade_codes:
        mask = worlds_df[f'Is{code}'] == True
        if mask.any():
            avg_ru = worlds_df[mask]['ResourceUnits'].mean()
            print(f"  {code}: {avg_ru:.1f} RU average")
    
    # Find complementary sectors (Ag + In)
    ag_sectors = worlds_df[worlds_df['IsAg'] == True]['Sector'].value_counts()
    in_sectors = worlds_df[worlds_df['IsIn'] == True]['Sector'].value_counts()
    
    print(f"\nTop Agricultural Sectors:")
    for sector, count in ag_sectors.head(5).items():
        print(f"  {sector}: {count} agricultural worlds")
    
    print(f"\nTop Industrial Sectors:")
    for sector, count in in_sectors.head(5).items():
        print(f"  {sector}: {count} industrial worlds")

def example_4_economic_outliers():
    """Example 4: Find economic outliers and unusual worlds"""
    print("\nExample 4: Economic Outlier Analysis")
    print("=" * 37)
    
    config = EconomicConfig(milieu="M1105")
    analyzer = EconomicAnalyzer(config)
    
    worlds_df = analyzer.collect_all_data()
    if worlds_df.empty:
        return
    
    # Find economic outliers
    outliers = analyzer.find_economic_outliers(threshold=2.0)
    
    if not outliers.empty:
        print(f"Found {len(outliers)} economic outliers (>2 sigma above sector mean):")
        print("\nTop 10 Economic Outliers:")
        for _, world in outliers.head(10).iterrows():
            print(f"  {world['Name']} ({world['Sector']}): {world['ResourceUnits']:,.0f} RU "
                  f"(z-score: {world['RU_zscore']:.2f})")
    
    # Find unusual combinations
    print("\nUnusual World Combinations:")
    
    # Rich but low population
    rich_low_pop = worlds_df[(worlds_df['IsRi'] == True) & (worlds_df['PopulationExp'] < 5)]
    if not rich_low_pop.empty:
        print(f"\nRich worlds with low population (<10^5): {len(rich_low_pop)}")
        for _, world in rich_low_pop.head(5).iterrows():
            print(f"  {world['Name']} ({world['Sector']}): Pop 10^{world['PopulationExp']}, {world['ResourceUnits']:.0f} RU")
    
    # High population but poor
    hi_pop_poor = worlds_df[(worlds_df['IsHi'] == True) & (worlds_df['IsPo'] == True)]
    if not hi_pop_poor.empty:
        print(f"\nHigh population but poor worlds: {len(hi_pop_poor)}")
        for _, world in hi_pop_poor.head(5).iterrows():
            print(f"  {world['Name']} ({world['Sector']}): Pop 10^{world['PopulationExp']}, {world['ResourceUnits']:.0f} RU")

def example_5_time_comparison():
    """Example 5: Compare different time periods"""
    print("\nExample 5: Time Period Comparison")
    print("=" * 34)
    
    milieux = ["M1105", "M1120"]  # Add more if available
    results = {}
    
    for milieu in milieux:
        print(f"\nAnalyzing {milieu}...")
        config = EconomicConfig(milieu=milieu, request_delay=0.5)
        analyzer = EconomicAnalyzer(config)
        
        worlds_df = analyzer.collect_all_data()
        if not worlds_df.empty:
            results[milieu] = {
                'worlds': len(worlds_df),
                'population': worlds_df['Population'].sum(),
                'total_ru': worlds_df['ResourceUnits'].sum(),
                'avg_ru': worlds_df['ResourceUnits'].mean(),
                'rich_worlds': worlds_df['IsRi'].sum(),
                'industrial': worlds_df['IsIn'].sum()
            }
    
    # Compare results
    if len(results) > 1:
        print("\nTime Period Comparison:")
        comparison_df = pd.DataFrame(results).T
        print(comparison_df)
        
        # Calculate changes
        if "M1105" in results and "M1120" in results:
            pop_change = ((results["M1120"]["population"] - results["M1105"]["population"]) / 
                         results["M1105"]["population"]) * 100
            ru_change = ((results["M1120"]["total_ru"] - results["M1105"]["total_ru"]) / 
                        results["M1105"]["total_ru"]) * 100
            
            print(f"\nChanges from M1105 to M1120:")
            print(f"  Population change: {pop_change:.1f}%")
            print(f"  Economic output change: {ru_change:.1f}%")

def run_all_examples():
    """Run all example analyses"""
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    print("Traveller Economic Analysis - Example Scripts")
    print("=" * 60)
    print("These examples demonstrate various analysis capabilities.")
    print("Note: Initial data collection may take several minutes.\n")
    
    try:
        example_1_basic_analysis()
        example_2_sector_comparison()
        example_3_trade_analysis()
        example_4_economic_outliers()
        # example_5_time_comparison()  # Commented out as it's data intensive
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("Check the example_1_output/ directory for detailed results.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have an internet connection and the required packages installed.")

if __name__ == "__main__":
    run_all_examples()
