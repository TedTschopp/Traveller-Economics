"""
Traveller Third Imperium Economic Analysis
=========================================

A comprehensive toolkit for analyzing economic activity across the Third Imperium
using data from the Traveller Map API.

Author: Based on the robust workflow specification
Date: 2025-07-26
"""

import requests
import pandas as pd
import numpy as np
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import re
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EconomicConfig:
    """Configuration for economic analysis parameters"""
    milieu: str = "M1105"  # Default to 1105 Imperial era
    canon_tag: str = "Official"  # Only official data
    cache_dir: str = "cache"
    request_delay: float = 1.0  # Seconds between API requests (be polite)
    imperium_allegiance_prefix: str = "Im"

class TravellerMapAPI:
    """Interface to the Traveller Map API"""
    
    BASE_URL = "https://travellermap.com"
    
    def __init__(self, config: EconomicConfig):
        self.config = config
        self.session = requests.Session()
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_sectors(self) -> List[Dict]:
        """Get list of sectors with required data"""
        url = f"{self.BASE_URL}/api/universe"
        params = {
            "requireData": 1,
            "milieu": self.config.milieu,
            "tag": self.config.canon_tag
        }
        
        logger.info(f"Fetching sectors for milieu {self.config.milieu}")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        sectors = response_data.get('Sectors', [])
        logger.info(f"Found {len(sectors)} sectors")
        return sectors
    
    def get_sector_data(self, sector_name: str) -> Optional[str]:
        """Get tab-delimited world data for a sector"""
        cache_file = self.cache_dir / f"{sector_name}_{self.config.milieu}.tsv"
        
        # Check cache first
        if cache_file.exists():
            logger.debug(f"Loading {sector_name} from cache")
            return cache_file.read_text()
        
        url = f"{self.BASE_URL}/data/{sector_name}/tab"
        params = {"milieu": self.config.milieu}
        
        try:
            time.sleep(self.config.request_delay)  # Be polite to the API
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.text
            # Cache the data
            cache_file.write_text(data)
            logger.debug(f"Cached {sector_name} data")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data for {sector_name}: {e}")
            return None

class EconomicCalculator:
    """Calculate economic metrics from world data"""
    
    STARPORT_SCORES = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0, 'X': -1}
    
    @staticmethod
    def parse_uwp(uwp: str) -> Dict:
        """Parse Universal World Profile"""
        if len(uwp) < 7:
            return {"starport": "X", "population_exp": 0}
        
        return {
            "starport": uwp[0],
            "size": uwp[1],
            "atmosphere": uwp[2], 
            "hydrosphere": uwp[3],
            "population_exp": EconomicCalculator.ehex_to_decimal(uwp[4]),
            "government": uwp[5],
            "law_level": uwp[6]
        }
    
    @staticmethod
    def ehex_to_decimal(ehex_char: str) -> int:
        """Convert extended hex character to decimal"""
        if ehex_char.isdigit():
            return int(ehex_char)
        elif ehex_char.upper() in 'ABCDEFGHJKLMNPQRSTUVWXYZ':
            # Extended hex mapping
            mapping = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
            return mapping.index(ehex_char.upper())
        return 0
    
    @staticmethod
    def parse_economic_extension(ex: str) -> Dict:
        """Parse Economic Extension (R L I ±E)"""
        # Match pattern like (D7E+5) or (D7E-2)
        match = re.match(r'\(([0-9A-Z])([0-9A-Z])([0-9A-Z])([+-]?\d+)\)', ex)
        if not match:
            return {"resources": 1, "labor": 1, "infrastructure": 1, "efficiency": 0}
        
        r, l, i, e = match.groups()
        return {
            "resources": max(1, EconomicCalculator.ehex_to_decimal(r)),
            "labor": max(1, EconomicCalculator.ehex_to_decimal(l)),
            "infrastructure": max(1, EconomicCalculator.ehex_to_decimal(i)),
            "efficiency": int(e)  # Keep sign
        }
    
    @staticmethod
    def calculate_resource_units(economic_ext: Dict) -> float:
        """Calculate Resource Units (RU) from economic extension"""
        ru = (economic_ext["resources"] * 
              economic_ext["labor"] * 
              economic_ext["infrastructure"])
        
        # Apply efficiency modifier
        efficiency = economic_ext["efficiency"]
        if efficiency >= 0:
            ru *= (1 + efficiency / 10.0)
        else:
            ru *= (1 / (1 + abs(efficiency) / 10.0))
        
        return ru
    
    @staticmethod
    def parse_trade_codes(remarks: str) -> List[str]:
        """Extract trade codes from remarks field"""
        if pd.isna(remarks):
            return []
        return remarks.split()
    
    @staticmethod
    def calculate_population(pop_exp: int) -> int:
        """Calculate approximate population from exponent"""
        return 10 ** pop_exp

