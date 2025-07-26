"""
Visualization module for Traveller Economic Analysis
===================================================

Creates charts, maps, and visualizations of Third Imperium economic data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EconomicVisualizer:
    """Create visualizations of economic data"""
    
    def __init__(self, style: str = "seaborn-v0_8"):
        """Initialize visualizer with plotting style"""
        plt.style.use(style)
        sns.set_palette("husl")
        self.colors = px.colors.qualitative.Set3
    
    def plot_sector_rankings(self, sector_stats: pd.DataFrame, output_dir: Path):
        """Create ranking visualizations"""
        if sector_stats.empty:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Third Imperium Sector Economic Rankings', fontsize=16, fontweight='bold')
        
        # Top 15 sectors by total RU
        top_ru = sector_stats.nlargest(15, 'ResourceUnits_sum')
        axes[0,0].barh(range(len(top_ru)), top_ru['ResourceUnits_sum'])
        axes[0,0].set_yticks(range(len(top_ru)))
        axes[0,0].set_yticklabels(top_ru['Sector'], fontsize=8)
        axes[0,0].set_xlabel('Total Resource Units')
        axes[0,0].set_title('Top Sectors by Total Economic Output')
        axes[0,0].invert_yaxis()
        
        # Top 15 sectors by RU per capita
        top_ru_pc = sector_stats.nlargest(15, 'RU_per_capita')
        axes[0,1].barh(range(len(top_ru_pc)), top_ru_pc['RU_per_capita'])
        axes[0,1].set_yticks(range(len(top_ru_pc)))
        axes[0,1].set_yticklabels(top_ru_pc['Sector'], fontsize=8)
        axes[0,1].set_xlabel('Resource Units per Capita')
        axes[0,1].set_title('Top Sectors by Economic Efficiency')
        axes[0,1].invert_yaxis()
        
        # Most industrial sectors
        top_industrial = sector_stats.nlargest(15, 'Pct_Industrial')
        axes[1,0].barh(range(len(top_industrial)), top_industrial['Pct_Industrial'])
        axes[1,0].set_yticks(range(len(top_industrial)))
        axes[1,0].set_yticklabels(top_industrial['Sector'], fontsize=8)
        axes[1,0].set_xlabel('% Industrial Worlds')
        axes[1,0].set_title('Most Industrialized Sectors')
        axes[1,0].invert_yaxis()
        
        # Most agricultural sectors
        top_ag = sector_stats.nlargest(15, 'Pct_Agricultural')
        axes[1,1].barh(range(len(top_ag)), top_ag['Pct_Agricultural'])
        axes[1,1].set_yticks(range(len(top_ag)))
        axes[1,1].set_yticklabels(top_ag['Sector'], fontsize=8)
        axes[1,1].set_xlabel('% Agricultural Worlds')
        axes[1,1].set_title('Most Agricultural Sectors')
        axes[1,1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(output_dir / 'sector_rankings.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_economic_distributions(self, worlds_df: pd.DataFrame, output_dir: Path):
        """Plot distributions of economic metrics"""
        if worlds_df.empty:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Third Imperium Economic Distributions', fontsize=16, fontweight='bold')
        
        # Resource Units distribution (log scale)
        ru_data = worlds_df[worlds_df['ResourceUnits'] > 0]['ResourceUnits']
        axes[0,0].hist(np.log10(ru_data), bins=50, alpha=0.7, color='skyblue')
        axes[0,0].set_xlabel('Log10(Resource Units)')
        axes[0,0].set_ylabel('Number of Worlds')
        axes[0,0].set_title('Resource Units Distribution')
        
        # Population distribution (log scale)
        pop_data = worlds_df[worlds_df['Population'] > 0]['Population']
        axes[0,1].hist(np.log10(pop_data), bins=50, alpha=0.7, color='lightcoral')
        axes[0,1].set_xlabel('Log10(Population)')
        axes[0,1].set_ylabel('Number of Worlds')
        axes[0,1].set_title('Population Distribution')
        
        # Starport distribution
        starport_counts = worlds_df['Starport'].value_counts().sort_index()
        axes[0,2].bar(starport_counts.index, starport_counts.values, alpha=0.7, color='lightgreen')
        axes[0,2].set_xlabel('Starport Class')
        axes[0,2].set_ylabel('Number of Worlds')
        axes[0,2].set_title('Starport Distribution')
        
        # Trade code distribution
        trade_codes = ['Ag', 'In', 'Ri', 'Hi', 'Po', 'Na']
        trade_counts = [worlds_df[f'Is{code}'].sum() for code in trade_codes]
        axes[1,0].bar(trade_codes, trade_counts, alpha=0.7, color='gold')
        axes[1,0].set_xlabel('Trade Code')
        axes[1,0].set_ylabel('Number of Worlds')
        axes[1,0].set_title('Trade Code Distribution')
        plt.setp(axes[1,0].xaxis.get_majorticklabels(), rotation=45)
        
        # RU vs Population scatter (sample for performance)
        sample_size = min(5000, len(worlds_df))
        sample_df = worlds_df.sample(n=sample_size)
        sample_df = sample_df[(sample_df['ResourceUnits'] > 0) & (sample_df['Population'] > 0)]
        
        axes[1,1].scatter(np.log10(sample_df['Population']), 
                         np.log10(sample_df['ResourceUnits']), 
                         alpha=0.5, s=10)
        axes[1,1].set_xlabel('Log10(Population)')
        axes[1,1].set_ylabel('Log10(Resource Units)')
        axes[1,1].set_title('Economic Output vs Population')
        
        # Efficiency distribution
        eff_data = worlds_df['Efficiency']
        axes[1,2].hist(eff_data, bins=21, alpha=0.7, color='mediumpurple')
        axes[1,2].set_xlabel('Efficiency Modifier')
        axes[1,2].set_ylabel('Number of Worlds')
        axes[1,2].set_title('Economic Efficiency Distribution')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'economic_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_interactive_dashboard(self, worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, output_dir: Path):
        """Create interactive Plotly dashboard"""
        if worlds_df.empty or sector_stats.empty:
            return
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Sector Economic Output', 'Economic Efficiency by Sector',
                'Trade Specialization', 'Population vs Economic Output',
                'Starport Infrastructure', 'Economic Outliers'
            ],
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Top 20 sectors by RU
        top_sectors = sector_stats.nlargest(20, 'ResourceUnits_sum')
        fig.add_trace(
            go.Bar(
                x=top_sectors['ResourceUnits_sum'],
                y=top_sectors['Sector'],
                orientation='h',
                name='Total RU',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # RU per capita scatter
        fig.add_trace(
            go.Scatter(
                x=sector_stats['ResourceUnits_sum'],
                y=sector_stats['RU_per_capita'],
                mode='markers',
                text=sector_stats['Sector'],
                name='Sectors',
                marker=dict(size=8, color='red', opacity=0.6)
            ),
            row=1, col=2
        )
        
        # Trade specialization
        trade_data = pd.DataFrame({
            'Agricultural': [sector_stats['Pct_Agricultural'].mean()],
            'Industrial': [sector_stats['Pct_Industrial'].mean()],
            'Rich': [sector_stats['Pct_Rich'].mean()]
        })
        
        for i, (col, val) in enumerate(trade_data.iloc[0].items()):
            fig.add_trace(
                go.Bar(x=[col], y=[val], name=col, showlegend=False),
                row=2, col=1
            )
        
        # Population vs RU scatter (sample)
        sample_worlds = worlds_df.sample(n=min(1000, len(worlds_df)))
        sample_worlds = sample_worlds[(sample_worlds['ResourceUnits'] > 0) & (sample_worlds['Population'] > 0)]
        
        fig.add_trace(
            go.Scatter(
                x=np.log10(sample_worlds['Population']),
                y=np.log10(sample_worlds['ResourceUnits']),
                mode='markers',
                text=sample_worlds['Name'],
                name='Worlds',
                marker=dict(size=4, opacity=0.6)
            ),
            row=2, col=2
        )
        
        # Starport distribution
        starport_counts = worlds_df['Starport'].value_counts()
        fig.add_trace(
            go.Bar(
                x=starport_counts.index,
                y=starport_counts.values,
                name='Starports',
                showlegend=False,
                marker_color='green'
            ),
            row=3, col=1
        )
        
        # Economic outliers (top RU worlds)
        top_worlds = worlds_df.nlargest(50, 'ResourceUnits')
        fig.add_trace(
            go.Scatter(
                x=top_worlds['Population'],
                y=top_worlds['ResourceUnits'],
                mode='markers',
                text=top_worlds['Name'] + '<br>' + top_worlds['Sector'],
                name='Top Economic Worlds',
                marker=dict(size=8, color='gold')
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Third Imperium Economic Dashboard",
            title_x=0.5,
            showlegend=False
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Resource Units", row=1, col=1)
        fig.update_yaxes(title_text="Sector", row=1, col=1)
        fig.update_xaxes(title_text="Total Resource Units", row=1, col=2)
        fig.update_yaxes(title_text="RU per Capita", row=1, col=2)
        fig.update_xaxes(title_text="Log10(Population)", row=2, col=2)
        fig.update_yaxes(title_text="Log10(Resource Units)", row=2, col=2)
        fig.update_xaxes(title_text="Population", row=3, col=2)
        fig.update_yaxes(title_text="Resource Units", row=3, col=2)
        
        # Save interactive dashboard
        fig.write_html(output_dir / 'interactive_dashboard.html')
        
        logger.info("Interactive dashboard saved as interactive_dashboard.html")
    
    def create_sector_heatmap(self, sector_stats: pd.DataFrame, output_dir: Path):
        """Create heatmap of sector economic metrics"""
        if sector_stats.empty:
            return
        
        # Select key metrics for heatmap
        heatmap_data = sector_stats[[
            'Sector', 'ResourceUnits_sum', 'RU_per_capita', 
            'Pct_Industrial', 'Pct_Agricultural', 'StarportScore_mean'
        ]].copy()
        
        # Normalize metrics to 0-100 scale for comparison
        metrics = ['ResourceUnits_sum', 'RU_per_capita', 'Pct_Industrial', 'Pct_Agricultural', 'StarportScore_mean']
        for metric in metrics:
            col_max = heatmap_data[metric].max()
            col_min = heatmap_data[metric].min()
            if col_max > col_min:
                heatmap_data[f'{metric}_norm'] = ((heatmap_data[metric] - col_min) / (col_max - col_min)) * 100
            else:
                heatmap_data[f'{metric}_norm'] = 0
        
        # Take top 30 sectors by total RU for readability
        top_sectors = heatmap_data.nlargest(30, 'ResourceUnits_sum')
        
        # Prepare data for heatmap
        heatmap_matrix = top_sectors[[
            'ResourceUnits_sum_norm', 'RU_per_capita_norm', 
            'Pct_Industrial', 'Pct_Agricultural', 'StarportScore_mean_norm'
        ]].values
        
        plt.figure(figsize=(12, 16))
        sns.heatmap(
            heatmap_matrix,
            yticklabels=top_sectors['Sector'],
            xticklabels=['Total Economic Output', 'Economic Efficiency', 'Industrial %', 'Agricultural %', 'Starport Quality'],
            cmap='RdYlBu_r',
            center=50,
            annot=False,
            fmt='.0f',
            cbar_kws={'label': 'Relative Score (0-100)'}
        )
        
        plt.title('Third Imperium Sector Economic Profile Heatmap\n(Top 30 Sectors by Total Output)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Economic Metrics', fontsize=12)
        plt.ylabel('Sectors', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_dir / 'sector_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_trade_network_analysis(self, worlds_df: pd.DataFrame, output_dir: Path):
        """Analyze and visualize trade patterns"""
        if worlds_df.empty:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Third Imperium Trade Pattern Analysis', fontsize=16, fontweight='bold')
        
        # Agricultural vs Industrial worlds by sector
        sector_trade = worlds_df.groupby('Sector').agg({
            'IsAg': 'sum',
            'IsIn': 'sum',
            'Name': 'count'
        }).reset_index()
        
        sector_trade['Ag_ratio'] = sector_trade['IsAg'] / sector_trade['Name']
        sector_trade['In_ratio'] = sector_trade['IsIn'] / sector_trade['Name']
        
        axes[0,0].scatter(sector_trade['Ag_ratio'], sector_trade['In_ratio'], alpha=0.6)
        axes[0,0].set_xlabel('Agricultural World Ratio')
        axes[0,0].set_ylabel('Industrial World Ratio')
        axes[0,0].set_title('Sector Trade Specialization')
        
        # Economic output by trade type
        trade_ru = []
        trade_labels = []
        for code in ['Ag', 'In', 'Ri', 'Hi', 'Po']:
            mask = worlds_df[f'Is{code}'] == True
            if mask.any():
                trade_ru.append(worlds_df[mask]['ResourceUnits'].mean())
                trade_labels.append(code)
        
        axes[0,1].bar(trade_labels, trade_ru, alpha=0.7)
        axes[0,1].set_xlabel('Trade Code')
        axes[0,1].set_ylabel('Average Resource Units')
        axes[0,1].set_title('Economic Output by Trade Classification')
        
        # Population vs Economic Output by Starport Class
        for starport in ['A', 'B', 'C', 'D', 'E']:
            subset = worlds_df[worlds_df['Starport'] == starport]
            if len(subset) > 0:
                subset_sample = subset.sample(n=min(200, len(subset)))
                valid_data = subset_sample[(subset_sample['Population'] > 0) & (subset_sample['ResourceUnits'] > 0)]
                if len(valid_data) > 0:
                    axes[1,0].scatter(np.log10(valid_data['Population']), 
                                    np.log10(valid_data['ResourceUnits']), 
                                    label=f'Class {starport}', alpha=0.6, s=20)
        
        axes[1,0].set_xlabel('Log10(Population)')
        axes[1,0].set_ylabel('Log10(Resource Units)')
        axes[1,0].set_title('Economic Output vs Population by Starport Class')
        axes[1,0].legend()
        
        # Economic efficiency distribution
        worlds_df['RU_per_capita'] = worlds_df['ResourceUnits'] / worlds_df['Population']
        worlds_df['RU_per_capita'] = worlds_df['RU_per_capita'].replace([np.inf, -np.inf], np.nan)
        ru_pc_data = worlds_df['RU_per_capita'].dropna()
        
        if len(ru_pc_data) > 0:
            # Use log scale for better visualization
            log_ru_pc = np.log10(ru_pc_data[ru_pc_data > 0])
            axes[1,1].hist(log_ru_pc, bins=50, alpha=0.7, color='purple')
            axes[1,1].set_xlabel('Log10(RU per Capita)')
            axes[1,1].set_ylabel('Number of Worlds')
            axes[1,1].set_title('Economic Efficiency Distribution')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'trade_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_all_visualizations(self, worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, output_dir: Path):
        """Generate all visualization outputs"""
        logger.info("Generating visualizations...")
        
        # Create output directory for plots
        viz_dir = output_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        try:
            self.plot_sector_rankings(sector_stats, viz_dir)
            self.plot_economic_distributions(worlds_df, viz_dir)
            self.create_sector_heatmap(sector_stats, viz_dir)
            self.plot_trade_network_analysis(worlds_df, viz_dir)
            self.create_interactive_dashboard(worlds_df, sector_stats, viz_dir)
            
            logger.info(f"All visualizations saved to {viz_dir}")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            logger.error("Some visualizations may require additional dependencies (matplotlib, seaborn, plotly)")

def create_visualizations(worlds_df: pd.DataFrame, sector_stats: pd.DataFrame, output_dir: str = "output"):
    """Convenience function to generate all visualizations"""
    visualizer = EconomicVisualizer()
    output_path = Path(output_dir)
    visualizer.generate_all_visualizations(worlds_df, sector_stats, output_path)
