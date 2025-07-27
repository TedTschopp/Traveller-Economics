#!/usr/bin/env python3
"""
Universal Trade Circuit Optimizer for Traveller
Analyzes optimal circular trade routes for any sector(s) with customizable ship parameters
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
from itertools import combinations, permutations
from typing import List, Dict, Tuple, Optional

class UniversalTradeCircuitOptimizer:
    """Optimize circular trade routes for any sector with customizable ship parameters"""
    
    def __init__(self, sectors: List[str], jump_range: int = 2, cargo_tons: int = 64):
        self.sectors = sectors if isinstance(sectors, list) else [sectors]
        self.jump_range = jump_range
        self.cargo_tons = cargo_tons
        self.worlds_df = None
        self.load_data()
        
    def load_data(self):
        """Load the economic data and filter for specified sectors"""
        # Try to load from output directory first (preferred location for CSV data)
        data_path = Path("output/all_imperium_worlds.csv")
        if not data_path.exists():
            # Try Analysis directory for backward compatibility
            data_path = Path("Analysis/all_imperium_worlds.csv")
            if not data_path.exists():
                data_path = Path("all_imperium_worlds.csv")
                if not data_path.exists():
                    raise FileNotFoundError("Economic data not found. Run universal analysis first.")
        
        df = pd.read_csv(data_path)
        
        # Filter for specified sectors
        self.worlds_df = df[df['Sector'].isin(self.sectors)].copy()
        
        if len(self.worlds_df) == 0:
            print(f"No worlds found for sectors: {', '.join(self.sectors)}")
            print("Available sectors:")
            available_sectors = sorted(df['Sector'].unique())
            for i, sector in enumerate(available_sectors):
                if i % 4 == 0:
                    print()
                print(f"{sector:<20}", end="")
            print("\n")
            sys.exit(1)
        
        # Parse hex coordinates for distance calculations
        self.worlds_df['Hex'] = self.worlds_df['Hex'].astype(str).str.zfill(4)
        self.worlds_df['hex_x'] = self.worlds_df['Hex'].str[:2].astype(int)
        self.worlds_df['hex_y'] = self.worlds_df['Hex'].str[2:].astype(int)
        
        print(f"Loaded {len(self.worlds_df)} worlds from {len(self.sectors)} sector(s): {', '.join(self.sectors)}")
        
    def calculate_distance(self, hex1: str, hex2: str) -> float:
        """Calculate hex distance between two worlds"""
        hex1_str = str(hex1).zfill(4)
        hex2_str = str(hex2).zfill(4)
        
        x1, y1 = int(hex1_str[:2]), int(hex1_str[2:])
        x2, y2 = int(hex2_str[:2]), int(hex2_str[2:])
        
        # Hex grid distance calculation
        dx = x2 - x1
        dy = y2 - y1
        
        if (dx >= 0 and dy >= 0) or (dx < 0 and dy < 0):
            distance = max(abs(dx), abs(dy))
        else:
            distance = abs(dx) + abs(dy)
            
        return distance
    
    def classify_trade_goods(self, world_data: pd.Series) -> Dict[str, List[str]]:
        """Classify what goods a world produces/demands based on trade codes"""
        trade_codes = world_data['TradeCodes']
        
        # Handle different data formats
        if isinstance(trade_codes, str):
            try:
                trade_codes = eval(trade_codes)
            except:
                trade_codes = []
        elif trade_codes is None or (isinstance(trade_codes, float) and np.isnan(trade_codes)):
            trade_codes = []
        elif not isinstance(trade_codes, list):
            trade_codes = []
        
        exports = []
        imports = []
        
        # Agricultural worlds export food, import manufactured goods
        if 'Ag' in trade_codes:
            exports.extend(['Food', 'Livestock', 'Organics'])
            imports.extend(['Manufactured Goods', 'Machinery', 'Electronics'])
            
        # Industrial worlds export manufactured goods, import raw materials
        if 'In' in trade_codes:
            exports.extend(['Manufactured Goods', 'Machinery', 'Electronics', 'Vehicles'])
            imports.extend(['Raw Materials', 'Ores', 'Crystals', 'Food'])
            
        # Rich worlds import luxury goods, export high-value items
        if 'Ri' in trade_codes:
            exports.extend(['Luxury Goods', 'Precious Metals', 'Art Objects'])
            imports.extend(['Luxury Consumables', 'Rare Materials'])
            
        # High population worlds import food, export manufactured goods
        if 'Hi' in trade_codes:
            imports.extend(['Food', 'Raw Materials'])
            exports.extend(['Manufactured Goods', 'Electronics'])
            
        # Poor worlds export raw materials, import everything else
        if 'Po' in trade_codes:
            exports.extend(['Raw Materials', 'Ores', 'Labor'])
            imports.extend(['Food', 'Manufactured Goods', 'Medicine'])
            
        # Desert worlds export minerals, import food and water
        if 'De' in trade_codes:
            exports.extend(['Minerals', 'Ores', 'Crystals'])
            imports.extend(['Food', 'Water', 'Life Support'])
            
        # Ice worlds export water, import food and manufactured goods
        if 'Ic' in trade_codes:
            exports.extend(['Water', 'Hydrogen'])
            imports.extend(['Food', 'Manufactured Goods', 'Heating Equipment'])
            
        # Non-aligned worlds often have unique trade opportunities
        if 'Na' in trade_codes:
            exports.extend(['Exotic Materials', 'Information'])
            imports.extend(['Standard Goods', 'Technology'])
        
        # Asteroid belts export minerals
        if 'As' in trade_codes:
            exports.extend(['Minerals', 'Ores', 'Crystals', 'Rare Elements'])
            imports.extend(['Food', 'Manufactured Goods', 'Life Support'])
            
        return {'exports': list(set(exports)), 'imports': list(set(imports))}
    
    def calculate_trade_profit(self, origin: pd.Series, destination: pd.Series) -> Dict:
        """Calculate potential profit for trade between two worlds"""
        try:
            origin_trade = self.classify_trade_goods(origin)
            dest_trade = self.classify_trade_goods(destination)
            
            # Find matching trade opportunities
            matches = set(origin_trade['exports']).intersection(set(dest_trade['imports']))
            
            if not matches:
                return {'profit_per_ton': 0, 'goods': [], 'viable': False, 'distance': 0}
            
            # Base profit calculation factors
            starport_bonus = {4: 1.4, 3: 1.2, 2: 1.0, 1: 0.8, 0: 0.6, -1: 0.4}
            
            origin_bonus = starport_bonus.get(origin.get('StarportScore', 0), 0.6)
            dest_bonus = starport_bonus.get(destination.get('StarportScore', 0), 0.6)
            
            # Population factors
            pop_factor = min(2.0, (destination.get('PopulationExp', 0) / 6.0))
            
            # Resource Unit factor
            economic_factor = min(2.0, (destination.get('ResourceUnits', 0) / 500.0))
            
            # Distance penalty
            distance = self.calculate_distance(origin['Hex'], destination['Hex'])
            distance_penalty = max(0.5, (1.0 - (distance * 0.1)))
            
            # Calculate base profit per ton
            base_profit = 1000  # Base Cr 1000 per ton
            profit_multiplier = origin_bonus * dest_bonus * pop_factor * economic_factor * distance_penalty
            
            profit_per_ton = base_profit * profit_multiplier
            
            # Special trade bonuses
            bonus_trades = {
                ('Ag', 'Hi'): 1.5,  # Food to high pop
                ('In', 'Po'): 1.4,  # Manufactured goods to poor worlds
                ('Ri', 'Hi'): 1.6,  # Luxury goods to rich, high pop
                ('De', 'Ag'): 1.3,  # Minerals to agricultural
                ('Ic', 'De'): 1.4,  # Water to desert worlds
                ('As', 'In'): 1.3,  # Asteroid minerals to industrial
            }
            
            # Get trade codes
            origin_codes = origin['TradeCodes']
            dest_codes = destination['TradeCodes']
            
            if isinstance(origin_codes, str):
                try:
                    origin_codes = eval(origin_codes)
                except:
                    origin_codes = []
            elif not isinstance(origin_codes, list):
                origin_codes = []
                
            if isinstance(dest_codes, str):
                try:
                    dest_codes = eval(dest_codes)
                except:
                    dest_codes = []
            elif not isinstance(dest_codes, list):
                dest_codes = []
            
            for (o_code, d_code), bonus in bonus_trades.items():
                if o_code in origin_codes and d_code in dest_codes:
                    profit_per_ton *= bonus
                    break
            
            return {
                'profit_per_ton': profit_per_ton,
                'goods': list(matches),
                'viable': len(matches) > 0 and profit_per_ton > 400,  # Lower threshold for flexibility
                'distance': distance
            }
            
        except Exception as e:
            return {'profit_per_ton': 0, 'goods': [], 'viable': False, 'distance': 0}
    
    def find_optimal_circuits(self, min_stops: int = 3, max_stops: int = 6, max_circuits: int = 20) -> List[Dict]:
        """Find optimal circular trading circuits (relaxed for more discovery)"""
        # Get high-value worlds for circuit analysis, with better filtering for large sectors
        high_value_worlds = self.worlds_df[
            (self.worlds_df['ResourceUnits'] > 100) | 
            (self.worlds_df['IsRi'] == 1) | 
            (self.worlds_df['IsHi'] == 1) |
            (self.worlds_df['IsAg'] == 1) |
            (self.worlds_df['IsIn'] == 1)
        ].copy()

        # For large datasets, further filter to top worlds by Resource Units (now 200 instead of 50)
        if len(high_value_worlds) > 200:
            high_value_worlds = high_value_worlds.nlargest(200, 'ResourceUnits')
            print(f"Limited analysis to top 200 worlds by economic value")

        print(f"Analyzing circuits with {len(high_value_worlds)} high-value worlds...")
        print(f"Jump range: {self.jump_range} parsecs, Cargo: {self.cargo_tons} tons")

        best_circuits = []

        # Try different circuit lengths (now up to 10 stops)
        for circuit_length in range(min_stops, min(max_stops + 1, len(high_value_worlds))):
            print(f"  Checking {circuit_length}-stop circuits...")

            # Allow more combinations for larger circuits (less aggressive limiting)
            if len(high_value_worlds) > 30:
                max_combinations = min(1000, int(5000 / circuit_length))  # More combinations for longer circuits
            else:
                max_combinations = min(2000, int(10000 / circuit_length))

            circuit_count = 0
            for world_indices in combinations(range(len(high_value_worlds)), circuit_length):
                circuit_count += 1
                if circuit_count > max_combinations:
                    break

                worlds = [high_value_worlds.iloc[i] for i in world_indices]

                # Try different orders for the circuit (still limited for performance)
                best_order = None
                best_profit = 0

                # For performance, limit permutation testing
                if circuit_length <= 3:
                    orders_to_try = list(permutations(worlds))[:6]
                elif circuit_length <= 5:
                    orders_to_try = list(permutations(worlds))[:8]
                else:
                    # For 6+ stops, try original, reversed, and one random shuffle
                    import random
                    orders_to_try = [tuple(worlds), tuple(reversed(worlds))]
                    random_order = list(worlds)
                    random.shuffle(random_order)
                    orders_to_try.append(tuple(random_order))

                for world_order in orders_to_try:
                    circuit_valid = True
                    total_distance = 0
                    circuit_profit = 0
                    circuit_legs = []

                    # Check each leg of the circuit
                    for i in range(len(world_order)):
                        current = world_order[i]
                        next_world = world_order[(i + 1) % len(world_order)]

                        distance = self.calculate_distance(current['Hex'], next_world['Hex'])

                        if distance > self.jump_range:
                            circuit_valid = False
                            break

                        total_distance += distance

                        # Calculate profit for this leg
                        trade_result = self.calculate_trade_profit(current, next_world)
                        if trade_result['viable']:
                            circuit_profit += trade_result['profit_per_ton']
                            circuit_legs.append({
                                'from': current['Name'],
                                'to': next_world['Name'],
                                'profit_per_ton': trade_result['profit_per_ton'],
                                'goods': trade_result['goods'][:3],
                                'distance': distance
                            })

                    if circuit_valid and circuit_profit > best_profit:
                        best_profit = circuit_profit
                        best_order = world_order
                        best_legs = circuit_legs
                        best_total_distance = total_distance

                # If we found a viable circuit, add it to our results (lowered profit threshold)
                if best_order and best_profit > 100:  # Lowered minimum viable circuit profit
                    num_jumps = len(best_order)
                    fuel_cost_per_jump = 1000  # Cr 1,000 per jump (standard for J-2, 64 dton)
                    total_fuel_cost = num_jumps * fuel_cost_per_jump
                    maintenance_cost = 18500  # Cr 18,500 per circuit (monthly, Free Trader)
                    gross_profit = best_profit * self.cargo_tons
                    net_profit = gross_profit - total_fuel_cost - maintenance_cost
                    circuit = {
                        'worlds': [w['Name'] for w in best_order],
                        'hexes': [w['Hex'] for w in best_order],
                        'starports': [w['Starport'] for w in best_order],
                        'sectors': [w['Sector'] for w in best_order],
                        'total_distance': best_total_distance,
                        'total_profit_per_ton': best_profit,
                        'total_profit': gross_profit,
                        'net_profit': net_profit,
                        'fuel_cost': total_fuel_cost,
                        'maintenance_cost': maintenance_cost,
                        'profit_per_jump': best_profit / len(best_order),
                        'circuit_length': len(best_order),
                        'legs': best_legs,
                        'efficiency': best_profit / best_total_distance if best_total_distance > 0 else 0
                    }
                    best_circuits.append(circuit)

        # Sort by total profit and return top circuits
        return sorted(best_circuits, key=lambda x: x['total_profit'], reverse=True)[:max_circuits]
    
    def generate_circuit_report(self, max_circuits: int = 10):
        """Generate comprehensive circular trade route report"""
        print("=" * 80)
        print("UNIVERSAL TRADE CIRCUIT OPTIMIZER")
        print("=" * 80)
        print(f"Sectors: {', '.join(self.sectors)}")
        print(f"Ship Configuration: Jump-{self.jump_range}, {self.cargo_tons} tons cargo capacity")
        print(f"Analysis Date: 1105 Imperial")
        print()
        
        # Find optimal circuits
        circuits = self.find_optimal_circuits(max_circuits=max_circuits)
        
        if not circuits:
            print("No viable circuits found with current parameters.")
            print("Try:")
            print("- Increasing jump range")
            print("- Selecting sectors with more interconnected worlds")
            print("- Reducing minimum profit requirements")
            return []
        
        print(f"TOP {min(len(circuits), max_circuits)} CIRCULAR TRADE ROUTES")
        print("-" * 60)
        
        for i, circuit in enumerate(circuits[:max_circuits]):
            print(f"\n{i+1}. CIRCUIT: {' → '.join(circuit['worlds'])} → {circuit['worlds'][0]}")
            print(f"   Sectors: {', '.join(set(circuit['sectors']))}")
            print(f"   Hexes: {' → '.join(circuit['hexes'])}")
            print(f"   Starports: {' → '.join(circuit['starports'])}")
            print(f"   Total Distance: {circuit['total_distance']} parsecs")
            print(f"   Gross Circuit Profit: Cr {circuit['total_profit']:,.0f} ({self.cargo_tons} tons)")
            print(f"   Fuel Cost: Cr {circuit['fuel_cost']:,.0f} ({circuit['circuit_length']} jumps @ Cr 1,000)")
            print(f"   Maintenance Cost: Cr {circuit['maintenance_cost']:,.0f} (per circuit)")
            print(f"   Net Circuit Profit: Cr {circuit['net_profit']:,.0f}")
            print(f"   Profit per Ton: Cr {circuit['total_profit_per_ton']:,.0f}")
            print(f"   Efficiency: Cr {circuit['efficiency']:.0f} per parsec per ton")
            
            print("   Detailed Legs:")
            for j, leg in enumerate(circuit['legs']):
                print(f"     {j+1}. {leg['from']} → {leg['to']} ({leg['distance']}pc)")
                print(f"        Profit: Cr {leg['profit_per_ton']:.0f}/ton")
                if leg['goods']:
                    print(f"        Goods: {', '.join(leg['goods'])}")
        
        # Summary statistics
        if circuits:
            avg_profit = sum(c['total_profit'] for c in circuits[:5]) / min(5, len(circuits))
            avg_distance = sum(c['total_distance'] for c in circuits[:5]) / min(5, len(circuits))
            
            print(f"\n\nCIRCUIT ANALYSIS SUMMARY")
            print("-" * 40)
            print(f"Best Circuit Profit: Cr {circuits[0]['total_profit']:,.0f}")
            print(f"Average Top-5 Profit: Cr {avg_profit:,.0f}")
            print(f"Average Circuit Distance: {avg_distance:.1f} parsecs")
            print(f"Circuits Found: {len(circuits)}")
        
        return circuits
    
    def save_results(self, circuits: List[Dict], filename_prefix: str = None):
        """Save circuit results to CSV files"""
        if not circuits:
            print("No circuits to save.")
            return
        
        if filename_prefix is None:
            sector_str = "_".join([s.replace(" ", "_").lower() for s in self.sectors])
            filename_prefix = f"{sector_str}_j{self.jump_range}_c{self.cargo_tons}"
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Save circuit summary
        circuits_df = pd.DataFrame([{
            'circuit_rank': i+1,
            'worlds': ' → '.join(c['worlds']) + f" → {c['worlds'][0]}",
            'sectors': ', '.join(set(c['sectors'])),
            'hexes': ' → '.join(c['hexes']),
            'starports': ' → '.join(c['starports']),
            'total_distance': c['total_distance'],
            'total_profit': c['total_profit'],
            'profit_per_ton': c['total_profit_per_ton'],
            'circuit_length': c['circuit_length'],
            'efficiency': c['efficiency']
        } for i, c in enumerate(circuits)])
        
        circuits_file = output_dir / f"{filename_prefix}_circuits.csv"
        circuits_df.to_csv(circuits_file, index=False)
        
        # Save detailed legs
        legs_data = []
        for i, circuit in enumerate(circuits):
            for j, leg in enumerate(circuit['legs']):
                legs_data.append({
                    'circuit_rank': i+1,
                    'leg_number': j+1,
                    'from_world': leg['from'],
                    'to_world': leg['to'],
                    'distance': leg['distance'],
                    'profit_per_ton': leg['profit_per_ton'],
                    'total_leg_profit': leg['profit_per_ton'] * self.cargo_tons,
                    'goods': ', '.join(leg['goods']) if leg['goods'] else ''
                })
        
        legs_df = pd.DataFrame(legs_data)
        legs_file = output_dir / f"{filename_prefix}_circuit_legs.csv"
        legs_df.to_csv(legs_file, index=False)
        
        print(f"\nResults saved to:")
        print(f"- {circuits_file}")
        print(f"- {legs_file}")


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Universal Trade Circuit Optimizer for Traveller')
    parser.add_argument('sectors', nargs='+', help='Sector name(s) to analyze (e.g., "Spinward Marches" "Trojan Reach")')
    parser.add_argument('-j', '--jump', type=int, default=2, help='Ship jump range (default: 2)')
    parser.add_argument('-c', '--cargo', type=int, default=64, help='Cargo capacity in tons (default: 64)')
    parser.add_argument('-n', '--num-circuits', type=int, default=10, help='Number of top circuits to display (default: 10)')
    parser.add_argument('--min-stops', type=int, default=3, help='Minimum stops in circuit (default: 3)')
    parser.add_argument('--max-stops', type=int, default=6, help='Maximum stops in circuit (default: 6)')
    parser.add_argument('--save', action='store_true', help='Save results to CSV files')
    
    args = parser.parse_args()
    
    try:
        optimizer = UniversalTradeCircuitOptimizer(
            sectors=args.sectors,
            jump_range=args.jump,
            cargo_tons=args.cargo
        )
        
        circuits = optimizer.generate_circuit_report(max_circuits=args.num_circuits)
        
        if args.save:
            optimizer.save_results(circuits)
        
        if circuits:
            print(f"\n{'='*80}")
            print("RECOMMENDATIONS:")
            print(f"Best circuit: {circuits[0]['total_profit']:,.0f} Cr profit")
            print(f"Start with: {circuits[0]['worlds'][0]} ({circuits[0]['hexes'][0]})")
            print(f"Complete circuit in {circuits[0]['total_distance']} parsecs")
            print(f"{'='*80}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