class WorldDataProcessor:
    """Process and enrich world data"""
    
    def __init__(self, config: EconomicConfig):
        self.config = config
        self.calculator = EconomicCalculator()
    
    def parse_sector_data(self, sector_name: str, data: str) -> pd.DataFrame:
        """Parse tab-delimited sector data into DataFrame"""
        if not data:
            return pd.DataFrame()
        
        lines = data.strip().split('\n')
        # Skip comment lines
        data_lines = [line for line in lines if not line.startswith('#')]
        
        if not data_lines:
            return pd.DataFrame()
        
        # Use the first non-comment line as headers
        headers = data_lines[0].split('\t')
        num_cols = len(headers)
        
        # Parse data rows, ensuring each has the same number of columns
        rows = []
        for line in data_lines[1:]:
            row = line.split('\t')
            # Pad row with empty strings if it's shorter than headers
            while len(row) < num_cols:
                row.append('')
            # Truncate if longer (shouldn't happen but be safe)
            row = row[:num_cols]
            rows.append(row)
        
        df = pd.DataFrame(rows, columns=headers)
        df['Sector'] = sector_name
        
        return df
    
    def enrich_world_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated economic metrics to world data"""
        if df.empty:
            return df
        
        # Filter to Imperium worlds only
        imperium_mask = df['Allegiance'].str.startswith(self.config.imperium_allegiance_prefix, na=False)
        df = df[imperium_mask].copy()
        
        if df.empty:
            return df
        
        # Parse UWP
        uwp_data = df['UWP'].apply(self.calculator.parse_uwp)
        df['Starport'] = [d['starport'] for d in uwp_data]
        df['PopulationExp'] = [d['population_exp'] for d in uwp_data]
        
        # Calculate population
        df['Population'] = df['PopulationExp'].apply(self.calculator.calculate_population)
        
        # Parse Economic Extension
        ex_data = df['(Ex)'].fillna('(000+0)').apply(self.calculator.parse_economic_extension)
        df['Resources'] = [d['resources'] for d in ex_data]
        df['Labor'] = [d['labor'] for d in ex_data]
        df['Infrastructure'] = [d['infrastructure'] for d in ex_data]
        df['Efficiency'] = [d['efficiency'] for d in ex_data]
        
        # Calculate Resource Units
        df['ResourceUnits'] = ex_data.apply(self.calculator.calculate_resource_units)
        
        # Parse trade codes
        df['TradeCodes'] = df['Remarks'].apply(self.calculator.parse_trade_codes)
        
        # Starport scores
        df['StarportScore'] = df['Starport'].map(self.calculator.STARPORT_SCORES).fillna(-1)
        
        # Trade code flags
        all_trade_codes = ['Ag', 'In', 'Ri', 'Hi', 'Po', 'Na', 'Va', 'De', 'Fl', 'Ic', 'Wa']
        for code in all_trade_codes:
            df[f'Is{code}'] = df['TradeCodes'].apply(lambda x: code in x)
        
        return df

class EconomicAnalyzer:
    """Analyze economic data and generate insights"""
    
    def __init__(self, config: EconomicConfig):
        self.config = config
        self.api = TravellerMapAPI(config)
        self.processor = WorldDataProcessor(config)
        self.all_worlds = pd.DataFrame()
    
    def collect_all_data(self) -> pd.DataFrame:
        """Collect and process data from all sectors"""
        sectors = self.api.get_sectors()
        all_worlds = []
        
        logger.info(f"Processing {len(sectors)} sectors...")
        
        for sector in tqdm(sectors, desc="Downloading sector data"):
            sector_name = sector['Names'][0]['Text']
            
            raw_data = self.api.get_sector_data(sector_name)
            if raw_data:
                sector_df = self.processor.parse_sector_data(sector_name, raw_data)
                if not sector_df.empty:
                    enriched_df = self.processor.enrich_world_data(sector_df)
                    if not enriched_df.empty:
                        all_worlds.append(enriched_df)
        
        if all_worlds:
            self.all_worlds = pd.concat(all_worlds, ignore_index=True)
            logger.info(f"Collected data for {len(self.all_worlds)} Imperium worlds")
        else:
            logger.warning("No world data collected")
            self.all_worlds = pd.DataFrame()
        
        return self.all_worlds
    
    def calculate_sector_statistics(self) -> pd.DataFrame:
        """Calculate aggregate statistics by sector"""
        if self.all_worlds.empty:
            return pd.DataFrame()
        
        # Basic aggregations
        sector_stats = self.all_worlds.groupby('Sector').agg({
            'Name': 'count',
            'ResourceUnits': ['sum', 'mean', 'median', 'std'],
            'Population': ['sum', 'mean'],
            'StarportScore': 'mean',
            'IsAg': 'sum',
            'IsIn': 'sum', 
            'IsRi': 'sum',
            'IsHi': 'sum',
            'IsPo': 'sum'
        }).round(2)
        
        # Flatten column names
        sector_stats.columns = ['_'.join(col).strip() for col in sector_stats.columns]
        
        # Calculate derived metrics
        sector_stats['RU_per_capita'] = (
            sector_stats['ResourceUnits_sum'] / sector_stats['Population_sum']
        ).fillna(0)
        
        sector_stats['Pct_Agricultural'] = (
            sector_stats['IsAg_sum'] / sector_stats['Name_count'] * 100
        ).fillna(0)
        
        sector_stats['Pct_Industrial'] = (
            sector_stats['IsIn_sum'] / sector_stats['Name_count'] * 100
        ).fillna(0)
        
        sector_stats['Pct_Rich'] = (
            sector_stats['IsRi_sum'] / sector_stats['Name_count'] * 100
        ).fillna(0)
        
        # Reset index to make Sector a column
        sector_stats = sector_stats.reset_index()
        
        return sector_stats
    
    def generate_rankings(self, sector_stats: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generate various ranking tables"""
        rankings = {}
        
        if sector_stats.empty:
            return rankings
        
        # Top sectors by total RU
        rankings['by_total_ru'] = sector_stats.nlargest(20, 'ResourceUnits_sum')[
            ['Sector', 'ResourceUnits_sum', 'Name_count', 'Population_sum']
        ]
        
        # Top sectors by RU per capita
        rankings['by_ru_per_capita'] = sector_stats.nlargest(20, 'RU_per_capita')[
            ['Sector', 'RU_per_capita', 'ResourceUnits_sum', 'Population_sum']
        ]
        
        # Most industrial sectors
        rankings['most_industrial'] = sector_stats.nlargest(20, 'Pct_Industrial')[
            ['Sector', 'Pct_Industrial', 'IsIn_sum', 'Name_count']
        ]
        
        # Most agricultural sectors
        rankings['most_agricultural'] = sector_stats.nlargest(20, 'Pct_Agricultural')[
            ['Sector', 'Pct_Agricultural', 'IsAg_sum', 'Name_count']
        ]
        
        # Best starport infrastructure
        rankings['best_starports'] = sector_stats.nlargest(20, 'StarportScore_mean')[
            ['Sector', 'StarportScore_mean', 'Name_count']
        ]
        
        return rankings
    
    def find_economic_outliers(self, threshold: float = 2.0) -> pd.DataFrame:
        """Find worlds with unusually high economic output"""
        if self.all_worlds.empty:
            return pd.DataFrame()
        
        # Calculate z-scores for ResourceUnits within each sector
        self.all_worlds['RU_zscore'] = (
            self.all_worlds.groupby('Sector')['ResourceUnits']
            .transform(lambda x: (x - x.mean()) / x.std())
        )
        
        outliers = self.all_worlds[
            self.all_worlds['RU_zscore'] > threshold
        ][['Name', 'Sector', 'Hex', 'ResourceUnits', 'RU_zscore', 'Population', 'TradeCodes']]
        
        return outliers.sort_values('RU_zscore', ascending=False)
    
    def save_results(self, output_dir: str = "output"):
        """Save all analysis results"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save raw world data
        if not self.all_worlds.empty:
            self.all_worlds.to_csv(output_path / "all_imperium_worlds.csv", index=False)
        
        # Calculate and save sector statistics
        sector_stats = self.calculate_sector_statistics()
        if not sector_stats.empty:
            sector_stats.to_csv(output_path / "sector_statistics.csv", index=False)
        
        # Generate and save rankings
        rankings = self.generate_rankings(sector_stats)
        for name, ranking_df in rankings.items():
            ranking_df.to_csv(output_path / f"ranking_{name}.csv", index=False)
        
        # Find and save outliers
        outliers = self.find_economic_outliers()
        if not outliers.empty:
            outliers.to_csv(output_path / "economic_outliers.csv", index=False)
        
        # Save summary statistics
        summary = self.generate_summary_report(sector_stats)
        with open(output_path / "summary_report.txt", 'w') as f:
            f.write(summary)
        
        logger.info(f"Results saved to {output_path}")
        return output_path
    
    def generate_summary_report(self, sector_stats: pd.DataFrame) -> str:
        """Generate a text summary of the analysis"""
        if self.all_worlds.empty or sector_stats.empty:
            return "No data available for summary."
        
        total_worlds = len(self.all_worlds)
        total_sectors = len(sector_stats)
        total_population = self.all_worlds['Population'].sum()
        total_ru = self.all_worlds['ResourceUnits'].sum()
        avg_ru_per_capita = total_ru / total_population if total_population > 0 else 0
        
        # Top performers
        top_ru_sector = sector_stats.loc[sector_stats['ResourceUnits_sum'].idxmax(), 'Sector']
        top_ru_per_capita_sector = sector_stats.loc[sector_stats['RU_per_capita'].idxmax(), 'Sector']
        
        report = f"""
