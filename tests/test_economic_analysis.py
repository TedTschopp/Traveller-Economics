"""
Unit tests for Traveller Economic Analysis
==========================================

Test suite for validating economic calculations and data processing.
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traveller_economics import EconomicCalculator, WorldDataProcessor, EconomicConfig

class TestEconomicCalculator(unittest.TestCase):
    """Test economic calculation functions"""
    
    def setUp(self):
        self.calculator = EconomicCalculator()
    
    def test_ehex_to_decimal(self):
        """Test extended hex to decimal conversion"""
        self.assertEqual(self.calculator.ehex_to_decimal('0'), 0)
        self.assertEqual(self.calculator.ehex_to_decimal('9'), 9)
        self.assertEqual(self.calculator.ehex_to_decimal('A'), 10)
        self.assertEqual(self.calculator.ehex_to_decimal('G'), 16)
        self.assertEqual(self.calculator.ehex_to_decimal('X'), 33)
    
    def test_parse_uwp(self):
        """Test UWP parsing"""
        uwp = "A867A95-D"
        result = self.calculator.parse_uwp(uwp)
        
        self.assertEqual(result['starport'], 'A')
        self.assertEqual(result['size'], '8')
        self.assertEqual(result['atmosphere'], '6')
        self.assertEqual(result['hydrosphere'], '7')
        self.assertEqual(result['population_exp'], 10)  # A = 10
        self.assertEqual(result['government'], '9')
        self.assertEqual(result['law_level'], '5')
    
    def test_parse_economic_extension(self):
        """Test economic extension parsing"""
        # Test standard format
        ex = "(D7E+5)"
        result = self.calculator.parse_economic_extension(ex)
        
        self.assertEqual(result['resources'], 13)  # D = 13
        self.assertEqual(result['labor'], 7)
        self.assertEqual(result['infrastructure'], 14)  # E = 14
        self.assertEqual(result['efficiency'], 5)
        
        # Test negative efficiency
        ex_neg = "(A5C-2)"
        result_neg = self.calculator.parse_economic_extension(ex_neg)
        self.assertEqual(result_neg['efficiency'], -2)
    
    def test_calculate_resource_units(self):
        """Test RU calculation"""
        # Test basic calculation
        economic_ext = {
            "resources": 10,
            "labor": 5,
            "infrastructure": 8,
            "efficiency": 0
        }
        ru = self.calculator.calculate_resource_units(economic_ext)
        self.assertEqual(ru, 400)  # 10 * 5 * 8
        
        # Test with positive efficiency
        economic_ext['efficiency'] = 5
        ru_pos = self.calculator.calculate_resource_units(economic_ext)
        self.assertEqual(ru_pos, 600)  # 400 * 1.5
        
        # Test with negative efficiency
        economic_ext['efficiency'] = -3
        ru_neg = self.calculator.calculate_resource_units(economic_ext)
        self.assertAlmostEqual(ru_neg, 307.69, places=2)  # 400 / 1.3
    
    def test_parse_trade_codes(self):
        """Test trade code parsing"""
        remarks = "Ag Ri Hi"
        codes = self.calculator.parse_trade_codes(remarks)
        self.assertEqual(codes, ['Ag', 'Ri', 'Hi'])
        
        # Test empty/null remarks
        self.assertEqual(self.calculator.parse_trade_codes(""), [])
        self.assertEqual(self.calculator.parse_trade_codes(pd.NA), [])
    
    def test_calculate_population(self):
        """Test population calculation"""
        self.assertEqual(self.calculator.calculate_population(0), 1)
        self.assertEqual(self.calculator.calculate_population(6), 1000000)
        self.assertEqual(self.calculator.calculate_population(9), 1000000000)

class TestWorldDataProcessor(unittest.TestCase):
    """Test world data processing"""
    
    def setUp(self):
        self.config = EconomicConfig()
        self.processor = WorldDataProcessor(self.config)
    
    def test_parse_sector_data(self):
        """Test parsing of tab-delimited sector data"""
        # Mock sector data
        test_data = """# Test sector data
