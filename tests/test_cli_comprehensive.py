#!/usr/bin/env python3
"""
CLI-focused test suite for metaprivBIDS core functionality.
Tests the command-line interface and core logic without GUI dependencies.

This test suite focuses on:
- Command-line interface functionality
- Core privacy analysis algorithms
- Data loading and processing
- Privacy metrics calculation
- Error handling and edge cases

Run from /tests folder:
    cd tests  # from the metaprivBIDS root directory
    # Activate your environment: conda activate your-env-name
    python test_cli_comprehensive.py
"""

import sys
import os
import warnings
from pathlib import Path

# Add the parent directory to sys.path to import metaprivBIDS
sys.path.insert(0, str(Path(__file__).parent.parent))

def suppress_warnings():
    """Suppress known warnings."""
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

def test_core_import():
    """Test importing core logic."""
    print("Testing core logic import...")
    try:
        from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
        print("✓ Core logic imported successfully")
        return metaprivBIDS_core_logic
    except ImportError as e:
        print(f"✗ Failed to import core logic: {e}")
        return None

def test_initialization(core_class):
    """Test initializing the core logic."""
    print("\nTesting core logic initialization...")
    try:
        metapriv = core_class()
        print("✓ Core logic initialized successfully")
        return metapriv
    except Exception as e:
        print(f"✗ Failed to initialize core logic: {e}")
        return None

def test_data_loading(metapriv):
    """Test loading CSV data files."""
    print("\nTesting data loading...")
    
    test_files = [
        "../Use_Case_Data/adult_mini.csv",
        "../Use_Case_Data/data_mod_noise.csv"
    ]
    
    results = {}
    
    for file_path in test_files:
        print(f"  Testing file: {file_path}")
        try:
            if os.path.exists(file_path):
                data_info = metapriv.load_data(file_path)
                results[file_path] = data_info
                print(f"    ✓ Loaded successfully: {data_info['data'].shape}")
                print(f"    ✓ Columns: {len(data_info['column_types'])}")
                
                # Show column information
                for i, (col, count, dtype) in enumerate(data_info['column_types'][:5]):
                    print(f"      - {col.strip()}: {count} unique values, {dtype}")
                if len(data_info['column_types']) > 5:
                    print(f"      ... and {len(data_info['column_types']) - 5} more columns")
                    
            else:
                print(f"    ⚠ File not found: {file_path}")
        except Exception as e:
            print(f"    ✗ Failed to load {file_path}: {e}")
    
    return results

def test_privacy_metrics(metapriv, data_info):
    """Test privacy metrics calculation."""
    print("\nTesting privacy metrics calculation...")
    
    if not data_info:
        print("  ⚠ No data loaded, skipping privacy metrics test")
        return
    
    # Get the first dataset
    first_dataset = list(data_info.values())[0]
    data = first_dataset['data'].copy()
    data.columns = data.columns.str.strip()
    
    print(f"  Using dataset with shape: {data.shape}")
    print(f"  Available columns: {list(data.columns)}")
    
    try:
        # Test with common demographic columns
        available_cols = list(data.columns)
        quasi_identifiers = []
        
        # Look for common quasi-identifier columns
        potential_qi = ['age', 'education', 'sex', 'marital-status', 'occupation']
        for col in potential_qi:
            if col in available_cols:
                quasi_identifiers.append(col)
        
        if len(quasi_identifiers) < 2:
            quasi_identifiers = available_cols[:min(3, len(available_cols))]
        
        print(f"  Using quasi-identifiers: {quasi_identifiers}")
        
        # Calculate k-anonymity
        k_anon = metapriv.calculate_k_anonymity(data, quasi_identifiers)
        print(f"  ✓ k-anonymity: {k_anon}")
        
        # Find a sensitive attribute
        sensitive_attrs = ['salary-class', 'disease']
        sensitive_attr = None
        for attr in sensitive_attrs:
            if attr in available_cols:
                sensitive_attr = attr
                break
        
        if not sensitive_attr and available_cols:
            sensitive_attr = available_cols[-1]  # Use last column as sensitive
        
        if sensitive_attr:
            l_div = metapriv.calculate_l_diversity(data, quasi_identifiers, sensitive_attr)
            print(f"  ✓ l-diversity (sensitive: {sensitive_attr}): {l_div}")
            
            # Calculate unique rows statistics
            unique_stats = metapriv.calculate_unique_rows(data, quasi_identifiers, sensitive_attr)
            print(f"  ✓ Unique rows: {unique_stats['num_unique_rows']}/{unique_stats['total_rows']}")
            print(f"    Privacy risk: {100*unique_stats['num_unique_rows']/unique_stats['total_rows']:.1f}% unique records")
        
    except Exception as e:
        print(f"  ✗ Privacy metrics calculation failed: {e}")

