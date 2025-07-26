#!/usr/bin/env python3
"""
Economic analysis for ALL political factions in the Traveller universe
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
from traveller_economics import TravellerMapAPI, EconomicCalculator, EconomicConfig
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AllFactionsAnalyzer:
    """Enhanced analyzer for all political factions"""
    
    def __init__(self, config: EconomicConfig = None, output_dir: str = "output"):
        self.config = config or EconomicConfig()
        self.api = TravellerMapAPI(self.config)
        self.calculator = EconomicCalculator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def collect_all_faction_data(self) -> pd.DataFrame:
        """Collect data for ALL worlds regardless of allegiance"""
        logger.info("Collecting data for ALL political factions")
        
        # Get all sectors
        sectors = self.api.get_sectors()
        logger.info(f"Found {len(sectors)} sectors total")
        
        all_worlds = []
        
        for sector in tqdm(sectors, desc="Processing all sectors"):
            try:
                sector_name = sector['Names'][0]['Text']
                
                # Get sector data
                sector_data = self.api.get_sector_data(sector_name)
                if sector_data is None:
                    continue
                
                # Parse without filtering by allegiance
                worlds = self.parse_sector_data_all_factions(sector_data, sector_name)
                all_worlds.extend(worlds)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing sector {sector.get('Names', [{'Text': 'Unknown'}])[0]['Text']}: {e}")
                continue
        
        if not all_worlds:
            raise ValueError("No world data collected")
        
        df = pd.DataFrame(all_worlds)
        logger.info(f"Collected {len(df)} worlds from all factions")
        
        # Calculate economic metrics
        df = self.calculate_all_metrics(df)
        
        return df
    
    def parse_sector_data_all_factions(self, sector_data: str, sector_name: str) -> List[Dict]:
        """Parse sector data for ALL worlds, not just Imperial"""
        worlds = []
        lines = sector_data.strip().split('\n')
        
        # Skip comment lines
        data_lines = [line for line in lines if not line.startswith('#')]
        
        if not data_lines:
            return worlds
        
        # Use the first non-comment line as headers
        headers = data_lines[0].split('\t')
        num_cols = len(headers)
        
        for line in data_lines[1:]:
            try:
                row = line.split('\t')
                # Pad row with empty strings if it's shorter than headers
                while len(row) < num_cols:
                    row.append('')
                # Truncate if longer
                row = row[:num_cols]
                
                world_data = dict(zip(headers, row))
                
                # Extract key fields
                name = world_data.get('Name', '').strip()
                uwp = world_data.get('UWP', '').strip()
                allegiance = world_data.get('Allegiance', '').strip()
                
                if not name or not uwp or len(uwp) < 7:
                    continue
                
                # Store essential data
                world = {
                    'Name': name,
                    'Sector': sector_name,
                    'Hex': world_data.get('Hex', '').strip(),
                    'UWP': uwp,
                    'Allegiance': allegiance,
                    'Bases': world_data.get('Bases', '').strip(),
                    'Remarks': world_data.get('Remarks', '').strip(),
                    'Zone': world_data.get('Zone', '').strip(),
                    'PBG': world_data.get('PBG', '').strip(),
                    'Economic_Extension': world_data.get('(Ex)', '').strip(),
                    'Allegiance_Name': self.get_allegiance_name(allegiance),
                    'Faction_Type': self.classify_faction_type(allegiance)
                }
                
                worlds.append(world)
                
            except Exception as e:
                logger.debug(f"Error parsing line in {sector_name}: {e}")
                continue
        
        return worlds
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate economic metrics for all worlds"""
        # Parse UWP
        uwp_data = df['UWP'].apply(self.calculator.parse_uwp)
        df['Starport'] = [d['starport'] for d in uwp_data]
        df['PopulationExp'] = [d['population_exp'] for d in uwp_data]
        
        # Calculate population
        df['Population'] = df['PopulationExp'].apply(self.calculator.calculate_population)
        
        # Parse Economic Extension
        ex_data = df['Economic_Extension'].fillna('(000+0)').apply(self.calculator.parse_economic_extension)
        df['Resources'] = [d['resources'] for d in ex_data]
        df['Labor'] = [d['labor'] for d in ex_data]
        df['Infrastructure'] = [d['infrastructure'] for d in ex_data]
        df['Efficiency'] = [d['efficiency'] for d in ex_data]
        
        # Calculate Resource Units
        df['ResourceUnits'] = ex_data.apply(self.calculator.calculate_resource_units)
        
        # Parse trade codes
        df['TradeCodes'] = df['Remarks'].apply(self.calculator.parse_trade_codes)
        
        # Trade classifications
        df['IsAg'] = df['TradeCodes'].apply(lambda codes: 1 if 'Ag' in codes else 0)
        df['IsIn'] = df['TradeCodes'].apply(lambda codes: 1 if 'In' in codes else 0)
        df['IsRi'] = df['TradeCodes'].apply(lambda codes: 1 if 'Ri' in codes else 0)
        df['IsHi'] = df['TradeCodes'].apply(lambda codes: 1 if 'Hi' in codes else 0)
        df['IsPo'] = df['TradeCodes'].apply(lambda codes: 1 if 'Po' in codes else 0)
        
        # Starport scoring
        starport_scores = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0, 'X': 0}
        df['StarportScore'] = df['Starport'].map(starport_scores).fillna(0)
        
        return df
    
    def get_allegiance_name(self, code: str) -> str:
        """Convert allegiance code to readable name"""
        allegiance_map = {
            # Third Imperium
            'ImAp': 'Third Imperium (Amec Protectorate)',
            'ImDc': 'Third Imperium (Domain of Col)',
            'ImDd': 'Third Imperium (Domain of Deneb)',
            'ImDg': 'Third Imperium (Domain of Gateway)',
            'ImDi': 'Third Imperium (Domain of Ilelish)',
            'ImDs': 'Third Imperium (Domain of Sol)',
            'ImDv': 'Third Imperium (Domain of Vland)',
            'ImLa': 'Third Imperium (League of Antares)',
            'ImLc': 'Third Imperium (Lancian Cultural Region)',
            'ImLu': 'Third Imperium (Luriani Cultural Association)',
            'ImSy': 'Third Imperium (Sylean Federation)',
            'ImVd': 'Third Imperium (Vilani Cultural Association)',
            
            # Aslan Hierate
            'As': 'Aslan Hierate',
            'AsIf': 'Aslan Hierate (Ifrit Lodge)',
            'AsMw': 'Aslan Hierate (Mewar Lodge)',
            'AsOf': 'Aslan Hierate (Ofa Lodge)',
            'AsSc': 'Aslan Hierate (Seieakh Lodge)',
            'AsSF': 'Aslan Hierate (Seieakh Foundation)',
            'AsT0': 'Aslan Hierate (Tuay Lodge)',
            'AsTA': 'Aslan Hierate (Tuay Alliance)',
            'AsTv': 'Aslan Hierate (Tuay Vacacy)',
            'AsVc': 'Aslan Hierate (Vcler Lodge)',
            'AsWc': 'Aslan Hierate (Wahtoi Lodge)',
            'AsXX': 'Aslan Hierate (Unknown Lodge)',
            
            # Zhodani Consulate
            'Zh': 'Zhodani Consulate',
            'ZhCA': 'Zhodani Consulate (Central Authority)',
            'ZhCo': 'Zhodani Consulate (Core Territories)',
            'ZhIN': 'Zhodani Consulate (Inner Territories)',
            'ZhOu': 'Zhodani Consulate (Outer Territories)',
            
            # Vargr Extents
            'Va': 'Vargr Extents',
            'VaEx': 'Vargr Extents',
            'VAsP': 'Vargr (Pact of Gaerr)',
            'VaDm': 'Vargr (Daemon Coalition)',
            'VaFd': 'Vargr (Federation of Gakish)',
            'VaGr': 'Vargr (Granicus Domain)',
            'VaKo': 'Vargr (Korsumug Empire)',
            'VaLi': 'Vargr (Ling Standard Products)',
            'VaPa': 'Vargr (Pact of Gaerr)',
            'VaSP': 'Vargr (Salinaikoer Pack)',
            'VaTr': 'Vargr (Various Coalition)',
            'VaVa': 'Vargr (Various)',
            
            # Solomani Confederation
            'SoCf': 'Solomani Confederation',
            'SoNS': 'Solomani (Non-Aligned Systems)',
            'SoRD': 'Solomani (Reformed Doothan Stellar Dominion)',
            'SoTA': 'Solomani (Terran Accord)',
            'SoWu': 'Solomani (Wuan Technology Association)',
            
            # K'kree Two Thousand Worlds
            'Kk': 'K\'kree Two Thousand Worlds',
            
            # Hiver Federation
            'Hi': 'Hiver Federation',
            'HiFd': 'Hiver Federation',
            
            # Others
            'Cs': 'Client State',
            'CsIm': 'Client State (Imperial)',
            'CsMP': 'Client State (Mercantile Protectorate)',
            'CsZh': 'Client State (Zhodani)',
            'Dr': 'Droyne',
            'Na': 'Non-Aligned',
            'NaHu': 'Non-Aligned (Human)',
            'NaXX': 'Non-Aligned (Unknown)',
            'Xx': 'Unknown',
        }
        
        return allegiance_map.get(code, f'Unknown ({code})')
    
    def classify_faction_type(self, code: str) -> str:
        """Classify faction into major categories"""
        if code.startswith('Im'):
            return 'Third Imperium'
        elif code.startswith('As'):
            return 'Aslan Hierate'
        elif code.startswith('Zh'):
            return 'Zhodani Consulate'
        elif code.startswith('Va'):
            return 'Vargr Extents'
        elif code.startswith('So'):
            return 'Solomani Confederation'
        elif code.startswith('Kk'):
            return 'K\'kree Two Thousand Worlds'
        elif code.startswith('Hi'):
            return 'Hiver Federation'
        elif code.startswith('Cs'):
            return 'Client States'
        elif code in ['Dr']:
            return 'Droyne'
        elif code.startswith('Na') or code == '':
            return 'Non-Aligned'
        else:
            return 'Other/Unknown'
    
    def analyze_by_faction(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create faction-level statistics"""
        logger.info("Calculating faction-level statistics")
        
        faction_stats = df.groupby(['Faction_Type', 'Allegiance', 'Allegiance_Name']).agg({
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
        faction_stats.columns = ['_'.join(col).strip() for col in faction_stats.columns.values]
        faction_stats = faction_stats.reset_index()
        
        # Calculate percentages and per capita metrics
        faction_stats['RU_per_capita'] = (faction_stats['ResourceUnits_sum'] / 
                                        faction_stats['Population_sum']).fillna(0)
        faction_stats['Pct_Agricultural'] = (faction_stats['IsAg_sum'] / 
                                           faction_stats['Name_count'] * 100).round(1)
        faction_stats['Pct_Industrial'] = (faction_stats['IsIn_sum'] / 
                                         faction_stats['Name_count'] * 100).round(1)
        faction_stats['Pct_Rich'] = (faction_stats['IsRi_sum'] / 
                                   faction_stats['Name_count'] * 100).round(1)
        
        # Rename columns for clarity
        rename_map = {
            'Name_count': 'Total_Worlds',
            'ResourceUnits_sum': 'Total_RU',
            'ResourceUnits_mean': 'Mean_RU',
            'ResourceUnits_median': 'Median_RU',
            'ResourceUnits_std': 'StdDev_RU',
            'Population_sum': 'Total_Population',
            'Population_mean': 'Mean_Population',
            'StarportScore_mean': 'Mean_Starport_Score',
            'IsAg_sum': 'Agricultural_Worlds',
            'IsIn_sum': 'Industrial_Worlds',
            'IsRi_sum': 'Rich_Worlds',
            'IsHi_sum': 'High_Pop_Worlds',
            'IsPo_sum': 'Poor_Worlds'
        }
        faction_stats = faction_stats.rename(columns=rename_map)
        
        # Sort by total RU descending
        faction_stats = faction_stats.sort_values('Total_RU', ascending=False)
        
        return faction_stats
    
    def analyze_by_major_faction(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create major faction summary (rolled up)"""
        logger.info("Calculating major faction summaries")
        
        major_faction_stats = df.groupby('Faction_Type').agg({
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
        major_faction_stats.columns = ['_'.join(col).strip() for col in major_faction_stats.columns.values]
        major_faction_stats = major_faction_stats.reset_index()
        
        # Calculate derived metrics
        major_faction_stats['RU_per_capita'] = (major_faction_stats['ResourceUnits_sum'] / 
                                              major_faction_stats['Population_sum']).fillna(0)
        major_faction_stats['Pct_Agricultural'] = (major_faction_stats['IsAg_sum'] / 
                                                 major_faction_stats['Name_count'] * 100).round(1)
        major_faction_stats['Pct_Industrial'] = (major_faction_stats['IsIn_sum'] / 
                                               major_faction_stats['Name_count'] * 100).round(1)
        major_faction_stats['Pct_Rich'] = (major_faction_stats['IsRi_sum'] / 
                                         major_faction_stats['Name_count'] * 100).round(1)
        
        # Rename columns
        rename_map = {
            'Name_count': 'Total_Worlds',
            'ResourceUnits_sum': 'Total_RU', 
            'ResourceUnits_mean': 'Mean_RU',
            'ResourceUnits_median': 'Median_RU',
            'ResourceUnits_std': 'StdDev_RU',
            'Population_sum': 'Total_Population',
            'Population_mean': 'Mean_Population',
            'StarportScore_mean': 'Mean_Starport_Score',
            'IsAg_sum': 'Agricultural_Worlds',
            'IsIn_sum': 'Industrial_Worlds',
            'IsRi_sum': 'Rich_Worlds',
            'IsHi_sum': 'High_Pop_Worlds',
            'IsPo_sum': 'Poor_Worlds'
        }
        major_faction_stats = major_faction_stats.rename(columns=rename_map)
        
        # Sort by total RU descending
        major_faction_stats = major_faction_stats.sort_values('Total_RU', ascending=False)
        
        return major_faction_stats
    
    def run_all_factions_analysis(self):
        """Run complete analysis for all political factions"""
        logger.info("Starting All Factions Economic Analysis")
        logger.info(f"Configuration: Milieu={self.config.milieu}, Canon={self.config.canon_tag}")
        
        try:
            # Phase 1: Data Collection
            logger.info("Phase 1: Collecting all faction data")
            all_worlds_df = self.collect_all_faction_data()
            
            # Save complete world dataset
            all_worlds_path = self.output_dir / "all_factions_worlds.csv"
            all_worlds_df.to_csv(all_worlds_path, index=False)
            logger.info(f"Saved {len(all_worlds_df)} worlds to {all_worlds_path}")
            
            # Phase 2: Faction Analysis
            logger.info("Phase 2: Faction-level analysis")
            faction_stats = self.analyze_by_faction(all_worlds_df)
            major_faction_stats = self.analyze_by_major_faction(all_worlds_df)
            
            # Save faction statistics
            faction_stats_path = self.output_dir / "faction_statistics.csv"
            faction_stats.to_csv(faction_stats_path, index=False)
            logger.info(f"Saved faction statistics to {faction_stats_path}")
            
            major_faction_stats_path = self.output_dir / "major_faction_statistics.csv"
            major_faction_stats.to_csv(major_faction_stats_path, index=False)
            logger.info(f"Saved major faction statistics to {major_faction_stats_path}")
            
            # Phase 3: Summary Report
            self.generate_all_factions_report(all_worlds_df, faction_stats, major_faction_stats)
            
            logger.info("All Factions Analysis completed successfully!")
            
            return {
                'total_worlds': len(all_worlds_df),
                'total_factions': len(faction_stats),
                'major_factions': len(major_faction_stats)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def generate_all_factions_report(self, worlds_df: pd.DataFrame, 
                                   faction_stats: pd.DataFrame, 
                                   major_faction_stats: pd.DataFrame):
        """Generate comprehensive report for all factions"""
        report_path = self.output_dir / "all_factions_summary.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("TRAVELLER UNIVERSE: ALL FACTIONS ECONOMIC ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Milieu: {self.config.milieu}\n")
            f.write(f"Canon Level: {self.config.canon_tag}\n\n")
            
            # Overall Statistics
            total_worlds = len(worlds_df)
            total_population = worlds_df['Population'].sum()
            total_ru = worlds_df['ResourceUnits'].sum()
            num_factions = faction_stats['Allegiance'].nunique()
            num_major_factions = major_faction_stats['Faction_Type'].nunique()
            
            f.write("UNIVERSE OVERVIEW\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Worlds Analyzed: {total_worlds:,}\n")
            f.write(f"Total Population: {total_population:,.0f} beings\n") 
            f.write(f"Total Economic Output: {total_ru:,.0f} Resource Units\n")
            f.write(f"Political Entities: {num_factions} specific allegiances\n")
            f.write(f"Major Factions: {num_major_factions} categories\n\n")
            
            # Major Faction Rankings
            f.write("MAJOR FACTION RANKINGS\n")
            f.write("-" * 40 + "\n")
            f.write("Rank | Faction                    | Worlds | Total RU  | RU/Capita    | Population\n")
            f.write("-" * 85 + "\n")
            
            for i, (_, row) in enumerate(major_faction_stats.head(10).iterrows()):
                ru_per_capita = f"{row['RU_per_capita']:.8f}"
                f.write(f"{i+1:4d} | {row['Faction_Type']:<26} | {row['Total_Worlds']:6d} | "
                       f"{row['Total_RU']:9,.0f} | {ru_per_capita:>12} | "
                       f"{row['Total_Population']:11,.0f}\n")
            
            f.write("\n")
            
            # Top Individual Political Entities  
            f.write("TOP POLITICAL ENTITIES (by Total Economic Output)\n")
            f.write("-" * 60 + "\n")
            f.write("Rank | Entity                                         | Worlds | Total RU\n")
            f.write("-" * 80 + "\n")
            
            for i, (_, row) in enumerate(faction_stats.head(15).iterrows()):
                entity_name = row['Allegiance_Name'][:45] + "..." if len(row['Allegiance_Name']) > 45 else row['Allegiance_Name']
                f.write(f"{i+1:4d} | {entity_name:<46} | {row['Total_Worlds']:6d} | {row['Total_RU']:9,.0f}\n")
            
            f.write("\n")
            
            # Economic Efficiency Rankings
            f.write("MOST ECONOMICALLY EFFICIENT FACTIONS (RU per Capita)\n")
            f.write("-" * 60 + "\n")
            f.write("Rank | Faction                    | RU/Capita    | Worlds | Mean RU\n")
            f.write("-" * 75 + "\n")
            
            efficient_factions = major_faction_stats.sort_values('RU_per_capita', ascending=False)
            for i, (_, row) in enumerate(efficient_factions.head(10).iterrows()):
                ru_per_capita = f"{row['RU_per_capita']:.8f}"
                f.write(f"{i+1:4d} | {row['Faction_Type']:<26} | {ru_per_capita:>12} | "
                       f"{row['Total_Worlds']:6d} | {row['Mean_RU']:7.0f}\n")
            
            f.write("\n")
            
            # Specialization Analysis
            f.write("FACTION SPECIALIZATION ANALYSIS\n")
            f.write("-" * 40 + "\n")
            f.write("Faction                     | %Ag  | %In  | %Ri  | %Hi  | %Po\n")
            f.write("-" * 65 + "\n")
            
            for _, row in major_faction_stats.iterrows():
                f.write(f"{row['Faction_Type']:<27} | {row['Pct_Agricultural']:4.1f} | "
                       f"{row['Pct_Industrial']:4.1f} | {row['Pct_Rich']:4.1f} | "
                       f"{row['Pct_Agricultural']:4.1f} | {row['Pct_Industrial']:4.1f}\n")
        
        logger.info(f"Generated comprehensive report: {report_path}")

def main():
    """Run all factions analysis"""
    config = EconomicConfig(
        milieu="M1105",
        canon_tag="Official"
    )
    
    analyzer = AllFactionsAnalyzer(config, output_dir="output")
    return analyzer.run_all_factions_analysis()

if __name__ == "__main__":
    results = main()
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Total worlds processed: {results['total_worlds']:,}")
    print(f"Political entities: {results['total_factions']:,}")
    print(f"Major factions: {results['major_factions']:,}")
