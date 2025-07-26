# Traveller Third Imperium Economic Analysis

A comprehensive toolkit for analyzing economic activity across the Third Imperium using data from the [Traveller Map API](https://travellermap.com/doc/api). This project implements the robust, repeatable workflow described in the original specification to quantify and compare economic activity for every sector of the Third Imperium.

## Features

### Core Analysis
- **Automated Data Collection**: Fetches official sector data from Traveller Map API
- **Economic Metrics Calculation**: Computes Resource Units (RU) from Economic Extensions
- **Sector-Level Aggregation**: Statistics, rankings, and comparisons across all Imperial sectors
- **Trade Pattern Analysis**: Identifies agricultural, industrial, and rich world distributions

### Advanced Analytics
- **Economic Inequality**: Gini coefficient calculations by sector
- **Development Classification**: Categorizes sectors by development level
- **Economic Diversity**: Shannon entropy analysis of trade specialization
- **Trade Route Analysis**: Identifies high-potential inter-sector trade routes
- **Economic Forecasting**: Simple growth projections with trade code modifiers

### Visualizations
- **Interactive Dashboards**: Plotly-based exploration tools
- **Statistical Charts**: Distribution plots, scatter analyses, correlation matrices
- **Sector Heatmaps**: Comparative economic profiles
- **Trade Network Visualizations**: Economic relationships and flows

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Traveller-Economics.git
cd Traveller-Economics

# Install dependencies
pip install -r requirements.txt

# For full functionality (visualizations + advanced analysis)
pip install -r requirements.txt matplotlib seaborn plotly scipy
```

### Basic Usage

```bash
# Run a complete analysis with default settings
python run_analysis.py --all

# Quick analysis with essential features only
python quick_start.py

# Custom analysis options
python run_analysis.py --milieu M1120 --visualizations --advanced
```

### Python API

```python
from traveller_economics import EconomicConfig, EconomicAnalyzer

# Configure analysis
config = EconomicConfig(
    milieu="M1105",           # Imperial era
    canon_tag="Official",     # Vetted data only
    request_delay=1.0         # Be polite to API
)

# Run analysis
analyzer = EconomicAnalyzer(config)
worlds_df = analyzer.collect_all_data()
analyzer.save_results("output")
```

## Data Sources and Methodology

### Traveller Map API Integration
- **Universe Endpoint**: Enumerates all sectors with official data
- **Sector Data**: Tab-delimited world records with UWP, trade codes, extensions
- **Automatic Caching**: Respects API limits with local storage
- **Milieu Support**: Analyze different time periods (M1105, M1120, etc.)

### Economic Calculations

**Resource Units (RU) Formula:**
```
RU = Resources × Labor × Infrastructure × Efficiency_Multiplier
```

Where:
- `Resources`, `Labor`, `Infrastructure`: Extended hex digits from Economic Extension
- `Efficiency_Multiplier`: `(1 + E/10)` for positive E, `1/(1 + |E|/10)` for negative E
- Zero values converted to 1 to avoid null economics

**Population Estimates:**
```
Population = 10^(Population_Exponent)
```

**Starport Infrastructure Scoring:**
- A=4, B=3, C=2, D=1, E=0, X=-1

### Statistical Methods

- **Gini Coefficient**: Economic inequality measurement within sectors
- **Shannon Diversity**: Trade specialization diversity index
- **Z-Score Analysis**: Economic outlier identification
- **Regression Models**: Population vs. economic output relationships

## Output Files

### Core Results
- `all_imperium_worlds.csv`: Complete world database with calculated metrics
- `sector_statistics.csv`: Aggregated statistics by sector
- `summary_report.txt`: Executive summary of findings

### Rankings
- `ranking_by_total_ru.csv`: Sectors by total economic output
- `ranking_by_ru_per_capita.csv`: Sectors by economic efficiency
- `ranking_most_industrial.csv`: Industrial specialization leaders
- `ranking_most_agricultural.csv`: Agricultural specialization leaders

### Advanced Analysis
- `advanced_economic_indicators.csv`: Gini, diversity, development metrics
- `economic_clusters.csv`: High-value economic clusters
- `trade_routes_analysis.csv`: Inter-sector trade potential
- `economic_forecast.csv`: Growth projections with trade modifiers

### Visualizations
- `interactive_dashboard.html`: Comprehensive Plotly dashboard
- `sector_rankings.png`: Top performers across categories
- `economic_distributions.png`: Statistical distributions
- `sector_heatmap.png`: Comparative economic profiles
- `trade_analysis.png`: Trade pattern visualizations

## Configuration Options

### Command Line Arguments

```bash
python run_analysis.py --help

Options:
  --milieu M1105          # Time period (M1105, M1120, IW, etc.)
  --canon-tag Official    # Data quality filter
  --output-dir results    # Output directory
  --visualizations        # Generate charts and graphs  
  --advanced             # Run economic modeling
  --all                  # Complete analysis suite
  --request-delay 1.0    # API politeness delay
  --skip-cache           # Force fresh downloads
```

### Configuration File

Copy `config_example.py` to `config.py` and customize:

```python
class Config:
    MILIEU = "M1105"
    CANON_TAG = "Official"
    REQUEST_DELAY = 1.0
    
    # Economic thresholds
    DEVELOPMENT_THRESHOLDS = {
        "highly_developed": {"ru_per_capita": 50, "starport_score": 2.5},
        "developed": {"ru_per_capita": 20, "starport_score": 2.0},
        # ... etc
    }
```

## Example Analyses

### Regional Economic Powerhouses

Find the top economic sectors by total output:

```python
sector_stats = analyzer.calculate_sector_statistics()
top_sectors = sector_stats.nlargest(10, 'ResourceUnits_sum')
print(top_sectors[['Sector', 'ResourceUnits_sum', 'Name_count']])
```

### Economic Efficiency Leaders

Identify sectors with highest RU per capita:

```python
efficient_sectors = sector_stats.nlargest(10, 'RU_per_capita')
print(efficient_sectors[['Sector', 'RU_per_capita', 'StarportScore_mean']])
```

### Trade Specialization Analysis

Find heavily industrial vs. agricultural sectors:

```python
industrial = sector_stats[sector_stats['Pct_Industrial'] > 30]
agricultural = sector_stats[sector_stats['Pct_Agricultural'] > 40]
```

### Economic Outliers

Identify worlds with unusually high economic output:

```python
outliers = analyzer.find_economic_outliers(threshold=2.0)
print(outliers[['Name', 'Sector', 'ResourceUnits', 'RU_zscore']])
```

## Advanced Features

### Time Series Analysis

Compare economic evolution across milieux:

```bash
python run_analysis.py --milieu M1105 --output-dir results_1105
python run_analysis.py --milieu M1120 --output-dir results_1120
# Compare results across time periods
```

### Regional Comparisons

Focus analysis on specific regions:

```python
# Filter to Spinward Marches region
spinward_sectors = ["Spinward Marches", "Deneb", "Trojan Reach", "Reft"]
regional_data = worlds_df[worlds_df['Sector'].isin(spinward_sectors)]
```

### Custom Economic Models

Extend the analysis with custom trade multipliers:

```python
from advanced_analysis import AdvancedEconomicAnalyzer

analyzer = AdvancedEconomicAnalyzer()
analyzer.trade_multipliers['Ag']['Ri'] = 2.0  # Boost Ag-Rich trade
results = analyzer.generate_advanced_report(worlds_df, sector_stats, output_dir)
```

## Performance and Scaling

### API Etiquette
- Default 1-second delay between requests
- Automatic caching of sector data
- Respects Traveller Map API guidelines
- ~300 sectors complete in 5-10 minutes

### Memory Usage
- Processes 10,000+ worlds efficiently
- Pandas DataFrame optimization
- Optional data sampling for visualization

### Parallelization
- Concurrent sector downloads (when respectful)
- Vectorized pandas operations
- Optional multiprocessing for large analyses

## Dependencies

### Required
- `requests`: HTTP client for API access
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `tqdm`: Progress bars

### Optional (Full Features)
- `matplotlib`: Static plotting and charts
- `seaborn`: Statistical visualizations
- `plotly`: Interactive dashboards
- `scipy`: Advanced statistical functions

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run tests directly:

```bash
python tests/test_economic_analysis.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
pip install -e .[dev]  # Install in development mode with dev dependencies
black .                # Format code
isort .               # Sort imports
flake8 .              # Lint code
pytest                # Run tests
```

## Data Sources and Attribution

This project uses data from:
- **Traveller Map**: https://travellermap.com/ (Joshua Bell)
- **Official Traveller Universe**: Marc Miller, Far Future Enterprises
- **Sector Data**: Various contributors to the Traveller Map project

All Traveller material is used under Fair Use for analysis and research purposes. 
Traveller is a trademark of Far Future Enterprises.

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release with complete analysis pipeline
- API integration with automatic caching
- Basic and advanced economic indicators
- Comprehensive visualization suite
- Interactive dashboard generation
- Full test coverage

## Acknowledgments

- **Joshua Bell** for the excellent Traveller Map API
- **Marc Miller** for creating the Traveller universe
- **The Traveller Community** for maintaining sector data quality
- **Original Workflow Author** for the robust analysis framework

## Support

For questions, bug reports, or feature requests:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review example analyses in `examples/`

---

*"The Third Imperium: 11,000 worlds, countless stories, infinite economic possibilities."*