# Universal Trade Circuit Optimizer - README

## Overview

I've created a comprehensive **Universal Trade Circuit Optimizer** that analyzes circular trade routes for any sector(s) in the Traveller universe, with fully customizable ship parameters.

## 🚀 Key Features

### **Flexible Ship Configuration**
- **Jump Range**: 1-6 parsecs (default: 2)
- **Cargo Capacity**: Any tonnage (default: 64 tons)
- **Circuit Analysis**: Finds optimal closed-loop trade routes that return to starting point

### **Universal Sector Support**
- Works with any sector from the Traveller universe
- Can analyze multiple sectors simultaneously
- Automatically filters to high-value worlds for performance

### **Intelligent Trade Analysis**
- Considers trade codes, starport quality, population, and economic strength
- Calculates distance penalties and trade bonuses
- Finds viable trade goods matches between worlds

## 📋 Generated Files

1. **`universal_trade_circuit_optimizer.py`** - Main analysis script
2. **`usage_examples.py`** - Usage examples and documentation
3. **Generated CSV files** (when using `--save` option):
   - `{sector}_j{jump}_c{cargo}_circuits.csv` - Circuit summaries
   - `{sector}_j{jump}_c{cargo}_circuit_legs.csv` - Detailed leg-by-leg analysis

## 💻 Usage Examples

### Basic Usage (Default: Jump-2, 64 tons)
```bash
python3 universal_trade_circuit_optimizer.py "Trojan Reach"
```

### Custom Ship Parameters
```bash
python3 universal_trade_circuit_optimizer.py "Trojan Reach" -j 3 -c 100
```

### Save Results to CSV
```bash
python3 universal_trade_circuit_optimizer.py "Spinward Marches" -j 2 -c 50 --save
```

### Multiple Sectors
```bash
python3 universal_trade_circuit_optimizer.py "Trojan Reach" "Reft" -j 4 -c 200
```

### Show Help
```bash
python3 universal_trade_circuit_optimizer.py --help
```

## 🎯 Example Output

```
TOP 3 CIRCULAR TRADE ROUTES
------------------------------------------------------------

1. CIRCUIT: Kryslion → Berengaria → Cyan → Perrior → Kryslion
   Sectors: Trojan Reach
   Hexes: 2002 → 2105 → 2102 → 2203
   Starports: D → B → C → A
   Total Distance: 9 parsecs
   Circuit Profit: Cr 1,054,667 (100 tons)
   Profit per Ton: Cr 10,547
   Efficiency: Cr 1172 per parsec per ton
   Detailed Legs:
     1. Berengaria → Cyan (3pc): Cr 3780/ton (Food)
     2. Cyan → Perrior (1pc): Cr 3780/ton (Manufactured Goods)
     3. Perrior → Kryslion (2pc): Cr 2987/ton (Raw Materials)
```

## 📊 Command Line Options

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `sectors` | - | Sector name(s) to analyze | Required |
| `--jump` | `-j` | Ship jump range (parsecs) | 2 |
| `--cargo` | `-c` | Cargo capacity (tons) | 64 |
| `--num-circuits` | `-n` | Number of circuits to display | 10 |
| `--min-stops` | - | Minimum stops in circuit | 3 |
| `--max-stops` | - | Maximum stops in circuit | 6 |
| `--save` | - | Save results to CSV files | False |

## 🔍 Trade Analysis Features

### **Trade Goods Classification**
- **Agricultural worlds**: Export food → Import manufactured goods
- **Industrial worlds**: Export manufactured goods → Import raw materials
- **Rich worlds**: Export luxury goods → Import rare materials
- **Poor worlds**: Export raw materials → Import everything else
- **Desert worlds**: Export minerals → Import food/water
- **And many more trade code combinations**

### **Profit Calculation Factors**
- **Starport Quality**: A-class (best) to X-class (worst) multipliers
- **Population Size**: Higher population = better markets
- **Economic Strength**: Based on Resource Units calculation
- **Distance Penalty**: Closer worlds = higher profits
- **Special Trade Bonuses**: e.g., Food to High-pop worlds (+50%)

### **Performance Optimization**
- Automatically limits analysis to top 50 worlds for large sectors
- Smart permutation testing (fewer for longer circuits)
- Configurable circuit length limits
- Memory-efficient processing

## 🚢 Recommended Ship Configurations

### **Small Trader (Jump-2, 64 tons)** - Default
- Good balance of range and cargo
- Suitable for most sectors
- Lower investment, moderate profits

### **Medium Trader (Jump-3, 100 tons)**
- Better range opens more opportunities
- Higher cargo capacity = higher absolute profits
- Sweet spot for established traders

### **Bulk Trader (Jump-1, 200+ tons)**
- Maximizes cargo for high-volume/low-margin trades
- Limited to adjacent worlds
- Best for dense, well-connected sectors

### **Long-Range Trader (Jump-4+, any cargo)**
- Access to remote, high-profit opportunities
- Higher fuel costs
- Best for sectors with scattered high-value worlds

## 🌟 Success Stories

### **Trojan Reach Results**
- **Best Circuit**: Cr 1,054,667 profit (Jump-3, 100 tons)
- **Most Efficient**: Kryslion → Berengaria → Cyan → perrior
- **Key Hubs**: Perrior (Naval base), Cyan (High-pop), Berengaria (Agricultural)

### **Performance Benchmarks**
- **Small sectors** (50-100 worlds): Complete analysis in seconds
- **Large sectors** (200+ worlds): Limited to top 50 worlds for performance
- **Memory usage**: Optimized for systems with 8GB+ RAM

## 🛠️ Technical Details

### **Distance Calculation**
Uses proper hex-map distance calculation for accurate parsec measurements.

### **Data Source**
Integrates with your existing comprehensive Traveller universe economic database (17,643+ worlds).

### **Output Formats**
- **Console**: Human-readable analysis with recommendations
- **CSV**: Machine-readable data for further analysis
- **Structured**: Both summary and detailed leg-by-leg breakdowns

## 🚀 Getting Started

1. **Ensure you have the economic database**: Run the universal economic analysis first
2. **Choose your sector**: Any sector name from the Traveller universe
3. **Configure your ship**: Jump range and cargo capacity
4. **Run the analysis**: See immediate results and recommendations
5. **Save results**: Use `--save` flag for CSV output
6. **Start trading**: Follow the recommended circuits for maximum profit!

---

**Safe travels, Trader! May your cargo bays be full and your jump drives true!** 🌌
