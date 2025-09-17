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
    python -m pytest test_csv_data_processing_clean.py -v
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
except ImportError:
    print("Failed to import metaprivBIDS. Please ensure the package is installed.")
    sys.exit(1)


class TestCSVDataProcessing:
    """Comprehensive test suite for CSV data processing with metaprivBIDS."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures."""
        self.mp = metaprivBIDS_core_logic()
        self.csv_data_dir = os.path.join(os.path.dirname(__file__), '..', 'Use_Case_Data')
        self.adult_mini_path = os.path.join(self.csv_data_dir, 'adult_mini.csv')
        self.data_mod_noise_path = os.path.join(self.csv_data_dir, 'data_mod_noise.csv')

    def test_csv_files_exist(self):
        """Test that required CSV files exist."""
        assert os.path.exists(self.adult_mini_path), f"adult_mini.csv not found at {self.adult_mini_path}"
        assert os.path.exists(self.data_mod_noise_path), f"data_mod_noise.csv not found at {self.data_mod_noise_path}"

    def test_load_adult_mini_csv(self):
        """Test loading adult_mini.csv dataset."""
        data_info = self.mp.load_data(self.adult_mini_path)
        
        # Verify data structure
        assert 'data' in data_info
        assert 'original_data' in data_info
        assert 'column_unique_counts' in data_info
        assert 'column_types' in data_info
        
        # Verify data dimensions
        data = data_info['data']
        assert data.shape[0] > 0, "Dataset should have rows"
        assert data.shape[1] > 0, "Dataset should have columns"
        
        # Expected columns in adult_mini.csv
        expected_columns = ['age', 'education', 'marital-status', 'occupation', 
                          'relationship', 'sex', 'salary-class', 'disease', 'exercise_weekly_hours']
        
        for col in expected_columns:
            assert col in data.columns, f"Expected column '{col}' not found"

    def test_load_data_mod_noise_csv(self):
        """Test loading data_mod_noise.csv dataset."""
        data_info = self.mp.load_data(self.data_mod_noise_path)
        
        # Verify data structure
        assert 'data' in data_info
        data = data_info['data']
        assert data.shape[0] > 0, "Dataset should have rows"
        assert data.shape[1] > 0, "Dataset should have columns"

    def test_privacy_metrics_adult_mini(self):
        """Test privacy metrics calculation on adult_mini.csv."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with demographic columns
        selected_columns = ['age', 'education', 'marital-status']
        sensitive_attr = 'salary-class'
        
        # Calculate privacy metrics
        unique_stats = self.mp.calculate_unique_rows(data, selected_columns, sensitive_attr)
        
        # Verify results structure
        assert 'total_rows' in unique_stats
        assert 'num_unique_rows' in unique_stats
        assert 'k_anonymity' in unique_stats
        assert 'l_diversity' in unique_stats
        
        # Verify reasonable values
        assert unique_stats['total_rows'] == len(data)
        assert unique_stats['k_anonymity'] >= 1
        assert unique_stats['l_diversity'] >= 1

    def test_k_anonymity_calculation(self):
        """Test k-anonymity calculation with various column combinations."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with single column
        k_anon_1 = self.mp.calculate_k_anonymity(data, ['sex'])
        assert k_anon_1 >= 1
        
        # Test with multiple columns (should generally decrease k-anonymity)
        k_anon_2 = self.mp.calculate_k_anonymity(data, ['sex', 'education'])
        assert k_anon_2 >= 1
        assert k_anon_2 <= k_anon_1  # More columns typically reduce k-anonymity

    def test_l_diversity_calculation(self):
        """Test ℓ-diversity calculation with sensitive attributes."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with different sensitive attributes
        selected_columns = ['age', 'education']
        
        l_div_salary = self.mp.calculate_l_diversity(data, selected_columns, 'salary-class')
        assert l_div_salary >= 1
        
        l_div_disease = self.mp.calculate_l_diversity(data, selected_columns, 'disease')
        assert l_div_disease >= 1

    def test_column_contribution_analysis(self):
        """Test analysis of column contributions to uniqueness."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with subset of columns
        selected_columns = ['age', 'education', 'marital-status', 'sex']
        
        results = self.mp.find_lowest_unique_columns(data, selected_columns)
        
        # Verify results structure
        assert isinstance(results, dict)
        assert len(results) == len(selected_columns)
        
        for col in selected_columns:
            assert col in results
            assert 'unique_count_after_removal' in results[col]
            assert 'difference' in results[col]
            assert 'normalized_difference' in results[col]

    def test_combined_column_analysis(self):
        """Test combined column contribution analysis."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with manageable subset
        selected_columns = ['sex', 'education', 'marital-status']
        
        result_df = self.mp.compute_combined_column_contribution(
            data, selected_columns, min_size=1, max_size=2
        )
        
        # Verify results
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) > 0
        assert 'Combination' in result_df.columns
        assert 'Unique Rows' in result_df.columns

    def test_data_comparison(self):
        """Test comparison between original and noise-modified data."""
        # Load both datasets
        original_info = self.mp.load_data(self.adult_mini_path)
        modified_info = self.mp.load_data(self.data_mod_noise_path)
        
        original_data = original_info['data']
        modified_data = modified_info['data']
        
        # Both should have same number of rows (approximately)
        assert abs(len(original_data) - len(modified_data)) <= 1
        
        # Calculate privacy metrics for both
        selected_columns = ['age', 'education', 'marital-status']
        sensitive_attr = 'salary-class' if 'salary-class' in original_data.columns else original_data.columns[-1]
        
        original_stats = self.mp.calculate_unique_rows(original_data, selected_columns, sensitive_attr)
        
        # Modified data might have different column structure, so adapt
        modified_columns = [col for col in selected_columns if col in modified_data.columns]
        if modified_columns:
            modified_stats = self.mp.calculate_unique_rows(modified_data, modified_columns, sensitive_attr)
            
            # Privacy metrics should be reasonable
            assert original_stats['k_anonymity'] >= 1
            assert modified_stats['k_anonymity'] >= 1

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        data_info = self.mp.load_data(self.adult_mini_path)
        data = data_info['data']
        
        # Test with empty column list
        with pytest.raises((ValueError, IndexError)):
            self.mp.calculate_k_anonymity(data, [])
        
        # Test with non-existent column
        with pytest.raises((ValueError, KeyError)):
            self.mp.calculate_k_anonymity(data, ['non_existent_column'])

    def test_data_integrity(self):
        """Test data integrity and quality checks."""
        for csv_path in [self.adult_mini_path, self.data_mod_noise_path]:
            data_info = self.mp.load_data(csv_path)
            data = data_info['data']
            
            # Check for basic data quality
            assert len(data) > 0, f"Dataset {csv_path} should not be empty"
            assert len(data.columns) > 0, f"Dataset {csv_path} should have columns"
            
            # Check column unique counts
            for col, count in data_info['column_unique_counts'].items():
                assert count > 0, f"Column {col} should have unique values"
                assert count <= len(data), f"Unique count for {col} shouldn't exceed total rows"

if __name__ == "__main__":
    # Allow direct execution
    pytest.main([__file__, "-v"])
