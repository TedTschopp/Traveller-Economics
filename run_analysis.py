#!/usr/bin/env python3
"""
Main execution script for Traveller Third Imperium Economic Analysis
====================================================================

This script orchestrates the complete economic analysis workflow:
1. Data collection from Traveller Map API
2. Economic metric calculations
3. Statistical analysis and insights
4. Visualization generation
5. Advanced economic modeling

Usage:
    python run_analysis.py [--milieu M1105] [--output-dir results] [--visualizations] [--advanced]
"""

import argparse
import sys
import logging
from pathlib import Path

# Import our analysis modules
from traveller_economics import EconomicConfig, EconomicAnalyzer

# Optional imports for advanced features
try:
    from visualizations import create_visualizations
    VISUALIZATIONS_AVAILABLE = True
except ImportError:
    VISUALIZATIONS_AVAILABLE = False
    logging.warning("Visualization modules not available. Install matplotlib, seaborn, plotly for full functionality.")

try:
    from advanced_analysis import run_advanced_analysis
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYSIS_AVAILABLE = False
    logging.warning("Advanced analysis not available. Install scipy for full functionality.")

def setup_logging(level: str = "INFO"):
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('traveller_economics.log')
        ]
    )

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Analyze Third Imperium economic activity using Traveller Map API data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_analysis.py                           # Basic analysis with default settings
  python run_analysis.py --milieu M1120           # Analyze different time period
  python run_analysis.py --visualizations         # Include charts and graphs
  python run_analysis.py --advanced               # Run advanced economic modeling
  python run_analysis.py --all                    # Run complete analysis suite
        """
    )
    
    parser.add_argument(
        '--milieu', '-m',
        default='M1105',
        help='Traveller milieu to analyze (default: M1105)'
    )
    
    parser.add_argument(
        '--canon-tag', '-c',
        default='Official',
        help='Canon quality tag filter (default: Official)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--cache-dir',
        default='cache',
        help='Directory for caching API responses (default: cache)'
    )
    
    parser.add_argument(
        '--request-delay',
        type=float,
        default=1.0,
        help='Delay between API requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--visualizations', '-v',
        action='store_true',
        help='Generate charts and visualizations'
    )
    
    parser.add_argument(
        '--advanced', '-a',
        action='store_true',
        help='Run advanced economic analysis'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run complete analysis including visualizations and advanced features'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Force fresh downloads (ignore cached data)'
    )
    
    return parser.parse_args()

def validate_dependencies(visualizations: bool, advanced: bool):
    """Check if required dependencies are available"""
    missing_deps = []
    
    if visualizations and not VISUALIZATIONS_AVAILABLE:
        missing_deps.extend(['matplotlib', 'seaborn', 'plotly'])
    
    if advanced and not ADVANCED_ANALYSIS_AVAILABLE:
        missing_deps.extend(['scipy'])
    
    if missing_deps:
        print(f"Missing dependencies for requested features: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True

def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Determine what features to run
    run_visualizations = args.visualizations or args.all
    run_advanced = args.advanced or args.all
    
    # Validate dependencies
    if not validate_dependencies(run_visualizations, run_advanced):
        sys.exit(1)
    
    # Create configuration
    config = EconomicConfig(
        milieu=args.milieu,
        canon_tag=args.canon_tag,
        cache_dir=args.cache_dir,
        request_delay=args.request_delay
    )
    
    logger.info(f"Starting Third Imperium Economic Analysis")
    logger.info(f"Configuration: Milieu={config.milieu}, Canon={config.canon_tag}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Clear cache if requested
    if args.skip_cache:
        cache_path = Path(config.cache_dir)
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
            logger.info("Cache cleared")
    
    try:
        # Create main analyzer
        analyzer = EconomicAnalyzer(config)
        
        # Step 1: Collect all sector data
        logger.info("Phase 1: Data Collection")
        worlds_df = analyzer.collect_all_data()
        
        if worlds_df.empty:
            logger.error("No data collected. Check your network connection and configuration.")
            sys.exit(1)
        
        # Step 2: Calculate sector statistics
        logger.info("Phase 2: Statistical Analysis")
        sector_stats = analyzer.calculate_sector_statistics()
        
        # Step 3: Save basic results
        logger.info("Phase 3: Saving Results")
        output_path = analyzer.save_results(args.output_dir)
        
        # Step 4: Generate visualizations (if requested)
        if run_visualizations and VISUALIZATIONS_AVAILABLE:
            logger.info("Phase 4: Generating Visualizations")
            create_visualizations(worlds_df, sector_stats, args.output_dir)
        
        # Step 5: Advanced analysis (if requested)
        if run_advanced and ADVANCED_ANALYSIS_AVAILABLE:
            logger.info("Phase 5: Advanced Economic Analysis")
            run_advanced_analysis(worlds_df, sector_stats, args.output_dir)
        
        # Final summary
        total_worlds = len(worlds_df)
        total_sectors = len(sector_stats) if not sector_stats.empty else 0
        total_population = worlds_df['Population'].sum()
        total_ru = worlds_df['ResourceUnits'].sum()
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print(f"Processed: {total_worlds:,} worlds across {total_sectors} sectors")
        print(f"Total Population: {total_population:,}")
        print(f"Total Economic Output: {total_ru:,.0f} Resource Units")
        print(f"Results saved to: {output_path}")
        
        if run_visualizations:
            print(f"Visualizations: {output_path}/visualizations/")
        
        if run_advanced:
            print("Advanced analysis: Check *_advanced_*.csv files")
        
        print("\nKey files:")
        print("  - all_imperium_worlds.csv: Complete world database")
        print("  - sector_statistics.csv: Aggregated sector metrics")
        print("  - ranking_*.csv: Various sector rankings")
        print("  - summary_report.txt: Executive summary")
        
        logger.info("Analysis completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        logger.debug("Full error details:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