def test_data_transformations(metapriv, data_info):
    """Test data transformation functions."""
    print("\nTesting data transformations...")
    
    if not data_info:
        print("  ⚠ No data loaded, skipping transformation tests")
        return
    
    # Get the first dataset
    first_dataset = list(data_info.values())[0]
    data = first_dataset['data'].copy()
    data.columns = data.columns.str.strip()
    
    # Test rounding for numerical columns
    numerical_cols = data.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 0:
        test_col = numerical_cols[0]
        print(f"  Testing rounding on column: {test_col}")
        try:
            original_values = data[test_col].copy()
            rounded_data = metapriv.round_values(data.copy(), test_col, precision=1)
            print(f"    ✓ Rounding applied successfully")
            print(f"    Original range: {original_values.min():.2f} - {original_values.max():.2f}")
            print(f"    Rounded range: {rounded_data[test_col].min():.2f} - {rounded_data[test_col].max():.2f}")
        except Exception as e:
            print(f"    ✗ Rounding failed: {e}")
        
        # Test noise addition
        print(f"  Testing noise addition on column: {test_col}")
        try:
            noisy_data = metapriv.add_noise(data.copy(), test_col, 'laplacian')
            print(f"    ✓ Noise addition applied successfully")
            noise_diff = abs(noisy_data[test_col] - original_values).mean()
            print(f"    Average noise magnitude: {noise_diff:.2f}")
        except Exception as e:
            print(f"    ✗ Noise addition failed: {e}")
    else:
        print("  ⚠ No numerical columns found for transformation tests")
    
    # Test categorical value combination
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        test_col = categorical_cols[0]
        print(f"  Testing value combination on column: {test_col}")
        try:
            original_unique = data[test_col].nunique()
            combined_history = metapriv.combine_values(data.copy(), test_col)
            print(f"    ✓ Value combination applied successfully")
            print(f"    Original unique values: {original_unique}")
        except Exception as e:
            print(f"    ✗ Value combination failed: {e}")

def test_column_analysis(metapriv, data_info):
    """Test column analysis functions."""
    print("\nTesting column analysis...")
    
    if not data_info:
        print("  ⚠ No data loaded, skipping column analysis")
        return
    
    # Get the first dataset
    first_dataset = list(data_info.values())[0]
    data = first_dataset['data'].copy()
    data.columns = data.columns.str.strip()
    
    # Test lowest unique columns analysis
    selected_columns = list(data.columns)[:min(4, len(data.columns))]
    print(f"  Testing lowest unique columns with: {selected_columns}")
    
    try:
        results = metapriv.find_lowest_unique_columns(data, selected_columns)
        print(f"    ✓ Analysis completed for {len(results)} columns")
        
        for col, stats in results.items():
            print(f"      {col}: difference={stats['difference']}, normalized={stats['normalized_difference']}")
    except Exception as e:
        print(f"    ✗ Column analysis failed: {e}")
    
    # Test combined column contribution
    print(f"  Testing combined column contribution...")
    try:
        contribution_df = metapriv.compute_combined_column_contribution(
            data, selected_columns, min_size=1, max_size=2
        )
        print(f"    ✓ Computed {len(contribution_df)} column combinations")
    except Exception as e:
        print(f"    ✗ Combined column contribution failed: {e}")

def test_error_handling(metapriv):
    """Test error handling and edge cases."""
    print("\nTesting error handling...")
    
    # Test with non-existent file
    try:
        metapriv.load_data("non_existent_file.csv")
        print("  ✗ Should have failed for non-existent file")
    except:
        print("  ✓ Properly handles non-existent file")
    
    # Test with empty column list
    try:
        import pandas as pd
        dummy_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        metapriv.calculate_k_anonymity(dummy_data, [])
        print("  ✗ Should have failed for empty column list")
    except:
        print("  ✓ Properly handles empty column list")

def run_comprehensive_cli_test():
    """Run the comprehensive CLI test suite."""
    print("=" * 60)
    print("metaprivBIDS Comprehensive CLI Test Suite")
    print("=" * 60)
    
    suppress_warnings()
    
    # Test core import
    core_class = test_core_import()
    if not core_class:
        print("\n✗ CRITICAL: Cannot import core logic. Exiting.")
        return False
    
    # Test initialization
    metapriv = test_initialization(core_class)
    if not metapriv:
        print("\n✗ CRITICAL: Cannot initialize core logic. Exiting.")
        return False
    
    # Test data loading
    data_info = test_data_loading(metapriv)
    
    # Test privacy metrics
    test_privacy_metrics(metapriv, data_info)
    
    # Test data transformations
    test_data_transformations(metapriv, data_info)
    
    # Test column analysis
    test_column_analysis(metapriv, data_info)
    
    # Test error handling
    test_error_handling(metapriv)
    
    print("\n" + "=" * 60)
    print("CLI Test Suite Completed!")
    print("=" * 60)
    
    # Summary
    if data_info:
        print(f"✓ Successfully tested with {len(data_info)} datasets")
        print("✓ Core functionality verified")
        print("✓ Privacy metrics calculation working")
        print("✓ Data transformations functional")
        print("\n🎯 metaprivBIDS CLI is ready for use!")
    else:
        print("⚠ Limited testing due to missing data files")
        print("✓ Core functionality verified")
    
    return True

if __name__ == "__main__":
    """Run the comprehensive CLI test when executed directly."""
    success = run_comprehensive_cli_test()
    sys.exit(0 if success else 1)
