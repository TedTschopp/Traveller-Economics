"""
Advanced economic analysis tools for Traveller data
===================================================

Provides sophisticated economic modeling and analysis capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class EconomicIndicators:
    """Container for calculated economic indicators"""
    gini_coefficient: float
    economic_diversity_index: float
    trade_balance_score: float
    infrastructure_index: float
    development_classification: str

class AdvancedEconomicAnalyzer:
    """Advanced economic analysis and modeling"""
    
    def __init__(self):
        self.trade_multipliers = {
            'Ag': {'In': 1.5, 'Hi': 1.3, 'Ri': 1.2},  # Agricultural worlds trade well with these
            'In': {'Ag': 1.4, 'Ri': 1.6, 'Hi': 1.1},  # Industrial worlds
            'Ri': {'Ag': 1.2, 'In': 1.5, 'Hi': 1.3},  # Rich worlds
            'Hi': {'Ag': 1.3, 'In': 1.1, 'Ri': 1.2}   # High population worlds
        }
    
    def calculate_gini_coefficient(self, values: pd.Series) -> float:
        """Calculate Gini coefficient for economic inequality"""
        sorted_values = np.sort(values.dropna())
        n = len(sorted_values)
        
        if n == 0:
            return 0.0
        
        cumsum = np.cumsum(sorted_values)
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
    
    def calculate_diversity_index(self, worlds_df: pd.DataFrame) -> float:
        """Calculate economic diversity using Simpson's Diversity Index"""
        trade_codes = ['Ag', 'In', 'Ri', 'Hi', 'Po', 'Na', 'Va']
        
        total_worlds = len(worlds_df)
        if total_worlds == 0:
            return 0.0
        
        diversity = 0.0
        for code in trade_codes:
            proportion = worlds_df[f'Is{code}'].sum() / total_worlds
            if proportion > 0:
                diversity -= proportion * np.log(proportion)
        
        return diversity
    
    def calculate_trade_potential(self, sector_worlds: pd.DataFrame) -> Dict[str, float]:
        """Calculate trade potential within a sector"""
        trade_potential = {}
        
        for primary_code in ['Ag', 'In', 'Ri', 'Hi']:
            primary_worlds = sector_worlds[sector_worlds[f'Is{primary_code}'] == True]
            potential_score = 0.0
            
            for _, world in primary_worlds.iterrows():
                for secondary_code, multiplier in self.trade_multipliers.get(primary_code, {}).items():
                    partner_worlds = sector_worlds[sector_worlds[f'Is{secondary_code}'] == True]
                    if len(partner_worlds) > 0:
                        # Simple distance-based trade potential (assuming uniform distribution)
                        base_potential = world['ResourceUnits'] * len(partner_worlds)
                        potential_score += base_potential * multiplier
            
            trade_potential[primary_code] = potential_score
        
        return trade_potential
    
    def classify_economic_development(self, sector_stats: pd.Series) -> str:
        """Classify sector economic development level"""
        ru_per_capita = sector_stats.get('RU_per_capita', 0)
        starport_score = sector_stats.get('StarportScore_mean', 0)
        industrial_pct = sector_stats.get('Pct_Industrial', 0)
        
        # Development classification based on multiple factors
        if ru_per_capita > 50 and starport_score > 2.5 and industrial_pct > 30:
            return "Highly Developed"
        elif ru_per_capita > 20 and starport_score > 2.0 and industrial_pct > 15:
            return "Developed"
        elif ru_per_capita > 5 and starport_score > 1.5:
            return "Developing"
        elif ru_per_capita > 1:
            return "Emerging"
        else:
            return "Underdeveloped"
    
    def calculate_sector_indicators(self, worlds_df: pd.DataFrame, sector_stats: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced economic indicators for all sectors"""
        indicators_list = []
        
        for _, sector_row in sector_stats.iterrows():
            sector_name = sector_row['Sector']
            sector_worlds = worlds_df[worlds_df['Sector'] == sector_name]
            
            if len(sector_worlds) == 0:
                continue
            
            # Calculate indicators
            gini = self.calculate_gini_coefficient(sector_worlds['ResourceUnits'])
            diversity = self.calculate_diversity_index(sector_worlds)
            trade_potential = self.calculate_trade_potential(sector_worlds)
            development = self.classify_economic_development(sector_row)
            
            # Infrastructure index (combination of starport scores and world count)
            avg_starport = sector_worlds['StarportScore'].mean()
            world_count = len(sector_worlds)
            infrastructure = (avg_starport * np.log10(max(1, world_count))) / 5.0  # Normalized
            
            indicators_list.append({
                'Sector': sector_name,
                'Gini_Coefficient': gini,
                'Economic_Diversity': diversity,
                'Trade_Potential_Ag': trade_potential.get('Ag', 0),
                'Trade_Potential_In': trade_potential.get('In', 0),
                'Trade_Potential_Ri': trade_potential.get('Ri', 0),
                'Trade_Potential_Hi': trade_potential.get('Hi', 0),
                'Infrastructure_Index': infrastructure,
                'Development_Classification': development
            })
        
        return pd.DataFrame(indicators_list)
    
    def identify_economic_clusters(self, worlds_df: pd.DataFrame, min_ru: float = 100) -> pd.DataFrame:
        """Identify clusters of high economic activity"""
        high_value_worlds = worlds_df[worlds_df['ResourceUnits'] >= min_ru].copy()
        
        if len(high_value_worlds) == 0:
            return pd.DataFrame()
        
        # Group by sector and calculate cluster metrics
        clusters = high_value_worlds.groupby('Sector').agg({
            'Name': 'count',
            'ResourceUnits': ['sum', 'mean'],
            'Population': 'sum',
            'StarportScore': 'mean'
        }).round(2)
        
        clusters.columns = ['World_Count', 'Total_RU', 'Avg_RU', 'Total_Population', 'Avg_Starport']
        clusters = clusters.reset_index()
        
        # Calculate cluster density (worlds per unit economic output)
        clusters['Economic_Density'] = clusters['World_Count'] / clusters['Total_RU'] * 1000
        
        # Rank clusters
        clusters['Cluster_Rank'] = clusters['Total_RU'].rank(ascending=False)
        
        return clusters.sort_values('Total_RU', ascending=False)
    
    def calculate_economic_volatility(self, worlds_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate economic volatility metrics by sector"""
        volatility_metrics = {}
        
        for sector in worlds_df['Sector'].unique():
            sector_worlds = worlds_df[worlds_df['Sector'] == sector]
            
            if len(sector_worlds) < 2:
                volatility_metrics[sector] = 0.0
                continue
            
            # Calculate coefficient of variation for Resource Units
            ru_std = sector_worlds['ResourceUnits'].std()
            ru_mean = sector_worlds['ResourceUnits'].mean()
            
            if ru_mean > 0:
                volatility_metrics[sector] = ru_std / ru_mean
            else:
                volatility_metrics[sector] = 0.0
        
        return volatility_metrics
    
    def generate_economic_forecast(self, worlds_df: pd.DataFrame, growth_rate: float = 0.02) -> pd.DataFrame:
        """Generate simple economic growth forecast"""
        forecast_df = worlds_df.copy()
        
        # Apply growth rate with some variability based on world characteristics
        base_growth = np.random.normal(growth_rate, growth_rate * 0.3, len(forecast_df))
        
        # Adjust growth based on trade codes
        growth_modifiers = np.ones(len(forecast_df))
        growth_modifiers[forecast_df['IsIn']] *= 1.5  # Industrial worlds grow faster
        growth_modifiers[forecast_df['IsRi']] *= 1.3  # Rich worlds have stable growth
        growth_modifiers[forecast_df['IsPo']] *= 0.7  # Poor worlds grow slower
        growth_modifiers[forecast_df['IsAg']] *= 1.1  # Agricultural worlds moderate growth
        
        # Starport bonus
        starport_bonus = forecast_df['StarportScore'] * 0.1
        
        total_growth = base_growth * growth_modifiers + starport_bonus
        
        # Apply forecast
        forecast_df['Projected_RU'] = forecast_df['ResourceUnits'] * (1 + total_growth)
        forecast_df['Growth_Rate'] = total_growth
        
        return forecast_df
    
    def analyze_trade_routes(self, worlds_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze potential trade routes between sectors"""
        trade_routes = []
        
        sectors = worlds_df['Sector'].unique()
        
        for i, sector_a in enumerate(sectors):
            for sector_b in sectors[i+1:]:
                sector_a_worlds = worlds_df[worlds_df['Sector'] == sector_a]
                sector_b_worlds = worlds_df[worlds_df['Sector'] == sector_b]
                
                # Calculate complementary trade potential
                a_ag = sector_a_worlds['IsAg'].sum()
                a_in = sector_a_worlds['IsIn'].sum()
                b_ag = sector_b_worlds['IsAg'].sum()
                b_in = sector_b_worlds['IsIn'].sum()
                
                # Trade potential based on complementary resources
                ag_in_potential = (a_ag * b_in + b_ag * a_in) / 2
                
                total_ru_a = sector_a_worlds['ResourceUnits'].sum()
                total_ru_b = sector_b_worlds['ResourceUnits'].sum()
                
                # Economic mass for trade calculation
                economic_mass = np.sqrt(total_ru_a * total_ru_b)
                
                if economic_mass > 0:
                    trade_routes.append({
                        'Sector_A': sector_a,
                        'Sector_B': sector_b,
                        'Trade_Potential': ag_in_potential,
                        'Economic_Mass': economic_mass,
                        'Combined_RU': total_ru_a + total_ru_b,
                        'Trade_Score': ag_in_potential * np.log10(economic_mass + 1)
                    })
        
        trade_routes_df = pd.DataFrame(trade_routes)
        if not trade_routes_df.empty:
            trade_routes_df = trade_routes_df.sort_values('Trade_Score', ascending=False)
        
        return trade_routes_df
    
    def generate_advanced_report(self, worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, output_dir: Path):
        """Generate comprehensive advanced economic analysis report"""
        
        # Calculate advanced indicators
        indicators_df = self.calculate_sector_indicators(worlds_df, sector_stats)
        clusters_df = self.identify_economic_clusters(worlds_df)
        volatility_metrics = self.calculate_economic_volatility(worlds_df)
        forecast_df = self.generate_economic_forecast(worlds_df)
        trade_routes_df = self.analyze_trade_routes(worlds_df)
        
        # Save CSV files to output directory
        output_dir.mkdir(exist_ok=True)
        indicators_df.to_csv(output_dir / 'advanced_economic_indicators.csv', index=False)
        clusters_df.to_csv(output_dir / 'economic_clusters.csv', index=False)
        forecast_df.to_csv(output_dir / 'economic_forecast.csv', index=False)
        trade_routes_df.to_csv(output_dir / 'trade_routes_analysis.csv', index=False)
        
        # Save human-readable report to Analysis directory
        analysis_dir = Path("Analysis")
        analysis_dir.mkdir(exist_ok=True)
        
        # Generate advanced text report
        report = self._generate_advanced_text_report(
            worlds_df, sector_stats, indicators_df, clusters_df, 
            volatility_metrics, trade_routes_df
        )
        
        with open(analysis_dir / 'advanced_economic_report.txt', 'w') as f:
            f.write(report)
        
        logger.info("Advanced economic analysis complete")
        return {
            'indicators': indicators_df,
            'clusters': clusters_df,
            'volatility': volatility_metrics,
            'forecast': forecast_df,
            'trade_routes': trade_routes_df
        }
    
    def _generate_advanced_text_report(self, worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, 
                                     indicators_df: pd.DataFrame, clusters_df: pd.DataFrame,
                                     volatility_metrics: Dict, trade_routes_df: pd.DataFrame) -> str:
        """Generate detailed text report of advanced analysis"""
        
        report = f"""
ADVANCED THIRD IMPERIUM ECONOMIC ANALYSIS
=========================================

ECONOMIC INEQUALITY ANALYSIS
-----------------------------
"""
        
        if not indicators_df.empty:
            avg_gini = indicators_df['Gini_Coefficient'].mean()
            high_inequality = indicators_df[indicators_df['Gini_Coefficient'] > 0.4]
            
            report += f"""
Average Gini Coefficient: {avg_gini:.3f}
Sectors with High Inequality (>0.4): {len(high_inequality)}

Most Unequal Sectors:
"""
            for _, sector in high_inequality.nlargest(5, 'Gini_Coefficient').iterrows():
                report += f"  {sector['Sector']}: {sector['Gini_Coefficient']:.3f}\n"
        
        report += f"""

ECONOMIC DIVERSITY ANALYSIS
----------------------------
"""
        
        if not indicators_df.empty:
            avg_diversity = indicators_df['Economic_Diversity'].mean()
            diverse_sectors = indicators_df[indicators_df['Economic_Diversity'] > avg_diversity]
            
            report += f"""
Average Economic Diversity Index: {avg_diversity:.3f}
Above-Average Diverse Sectors: {len(diverse_sectors)}

Most Economically Diverse Sectors:
"""
            for _, sector in indicators_df.nlargest(5, 'Economic_Diversity').iterrows():
                report += f"  {sector['Sector']}: {sector['Economic_Diversity']:.3f}\n"
        
        report += f"""

DEVELOPMENT CLASSIFICATION
--------------------------
"""
        
        if not indicators_df.empty:
            dev_counts = indicators_df['Development_Classification'].value_counts()
            for dev_level, count in dev_counts.items():
                pct = (count / len(indicators_df)) * 100
                report += f"{dev_level}: {count} sectors ({pct:.1f}%)\n"
        
        report += f"""

ECONOMIC CLUSTERS ANALYSIS
---------------------------
"""
        
        if not clusters_df.empty:
            report += f"""
Total Economic Clusters Identified: {len(clusters_df)}

Top 10 Economic Clusters by Total Output:
"""
            for _, cluster in clusters_df.head(10).iterrows():
                report += f"  {cluster['Sector']}: {cluster['Total_RU']:,.0f} RU ({cluster['World_Count']} worlds)\n"
        
        report += f"""

TRADE ROUTE ANALYSIS
--------------------
"""
        
        if not trade_routes_df.empty:
            report += f"""
Potential Trade Routes Identified: {len(trade_routes_df)}

Top 10 Trade Routes by Potential:
"""
            for _, route in trade_routes_df.head(10).iterrows():
                report += f"  {route['Sector_A']} ↔ {route['Sector_B']}: Score {route['Trade_Score']:.0f}\n"
        
        report += f"""

ECONOMIC VOLATILITY
-------------------
"""
        
        if volatility_metrics:
            volatile_sectors = {k: v for k, v in volatility_metrics.items() if v > 1.0}
            stable_sectors = {k: v for k, v in volatility_metrics.items() if v < 0.3}
            
            report += f"""
High Volatility Sectors (CV > 1.0): {len(volatile_sectors)}
Stable Sectors (CV < 0.3): {len(stable_sectors)}

Most Volatile Sectors:
"""
            for sector, volatility in sorted(volatile_sectors.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"  {sector}: {volatility:.3f}\n"
        
        report += f"""

METHODOLOGY NOTES
-----------------
- Gini Coefficient: Measures economic inequality (0 = perfect equality, 1 = maximum inequality)
- Diversity Index: Shannon entropy measure of trade code distribution
- Trade Potential: Calculated based on complementary resource availability
- Economic Clusters: Sectors with worlds exceeding 100 RU threshold
- Volatility: Coefficient of variation in Resource Units within sectors

This analysis provides quantitative insights into Third Imperium economic
structure, trade opportunities, and development patterns using canonical
Traveller data from the Official Timeline.
"""
        
        return report

def run_advanced_analysis(worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, output_dir: str = "output"):
    """Convenience function to run all advanced analysis"""
    analyzer = AdvancedEconomicAnalyzer()
    output_path = Path(output_dir)
    return analyzer.generate_advanced_report(worlds_df, sector_stats, output_path)
