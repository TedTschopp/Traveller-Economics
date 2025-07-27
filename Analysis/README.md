# Analysis Directory

This directory contains all economic analysis outputs and trade route calculations for the Traveller Economics project.

## Universal Economic Analysis Files

### Core Data Files
- `all_factions_worlds.csv` - Complete dataset of all 17,643 worlds across 119 political entities
- `all_imperium_worlds.csv` - Dataset focused on Third Imperium worlds
- `faction_statistics.csv` - Statistical summary for all 119 political factions
- `major_faction_statistics.csv` - Statistics for the 7 major political entities
- `sector_statistics.csv` - Sector-level economic statistics

### Economic Analysis Reports
- `all_factions_summary.txt` - Comprehensive summary of universal economic analysis
- `complete_universe_analysis.txt` - Complete economic analysis report
- `summary_report.txt` - Executive summary of economic findings

### Advanced Economic Analysis
- `advanced_economic_indicators.csv` - Gini coefficients, diversity indices, and development classifications
- `advanced_economic_report.txt` - Advanced economic analysis with inequality and volatility metrics
- `economic_clusters.csv` - Identification of high economic activity clusters
- `economic_forecast.csv` - Economic growth projections with trade code adjustments
- `economic_outliers.csv` - Worlds with exceptional economic characteristics
- `trade_routes_analysis.csv` - Inter-sector trade route potential analysis

### Rankings and Classifications
- `ranking_best_starports.csv` - Worlds ranked by starport quality
- `ranking_by_ru_per_capita.csv` - Worlds ranked by Resource Units per capita
- `ranking_by_total_ru.csv` - Worlds ranked by total economic output
- `ranking_most_agricultural.csv` - Top agricultural worlds by output
- `ranking_most_industrial.csv` - Top industrial worlds by output

## Sector-Specific Trade Route Analysis

### Trojan Reach Trade Routes
- `trojan_reach_trade_routes.csv` - Bilateral trade route analysis for Trojan Reach
- `trojan_reach_circuits.csv` - Multi-stop trade circuit analysis
- `TROJAN_REACH_TRADE_ANALYSIS.md` - Comprehensive Trojan Reach trade strategy report

### Ship-Specific Optimizations
- `trojan_reach_j2_c64_circuits.csv` - Optimal circuits for Jump-2 ship with 64 tons cargo
- `trojan_reach_j2_c64_circuit_legs.csv` - Detailed leg-by-leg analysis for J2/64t configuration
- `trojan_reach_j2_c64_analysis.md` - Complete analysis report for J2/64t ship configuration
- `trojan_reach_j3_c100_circuits.csv` - Optimal circuits for Jump-3 ship with 100 tons cargo
- `trojan_reach_j3_c100_circuit_legs.csv` - Detailed leg-by-leg analysis for J3/100t configuration

## Visualizations
- `visualizations/` - Directory containing charts and graphs of economic data

## Data Sources
All analysis is based on official Traveller Map API data (1105 Imperial timeline) using canonical world data and economic extensions.

## Analysis Methodology
- **Resource Units Calculation**: R × L × I × E formula from Economic Extensions
- **Trade Profit Modeling**: Factors in starport quality, population, economic strength, and distance
- **Circuit Optimization**: Considers jump range constraints and cargo capacity limitations
- **Economic Indicators**: Uses standard economic metrics including Gini coefficients and diversity indices

## Usage
These files are generated automatically by the various analysis scripts in the main directory. To regenerate:

1. **Universal Analysis**: Run `run_all_factions.py` or `all_factions_analysis.py`
2. **Advanced Analysis**: Run `advanced_analysis.py`
3. **Trade Routes**: Run `universal_trade_circuit_optimizer.py` with desired parameters

All scripts are configured to save outputs to this Analysis directory by default.
