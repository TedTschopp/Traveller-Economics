# Example configuration file for Traveller Economic Analysis
# Copy this to config.py and modify as needed

class Config:
    """Configuration settings for economic analysis"""
    
    # API Settings
    MILIEU = "M1105"  # Options: M1105, M1120, IW (Imperial War), etc.
    CANON_TAG = "Official"  # Filter for data quality
    REQUEST_DELAY = 1.0  # Seconds between API calls (be respectful)
    
    # Cache Settings
    CACHE_DIR = "cache"
    USE_CACHE = True  # Set to False to force fresh downloads
    
    # Output Settings
    OUTPUT_DIR = "output"
    SAVE_RAW_DATA = True
    GENERATE_VISUALIZATIONS = True
    RUN_ADVANCED_ANALYSIS = True
    
    # Analysis Parameters
    IMPERIUM_ALLEGIANCE_PREFIX = "Im"  # Filter for Imperial worlds
    MIN_RU_FOR_CLUSTERS = 100  # Minimum RU to be considered in economic clusters
    ECONOMIC_GROWTH_RATE = 0.02  # Annual growth rate for forecasting (2%)
    
    # Visualization Settings
    PLOT_STYLE = "seaborn-v0_8"  # matplotlib style
    COLOR_PALETTE = "husl"  # seaborn color palette
    FIGURE_DPI = 300  # Resolution for saved plots
    
    # Economic Classification Thresholds
    DEVELOPMENT_THRESHOLDS = {
        "highly_developed": {"ru_per_capita": 50, "starport_score": 2.5, "industrial_pct": 30},
        "developed": {"ru_per_capita": 20, "starport_score": 2.0, "industrial_pct": 15},
        "developing": {"ru_per_capita": 5, "starport_score": 1.5, "industrial_pct": 0},
        "emerging": {"ru_per_capita": 1, "starport_score": 0, "industrial_pct": 0}
    }
    
    # Trade Multipliers (for advanced analysis)
    TRADE_MULTIPLIERS = {
        'Ag': {'In': 1.5, 'Hi': 1.3, 'Ri': 1.2},  # Agricultural worlds
        'In': {'Ag': 1.4, 'Ri': 1.6, 'Hi': 1.1},  # Industrial worlds
        'Ri': {'Ag': 1.2, 'In': 1.5, 'Hi': 1.3},  # Rich worlds
        'Hi': {'Ag': 1.3, 'In': 1.1, 'Ri': 1.2}   # High population worlds
    }
    
    # Logging Settings
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True
    LOG_FILE = "traveller_economics.log"

# Historical Milieux for Time Series Analysis
AVAILABLE_MILIEUX = {
    "M1105": "Year 1105 - Classic Traveller Era",
    "M1120": "Year 1120 - Late Classic Era", 
    "M1248": "Year 1248 - New Era",
    "IW": "Imperial War Period",
    "TNE": "The New Era",
    "M1900": "Far Future Era"
}

# Sector Groupings for Regional Analysis
SECTOR_REGIONS = {
    "Core": ["Core", "Fornast", "Delphi", "Old Expanses"],
    "Spinward_Marches": ["Spinward Marches", "Deneb", "Trojan Reach", "Reft"],
    "Solomani_Rim": ["Solomani Rim", "Alpha Crucis", "Daibei", "Old Expanses"],
    "Vargr_Extents": ["Gvurrdon", "Provence", "Windhorn", "Antares"],
    "Zhodani_Consulate": ["Zhodane", "Cronor", "Querion", "Vanguard Reaches"]
}

# Trade Code Descriptions
TRADE_CODE_DESCRIPTIONS = {
    "Ag": "Agricultural - Major food/biological exports",
    "In": "Industrial - Manufacturing and technology hub", 
    "Ri": "Rich - High standard of living and wealth",
    "Hi": "High Population - Over 1 billion inhabitants",
    "Po": "Poor - Limited economic development",
    "Na": "Non-Agricultural - Cannot support population with local food",
    "Va": "Vacuum - No atmosphere or trace atmosphere",
    "De": "Desert - Little or no surface water",
    "Fl": "Fluid Oceans - Non-water liquid oceans",
    "Ic": "Ice-Capped - Frozen surface water",
    "Wa": "Water World - Surface almost entirely water"
}

# Example usage in custom analysis
def get_custom_config():
    """Return a customized configuration"""
    config = Config()
    
    # Example: Focus on Spinward Marches region only  
    config.REGION_FILTER = SECTOR_REGIONS["Spinward_Marches"]
    
    # Example: Different time period
    config.MILIEU = "M1120"
    
    # Example: More aggressive caching
    config.REQUEST_DELAY = 0.5
    
    return config
