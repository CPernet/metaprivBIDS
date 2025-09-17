#!/usr/bin/env python3
"""
Simple CLI demonstration of metaprivBIDS functionality using CSV data.
This script shows how to use the core functionality without GUI dependencies.

Usage:
    cd /path/to/metaprivBIDS/tests
    # Activate your environment
    python demo_cli_usage.py
"""

import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("=" * 60)
    print("metaprivBIDS CLI Demonstration")
    print("=" * 60)
    
    try:
        from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
        print("✓ Successfully imported metaprivBIDS core logic")
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        print("Please ensure metaprivBIDS is installed: python install.py")
        return False
    
    # Initialize the core logic
    mp = metaprivBIDS_core_logic()
    print("✓ Core logic initialized")
    
    # Path to CSV data
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'Use_Case_Data', 'adult_mini.csv')
    
    if not os.path.exists(csv_path):
        print(f"✗ CSV file not found: {csv_path}")
        return False
    
    print(f"✓ Found CSV data: {os.path.basename(csv_path)}")
    
    # Load the data
    print("\n" + "-" * 40)
    print("Loading and Analyzing Data")
    print("-" * 40)
    
    data_info = mp.load_data(csv_path)
    data = data_info['data']
    
    print(f"Dataset shape: {data.shape[0]} rows × {data.shape[1]} columns")
    print(f"Columns: {', '.join(data.columns[:5])}{'...' if len(data.columns) > 5 else ''}")
    
    # Display column types
    print("\nColumn Analysis:")
    for col, count, col_type in data_info['column_types'][:8]:
        print(f"  {col:20} {count:3d} unique values  ({col_type})")
    
    # Privacy Analysis
    print("\n" + "-" * 40)
    print("Privacy Analysis")
    print("-" * 40)
    
    # Test different column combinations
    test_scenarios = [
        {
            'name': 'Basic Demographics',
            'columns': ['age', 'sex', 'education'],
            'sensitive': 'salary-class'
        },
        {
            'name': 'Extended Demographics', 
            'columns': ['age', 'sex', 'education', 'marital-status'],
            'sensitive': 'salary-class'
        },
        {
            'name': 'Health + Demographics',
            'columns': ['age', 'sex', 'disease'],
            'sensitive': 'salary-class'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Quasi-identifiers: {', '.join(scenario['columns'])}")
        print(f"Sensitive attribute: {scenario['sensitive']}")
        
        try:
            # Calculate privacy metrics
            stats = mp.calculate_unique_rows(
                data, 
                scenario['columns'], 
                scenario['sensitive']
            )
            
            print(f"  k-anonymity: {stats['k_anonymity']}")
            print(f"  ℓ-diversity: {stats['l_diversity']}")
            print(f"  Unique rows: {stats['num_unique_rows']}/{stats['total_rows']} ({stats['num_unique_rows']/stats['total_rows']*100:.1f}%)")
            
            # Risk assessment
            if stats['k_anonymity'] == 1:
                risk_level = "HIGH RISK"
            elif stats['k_anonymity'] < 5:
                risk_level = "MEDIUM RISK"
            else:
                risk_level = "LOW RISK"
            
            print(f"  Privacy risk: {risk_level}")
            
        except Exception as e:
            print(f"  Error calculating metrics: {e}")
    
    # Column Contribution Analysis
    print("\n" + "-" * 40)
    print("Column Contribution Analysis")
    print("-" * 40)
    
    analysis_columns = ['age', 'sex', 'education', 'marital-status']
    print(f"Analyzing contribution of: {', '.join(analysis_columns)}")
    
    try:
        contribution_results = mp.find_lowest_unique_columns(data, analysis_columns)
        
        print("\nColumn impact on uniqueness:")
        for col, results in contribution_results.items():
            print(f"  {col:15} removes {results['difference']:3d} unique rows (norm: {results['normalized_difference']:.2f})")
        
        # Find most contributing column
        max_contrib = max(contribution_results.items(), key=lambda x: x[1]['difference'])
        print(f"\nMost contributing column: {max_contrib[0]} ({max_contrib[1]['difference']} unique rows)")
        
    except Exception as e:
        print(f"Error in contribution analysis: {e}")
    
    # Data Transformation Demo
    print("\n" + "-" * 40)
    print("Data Transformation Demo")
    print("-" * 40)
    
    print("Original age distribution:")
    print(f"  Min: {data['age'].min()}, Max: {data['age'].max()}, Mean: {data['age'].mean():.1f}")
    
    # Test rounding
    try:
        rounded_data = mp.round_values(data.copy(), 'age', precision=1)
        print("After rounding to nearest 10:")
        print(f"  Min: {rounded_data['age'].min()}, Max: {rounded_data['age'].max()}, Mean: {rounded_data['age'].mean():.1f}")
        print(f"  Unique ages reduced from {data['age'].nunique()} to {rounded_data['age'].nunique()}")
    except Exception as e:
        print(f"Error in rounding: {e}")
    
    print("\n" + "=" * 60)
    print("✓ CLI demonstration completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Examine the CSV data files in Use_Case_Data/")
    print("2. Run the comprehensive tests: python -m pytest test_csv_data_processing_clean.py -v")
    print("3. Explore the core logic functions in your own scripts")
    print("4. Refer to TEST_EXECUTION_SUMMARY.md for detailed results")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
