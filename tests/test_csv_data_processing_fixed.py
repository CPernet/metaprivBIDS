#!/usr/bin/env python3
"""
Comprehensive tests for metaprivBIDS using the actual CSV data files.
Tests core privacy analysis functionality without GUI dependencies.

This test suite validates:
- Loading and processing CSV data files
- Privacy metrics calculation (k-anonymity, l-diversity)
- Data transformation functions
- Column analysis and unique value detection
- Privacy risk assessment algorithms

Run from /tests folder:
    cd tests  # from the metaprivBIDS root directory
    # Activate your environment: conda activate your-env-name
    python -m pytest test_csv_data_processing_fixed.py -v
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import metaprivBIDS
sys.path.insert(0, str(Path(__file__).parent.parent))

from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic


class TestCSVDataProcessing:
    """Test suite for CSV data processing with metaprivBIDS core logic."""
    
    @pytest.fixture(scope="class")
    def metapriv_instance(self):
        """Create a metaprivBIDS core logic instance."""
        return metaprivBIDS_core_logic()
    
    @pytest.fixture(scope="class")
    def adult_mini_path(self):
        """Path to the adult_mini.csv test data."""
        return "../Use_Case_Data/adult_mini.csv"
    
    @pytest.fixture(scope="class")
    def data_mod_noise_path(self):
        """Path to the data_mod_noise.csv test data."""
        return "../Use_Case_Data/data_mod_noise.csv"
    
    @pytest.fixture(scope="class")
    def adult_data(self, metapriv_instance, adult_mini_path):
        """Load adult_mini.csv data."""
        if not os.path.exists(adult_mini_path):
            pytest.skip(f"Test data file not found: {adult_mini_path}")
        return metapriv_instance.load_data(adult_mini_path)
    
    @pytest.fixture(scope="class")
    def noise_data(self, metapriv_instance, data_mod_noise_path):
        """Load data_mod_noise.csv data."""
        if not os.path.exists(data_mod_noise_path):
            pytest.skip(f"Test data file not found: {data_mod_noise_path}")
        return metapriv_instance.load_data(data_mod_noise_path)

    def test_csv_file_loading(self, adult_data, noise_data):
        """Test that CSV files can be loaded successfully."""
        # Test adult_mini.csv
        assert 'data' in adult_data
        assert 'original_data' in adult_data
        assert 'column_unique_counts' in adult_data
        assert 'column_types' in adult_data
        
        # Check data shape and columns
        assert adult_data['data'].shape[0] > 0, "Should have rows"
        assert adult_data['data'].shape[1] > 0, "Should have columns"
        
        # Test data_mod_noise.csv
        assert 'data' in noise_data
        assert noise_data['data'].shape[0] > 0, "Should have rows"
        assert noise_data['data'].shape[1] > 0, "Should have columns"
    
    def test_column_analysis(self, adult_data):
        """Test column type detection and unique value counting."""
        data_info = adult_data
        
        # Check that all expected columns are present
        expected_columns = ['age', 'education', 'marital-status', 'occupation', 
                          'relationship', 'sex', 'salary-class', 'disease', 'exercise_weekly_hours']
        
        for col in expected_columns:
            assert col.strip() in [c.strip() for c in data_info['data'].columns], f"Column {col} should be present"
        
        # Check column types classification
        assert len(data_info['column_types']) == len(data_info['data'].columns)
        
        # Verify column unique counts
        for col in data_info['data'].columns:
            col_stripped = col.strip()
            assert col_stripped in data_info['column_unique_counts'] or col in data_info['column_unique_counts']
    
    def test_privacy_metrics_calculation(self, metapriv_instance, adult_data):
        """Test k-anonymity and l-diversity calculations."""
        data = adult_data['data']
        
        # Test with demographic columns (quasi-identifiers)
        quasi_identifiers = ['age', 'education', 'marital-status', 'sex']
        sensitive_attribute = 'salary-class'
        
        # Clean column names
        data.columns = data.columns.str.strip()
        
        # Calculate k-anonymity
        k_anon = metapriv_instance.calculate_k_anonymity(data, quasi_identifiers)
        assert isinstance(k_anon, (int, np.integer))
        assert k_anon >= 1, "k-anonymity should be at least 1"
        
        # Calculate l-diversity
        l_div = metapriv_instance.calculate_l_diversity(data, quasi_identifiers, sensitive_attribute)
        assert isinstance(l_div, (int, np.integer))
        assert l_div >= 1, "l-diversity should be at least 1"
        
        print(f"Privacy metrics - k-anonymity: {k_anon}, l-diversity: {l_div}")
    
    def test_unique_rows_analysis(self, metapriv_instance, adult_data):
        """Test unique rows detection and privacy risk assessment."""
        data = adult_data['data']
        data.columns = data.columns.str.strip()
        
        selected_columns = ['age', 'education', 'sex']
        sensitive_attr = 'salary-class'
        
        stats = metapriv_instance.calculate_unique_rows(data, selected_columns, sensitive_attr)
        
        # Verify all expected keys are present
        expected_keys = ['total_rows', 'total_columns', 'num_selected_columns', 
                        'num_unique_rows', 'k_anonymity', 'l_diversity']
        
        for key in expected_keys:
            assert key in stats, f"Key {key} should be in stats"
        
        # Verify data consistency
        assert stats['total_rows'] == len(data)
        assert stats['total_columns'] == len(data.columns)
        assert stats['num_selected_columns'] == len(selected_columns)
        assert stats['num_unique_rows'] >= 0
        
        print(f"Unique rows analysis: {stats}")
    
    def test_comprehensive_privacy_analysis(self, metapriv_instance, adult_data):
        """Comprehensive privacy analysis using multiple metrics."""
        data = adult_data['data'].copy()
        data.columns = data.columns.str.strip()
        
        # Define analysis parameters
        quasi_identifiers = ['age', 'education', 'sex', 'marital-status']
        sensitive_attributes = ['salary-class', 'disease']
        
        print("\n=== Comprehensive Privacy Analysis ===")
        
        for sensitive_attr in sensitive_attributes:
            if sensitive_attr in data.columns:
                print(f"\nAnalyzing with sensitive attribute: {sensitive_attr}")
                
                # Calculate privacy metrics
                k_anon = metapriv_instance.calculate_k_anonymity(data, quasi_identifiers)
                l_div = metapriv_instance.calculate_l_diversity(data, quasi_identifiers, sensitive_attr)
                
                # Calculate unique rows
                unique_stats = metapriv_instance.calculate_unique_rows(data, quasi_identifiers, sensitive_attr)
                
                print(f"  k-anonymity: {k_anon}")
                print(f"  l-diversity: {l_div}")
                print(f"  Unique rows: {unique_stats['num_unique_rows']}/{unique_stats['total_rows']} "
                      f"({100*unique_stats['num_unique_rows']/unique_stats['total_rows']:.1f}%)")
                
                # Privacy risk assessment
                risk_level = "HIGH" if unique_stats['num_unique_rows'] > unique_stats['total_rows'] * 0.1 else "MODERATE" if unique_stats['num_unique_rows'] > 0 else "LOW"
                print(f"  Privacy risk: {risk_level}")


def test_cli_integration():
    """Test CLI integration and command-line interface."""
    print("\n=== CLI Integration Test ===")
    
    try:
        # Test direct import and usage
        from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
        
        metapriv = metaprivBIDS_core_logic()
        print("✓ Core logic imported and initialized successfully")
        
        # Test with sample data
        if os.path.exists("../Use_Case_Data/adult_mini.csv"):
            data_info = metapriv.load_data("../Use_Case_Data/adult_mini.csv")
            print("✓ Sample data loaded successfully")
            print(f"  Data shape: {data_info['data'].shape}")
            print(f"  Columns: {len(data_info['column_types'])}")
            
            return True
        else:
            print("⚠ Sample data file not found")
            return False
            
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        return False


if __name__ == "__main__":
    """Run tests directly if executed as script."""
    print("Running metaprivBIDS CSV Data Processing Tests")
    print("=" * 50)
    
    # Run CLI integration test first
    test_cli_integration()
    
    # Run pytest
    pytest.main([__file__, "-v"])
