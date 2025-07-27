#!/usr/bin/env python3
"""
Trojan Reach Trade Route Optimizer
Analyzes optimal trade routes for a Jump-2 ship with 100 tons cargo capacity
"""

import pandas as pd
import numpy as np
from pathlib import Path
import math
from itertools import combinations
from typing import List, Dict, Tuple

class TrojanReachTradeOptimizer:
    """Optimize trade routes in the Trojan Reach sector"""
    
    def __init__(self):
        self.worlds_df = None
        self.load_data()
        
    def load_data(self):
        """Load the economic data"""
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
        # Filter for Trojan Reach worlds only
        self.worlds_df = df[df['Sector'] == 'Trojan Reach'].copy()
        
        # Parse hex coordinates for distance calculations
        self.worlds_df['Hex'] = self.worlds_df['Hex'].astype(str).str.zfill(4)  # Ensure 4-digit format
        self.worlds_df['hex_x'] = self.worlds_df['Hex'].str[:2].astype(int)
        self.worlds_df['hex_y'] = self.worlds_df['Hex'].str[2:].astype(int)
        
        print(f"Loaded {len(self.worlds_df)} worlds in Trojan Reach")
        
    def calculate_distance(self, hex1: str, hex2: str) -> float:
        """Calculate hex distance between two worlds"""
        hex1_str = str(hex1).zfill(4)  # Ensure 4 characters with leading zeros
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
        
        # Handle the case where trade_codes might be a string representation of a list
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
            
        return {'exports': list(set(exports)), 'imports': list(set(imports))}
    
    def calculate_trade_profit(self, origin: pd.Series, destination: pd.Series) -> Dict:
        """Calculate potential profit for trade between two worlds"""
        try:
            origin_trade = self.classify_trade_goods(origin)
            dest_trade = self.classify_trade_goods(destination)
            
            # Find matching trade opportunities (origin exports match destination imports)
            matches = set(origin_trade['exports']).intersection(set(dest_trade['imports']))
            
            if not matches:
                return {'profit_per_ton': 0, 'goods': [], 'viable': False, 'distance': 0, 'multiplier': 0}
            
            # Base profit calculation factors
            starport_bonus = {4: 1.4, 3: 1.2, 2: 1.0, 1: 0.8, 0: 0.6, -1: 0.4}  # A to X starports
            
            origin_bonus = starport_bonus.get(origin.get('StarportScore', 0), 0.6)
            dest_bonus = starport_bonus.get(destination.get('StarportScore', 0), 0.6)
            
            # Population factors (higher pop = better markets)
            pop_factor = min(2.0, (destination.get('PopulationExp', 0) / 6.0))
            
            # Resource Unit factor (economic strength)
            economic_factor = min(2.0, (destination.get('ResourceUnits', 0) / 500.0))
            
            # Distance penalty (closer is better)
            distance = self.calculate_distance(origin['Hex'], destination['Hex'])
            distance_penalty = max(0.5, (1.0 - (distance * 0.1)))
            
            # Calculate base profit per ton
            base_profit = 1000  # Base Cr 1000 per ton
            profit_multiplier = origin_bonus * dest_bonus * pop_factor * economic_factor * distance_penalty
            
            profit_per_ton = base_profit * profit_multiplier
            
            # Special bonuses for specific trade combinations
            bonus_trades = {
                ('Ag', 'Hi'): 1.5,  # Food to high pop
                ('In', 'Po'): 1.4,  # Manufactured goods to poor worlds
                ('Ri', 'Hi'): 1.6,  # Luxury goods to rich, high pop
                ('De', 'Ag'): 1.3,  # Minerals to agricultural
                ('Ic', 'De'): 1.4,  # Water to desert worlds
            }
            
            # Get trade codes properly
            origin_codes = origin['TradeCodes']
            dest_codes = destination['TradeCodes']
            
            # Ensure they are lists
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
                'viable': len(matches) > 0 and profit_per_ton > 500,
                'distance': distance,
                'multiplier': profit_multiplier
            }
            
        except Exception as e:
            print(f"Error in profit calculation for {origin.get('Name', 'Unknown')} -> {destination.get('Name', 'Unknown')}: {e}")
            return {'profit_per_ton': 0, 'goods': [], 'viable': False, 'distance': 0, 'multiplier': 0}
    
    def find_jump2_routes(self) -> List[Dict]:
        """Find all viable Jump-2 trade routes"""
        viable_routes = []
        
        for i, origin in self.worlds_df.iterrows():
            for j, destination in self.worlds_df.iterrows():
                if i >= j:  # Avoid duplicates and self-trades
                    continue
                    
                distance = self.calculate_distance(origin['Hex'], destination['Hex'])
                
                # Only consider Jump-2 or less routes
                if distance <= 2:
                    # Calculate profit in both directions
                    profit_a_to_b = self.calculate_trade_profit(origin, destination)
                    profit_b_to_a = self.calculate_trade_profit(destination, origin)
                    
                    if profit_a_to_b['viable'] or profit_b_to_a['viable']:
                        route = {
                            'origin': origin['Name'],
                            'origin_hex': origin['Hex'],
                            'origin_starport': origin['Starport'],
                            'origin_codes': origin['TradeCodes'],
                            'destination': destination['Name'],
                            'dest_hex': destination['Hex'],
                            'dest_starport': destination['Starport'],
                            'dest_codes': destination['TradeCodes'],
                            'distance': distance,
                            'profit_a_to_b': profit_a_to_b['profit_per_ton'],
                            'goods_a_to_b': profit_a_to_b['goods'],
                            'profit_b_to_a': profit_b_to_a['profit_per_ton'],
                            'goods_b_to_a': profit_b_to_a['goods'],
                            'round_trip_profit': profit_a_to_b['profit_per_ton'] + profit_b_to_a['profit_per_ton'],
                            'viable_a_to_b': profit_a_to_b['viable'],
                            'viable_b_to_a': profit_b_to_a['viable']
                        }
                        viable_routes.append(route)
        
        return sorted(viable_routes, key=lambda x: x['round_trip_profit'], reverse=True)
    
    def find_optimal_circuit(self, max_stops: int = 4) -> List[Dict]:
        """Find optimal multi-stop trading circuit"""
        # Get high-value worlds for circuit analysis
        high_value_worlds = self.worlds_df[
            (self.worlds_df['ResourceUnits'] > 100) | 
            (self.worlds_df['IsRi'] == 1) | 
            (self.worlds_df['IsHi'] == 1) |
            (self.worlds_df['IsAg'] == 1) |
            (self.worlds_df['IsIn'] == 1)
        ].copy()
        
        print(f"Analyzing circuits with {len(high_value_worlds)} high-value worlds...")
        
        best_circuits = []
        
        # Try different circuit lengths
        for circuit_length in range(3, min(max_stops + 1, len(high_value_worlds))):
            for world_combo in combinations(high_value_worlds.iterrows(), circuit_length):
                worlds = [w[1] for w in world_combo]  # Extract the Series objects
                
                # Check if all jumps in circuit are <= 2
                circuit_valid = True
                total_distance = 0
                circuit_profit = 0
                
                for i in range(len(worlds)):
                    current = worlds[i]
                    next_world = worlds[(i + 1) % len(worlds)]  # Wrap around for circuit
                    
                    distance = self.calculate_distance(current['Hex'], next_world['Hex'])
                    if distance > 2:
                        circuit_valid = False
                        break
                    
                    total_distance += distance
                    
                    # Calculate profit for this leg
                    trade_result = self.calculate_trade_profit(current, next_world)
                    if trade_result['viable']:
                        circuit_profit += trade_result['profit_per_ton']
                
                if circuit_valid and circuit_profit > 2000:  # Minimum viable circuit profit
                    circuit = {
                        'worlds': [w['Name'] for w in worlds],
                        'hexes': [w['Hex'] for w in worlds],
                        'starports': [w['Starport'] for w in worlds],
                        'total_distance': total_distance,
                        'total_profit': circuit_profit,
                        'profit_per_jump': circuit_profit / len(worlds),
                        'circuit_length': len(worlds)
                    }
                    best_circuits.append(circuit)
        
        return sorted(best_circuits, key=lambda x: x['total_profit'], reverse=True)[:10]
    
    def generate_trade_report(self):
        """Generate comprehensive trade route report"""
        print("=" * 80)
        print("TROJAN REACH OPTIMAL TRADE ROUTES")
        print("=" * 80)
        print("Ship Configuration: Jump-2, 100 tons cargo capacity")
        print("Analysis Date: 2025 (Milieu 1105)")
        print()
        
        # Find best bilateral routes
        print("TOP 10 BILATERAL TRADE ROUTES")
        print("-" * 50)
        
        try:
            routes = self.find_jump2_routes()
            print(f"Found {len(routes)} viable routes")
        except Exception as e:
            print(f"Error finding routes: {e}")
            import traceback
            traceback.print_exc()
            return None, None
        
        for i, route in enumerate(routes[:10]):
            print(f"\n{i+1}. {route['origin']} ({route['origin_hex']}) ↔ {route['destination']} ({route['dest_hex']})")
            print(f"   Distance: {route['distance']} parsecs")
            print(f"   Starports: {route['origin_starport']} → {route['dest_starport']}")
            
            if route['viable_a_to_b']:
                print(f"   {route['origin']} → {route['destination']}: Cr {route['profit_a_to_b']:.0f}/ton")
                print(f"     Goods: {', '.join(route['goods_a_to_b'][:3])}...")
                
            if route['viable_b_to_a']:
                print(f"   {route['destination']} → {route['origin']}: Cr {route['profit_b_to_a']:.0f}/ton")
                print(f"     Goods: {', '.join(route['goods_b_to_a'][:3])}...")
                
            total_cargo_profit = route['round_trip_profit'] * 100  # 100 tons
            print(f"   Round-trip profit (100 tons): Cr {total_cargo_profit:,.0f}")
        
        # Find best circuits
        print("\n\nTOP 5 TRADING CIRCUITS")
        print("-" * 50)
        circuits = self.find_optimal_circuit()
        
        for i, circuit in enumerate(circuits[:5]):
            print(f"\n{i+1}. Circuit: {' → '.join(circuit['worlds'])} → {circuit['worlds'][0]}")
            print(f"   Hexes: {' → '.join(circuit['hexes'])}")
            print(f"   Starports: {' → '.join(circuit['starports'])}")
            print(f"   Total Distance: {circuit['total_distance']} parsecs")
            print(f"   Total Profit: Cr {circuit['total_profit']:.0f}/ton")
            print(f"   With 100 tons: Cr {circuit['total_profit'] * 100:,.0f} per circuit")
            print(f"   Profit per jump: Cr {circuit['profit_per_jump']:.0f}/ton")
        
        # Specific world analysis
        print("\n\nKEY TRADING HUBS IN TROJAN REACH")
        print("-" * 50)
        
        # Identify best trading hubs based on connections and profitability
        hub_analysis = {}
        for route in routes:
            for world in [route['origin'], route['destination']]:
                if world not in hub_analysis:
                    hub_analysis[world] = {'connections': 0, 'total_profit': 0}
                hub_analysis[world]['connections'] += 1
                hub_analysis[world]['total_profit'] += route['round_trip_profit']
        
        best_hubs = sorted(hub_analysis.items(), 
                          key=lambda x: x[1]['connections'] * x[1]['total_profit'], 
                          reverse=True)
        
        for i, (world, data) in enumerate(best_hubs[:5]):
            world_data = self.worlds_df[self.worlds_df['Name'] == world].iloc[0]
            print(f"\n{i+1}. {world} ({world_data['Hex']})")
            print(f"   Starport: {world_data['Starport']} | Population: 10^{world_data['PopulationExp']}")
            print(f"   Trade Codes: {world_data['TradeCodes']}")
            print(f"   Connections: {data['connections']} routes")
            print(f"   Average profit per route: Cr {data['total_profit']/data['connections']:.0f}/ton")
        
        # Trading strategy recommendations
        print("\n\nTRADING STRATEGY RECOMMENDATIONS")
        print("-" * 50)
        print("\n1. QUICK PROFIT ROUTES (1-2 jumps):")
        
        quick_routes = [r for r in routes[:3] if r['distance'] <= 1]
        if not quick_routes:
            quick_routes = routes[:3]
            
        for route in quick_routes:
            print(f"   • {route['origin']} ↔ {route['destination']} ({route['distance']} parsec)")
            print(f"     Potential: Cr {route['round_trip_profit'] * 100:,.0f} per round trip")
        
        print("\n2. LONG-TERM CIRCUITS (3-4 stops):")
        for circuit in circuits[:2]:
            print(f"   • {len(circuit['worlds'])}-stop circuit: {' → '.join(circuit['worlds'])}")
            print(f"     Potential: Cr {circuit['total_profit'] * 100:,.0f} per complete circuit")
        
        print("\n3. SPECIALIZED TRADING OPPORTUNITIES:")
        
        # Find specialty trade opportunities
        ag_worlds = self.worlds_df[self.worlds_df['IsAg'] == 1]
        hi_worlds = self.worlds_df[self.worlds_df['IsHi'] == 1]
        
        if len(ag_worlds) > 0 and len(hi_worlds) > 0:
            print("   • Food Trading: Agricultural worlds → High population worlds")
            for ag_world in ag_worlds.head(2).iterrows():
                ag_data = ag_world[1]
                nearby_hi = []
                for hi_world in hi_worlds.iterrows():
                    hi_data = hi_world[1]
                    distance = self.calculate_distance(ag_data['Hex'], hi_data['Hex'])
                    if distance <= 2:
                        nearby_hi.append((hi_data['Name'], distance))
                
                if nearby_hi:
                    print(f"     {ag_data['Name']} → {nearby_hi[0][0]} ({nearby_hi[0][1]} parsecs)")
        
        return routes, circuits

def main():
    """Run the trade route analysis"""
    try:
        optimizer = TrojanReachTradeOptimizer()
        routes, circuits = optimizer.generate_trade_report()
        
        # Save detailed results
        routes_df = pd.DataFrame(routes)
        circuits_df = pd.DataFrame(circuits)
        
        routes_df.to_csv('output/trojan_reach_trade_routes.csv', index=False)
        circuits_df.to_csv('output/trojan_reach_circuits.csv', index=False)
        
        print(f"\n\nDetailed results saved to:")
        print("- output/trojan_reach_trade_routes.csv")
        print("- output/trojan_reach_circuits.csv")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to run the economic analysis first: python3 run_analysis.py")

if __name__ == "__main__":
    main()