Third Imperium Economic Analysis Summary
========================================
Milieu: {self.config.milieu}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Imperium Worlds: {total_worlds:,}
Total Sectors: {total_sectors}
Total Population: {total_population:,}
Total Resource Units: {total_ru:,.0f}
Average RU per Capita: {avg_ru_per_capita:.2f}

TOP PERFORMERS
--------------
Highest Total Economic Output: {top_ru_sector}
Highest RU per Capita: {top_ru_per_capita_sector}

TRADE BREAKDOWN
---------------
Agricultural Worlds: {self.all_worlds['IsAg'].sum():,} ({self.all_worlds['IsAg'].mean()*100:.1f}%)
Industrial Worlds: {self.all_worlds['IsIn'].sum():,} ({self.all_worlds['IsIn'].mean()*100:.1f}%)
Rich Worlds: {self.all_worlds['IsRi'].sum():,} ({self.all_worlds['IsRi'].mean()*100:.1f}%)
High Population Worlds: {self.all_worlds['IsHi'].sum():,} ({self.all_worlds['IsHi'].mean()*100:.1f}%)
Poor Worlds: {self.all_worlds['IsPo'].sum():,} ({self.all_worlds['IsPo'].mean()*100:.1f}%)

STARPORT INFRASTRUCTURE
-----------------------
Class A Starports: {(self.all_worlds['Starport'] == 'A').sum():,}
Class B Starports: {(self.all_worlds['Starport'] == 'B').sum():,}
Class C Starports: {(self.all_worlds['Starport'] == 'C').sum():,}
Average Starport Score: {self.all_worlds['StarportScore'].mean():.2f}

This analysis uses official Traveller Map API data to provide
quantitative insights into Third Imperium economic activity.
"""
        return report

def main():
    """Main execution function"""
    # Configure the analysis
    config = EconomicConfig(
        milieu="M1105",
        canon_tag="Official",
        cache_dir="cache",
        request_delay=1.0
    )
    
    # Create analyzer and run analysis
    analyzer = EconomicAnalyzer(config)
    
    logger.info("Starting Third Imperium Economic Analysis")
    
    # Collect all data
    worlds_df = analyzer.collect_all_data()
    
    if worlds_df.empty:
        logger.error("No data collected. Check your configuration and network connection.")
        return
    
    # Save results
    output_path = analyzer.save_results()
    
    # Print summary
    sector_stats = analyzer.calculate_sector_statistics()
    summary = analyzer.generate_summary_report(sector_stats)
    print(summary)
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()