Name	Hex	UWP	Remarks	Ex	Allegiance
Mora	3124	A867A95-D	Ag Ri Hi	(D7E+5)	ImDd
Regina	1910	A788899-C	Ag Ri	(C6D+2)	ImDd
Efate	1705	A646930-D	Hi In	(B8F+4)	ImDd"""
        
        df = self.processor.parse_sector_data("Test Sector", test_data)
        
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[0]['Name'], 'Mora')
        self.assertEqual(df.iloc[0]['Sector'], 'Test Sector')
        self.assertTrue('UWP' in df.columns)
    
    def test_enrich_world_data(self):
        """Test world data enrichment"""
        # Create test dataframe
        test_df = pd.DataFrame({
            'Name': ['Mora', 'Regina'],
            'UWP': ['A867A95-D', 'A788899-C'],
            'Remarks': ['Ag Ri Hi', 'Ag Ri'],
            'Ex': ['(D7E+5)', '(C6D+2)'],
            'Allegiance': ['ImDd', 'ImDd'],
            'Sector': ['Test', 'Test']
        })
        
        enriched_df = self.processor.enrich_world_data(test_df)
        
        # Check if new columns were added
        expected_columns = ['Starport', 'PopulationExp', 'Population', 'ResourceUnits', 
                          'Resources', 'Labor', 'Infrastructure', 'Efficiency',
                          'TradeCodes', 'StarportScore', 'IsAg', 'IsIn', 'IsRi']
        
        for col in expected_columns:
            self.assertIn(col, enriched_df.columns)
        
        # Check specific calculations
        self.assertEqual(enriched_df.iloc[0]['Starport'], 'A')
        self.assertEqual(enriched_df.iloc[0]['PopulationExp'], 10)  # A
        self.assertEqual(enriched_df.iloc[0]['Population'], 10**10)
        self.assertTrue(enriched_df.iloc[0]['IsAg'])
        self.assertTrue(enriched_df.iloc[0]['IsRi'])
    
    def test_imperium_filtering(self):
        """Test filtering to Imperium worlds only"""
        test_df = pd.DataFrame({
            'Name': ['Imperial World', 'Zhodani World', 'Independent'],
            'Allegiance': ['ImDd', 'ZhCo', 'In'],
            'UWP': ['A788899-C', 'B567788-9', 'C445566-7'],
            'Remarks': ['', '', ''],
            'Ex': ['(C6D+2)', '(B5C+1)', '(A4B+0)'],
            'Sector': ['Test', 'Test', 'Test']
        })
        
        enriched_df = self.processor.enrich_world_data(test_df)
        
        # Should only have the Imperial world
        self.assertEqual(len(enriched_df), 1)
        self.assertEqual(enriched_df.iloc[0]['Name'], 'Imperial World')

class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def setUp(self):
        self.calculator = EconomicCalculator()
    
    def test_invalid_uwp_handling(self):
        """Test handling of invalid UWP strings"""
        # Too short UWP
        result = self.calculator.parse_uwp("A78")
        self.assertEqual(result['starport'], 'X')
        self.assertEqual(result['population_exp'], 0)
        
        # Empty UWP
        result = self.calculator.parse_uwp("")
        self.assertEqual(result['starport'], 'X')
    
    def test_invalid_economic_extension(self):
        """Test handling of malformed economic extensions"""
        # Invalid format
        result = self.calculator.parse_economic_extension("Invalid")
        self.assertEqual(result['resources'], 1)
        self.assertEqual(result['labor'], 1)
        self.assertEqual(result['infrastructure'], 1)
        self.assertEqual(result['efficiency'], 0)
        
        # Empty string
        result = self.calculator.parse_economic_extension("")
        self.assertEqual(result['resources'], 1)
    
    def test_zero_values_handling(self):
        """Test handling of zero values in calculations"""
        # Economic extension with zeros
        ex_with_zeros = {
            "resources": 0,
            "labor": 0, 
            "infrastructure": 0,
            "efficiency": 0
        }
        
        # Should convert zeros to 1s for R, L, I
        ru = self.calculator.calculate_resource_units(ex_with_zeros)
        self.assertEqual(ru, 1)  # 1 * 1 * 1

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [TestEconomicCalculator, TestWorldDataProcessor, TestDataValidation]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
