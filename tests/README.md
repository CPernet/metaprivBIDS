# metaprivBIDS Test Suite Documentation

This directory contains comprehensive tests for the metaprivBIDS package, focusing on privacy analysis functionality for tabular data.

## Overview

The test suite validates:
- **Privacy Metrics**: k-anonymity, ℓ-diversity, SUDA, PIF calculations
- **Data Processing**: CSV loading, column analysis, data transformations
- **CLI Functionality**: Command-line interface without GUI dependencies
- **Real Data Testing**: Using actual CSV files from Use_Case_Data/
- **Error Handling**: Edge cases and error conditions

## Test Files

### Core Test Files

1. **`test_csv_data_processing.py`** - Comprehensive CSV data testing
   - Tests with real CSV files (adult_mini.csv, data_mod_noise.csv)
   - Privacy metrics calculation and validation
   - Data transformation functions
   - Column analysis and contribution assessment

2. **`test_cli_comprehensive.py`** - CLI-focused testing
   - Command-line interface validation
   - Core logic functionality without GUI
   - Error handling and edge cases
   - Direct execution for quick validation

3. **`test_metaprivBIDS_core_logic.py`** - Unit tests
   - Individual function testing with mock data
   - Isolated component validation
   - Pytest-based test structure

4. **`test_cli_functionality.py`** - Basic CLI validation
   - Simple smoke test for CLI functionality
   - Quick verification of core imports

## Running Tests

### Prerequisites

All tests must be run from the `/tests` directory with the appropriate environment:

```bash
cd /path/to/metaprivBIDS/tests
# Activate your conda/virtual environment
conda activate your-env-name  # or source your-venv/bin/activate
```

### Individual Test Execution

#### 1. Quick CLI Validation
```bash
python test_cli_functionality.py
```
- **Purpose**: Quick smoke test
- **Runtime**: ~5 seconds
- **Use case**: Verify basic functionality

#### 2. Comprehensive CLI Testing  
```bash
python test_cli_comprehensive.py
```
- **Purpose**: Full CLI functionality test
- **Runtime**: ~30 seconds
- **Use case**: Thorough validation without GUI
- **Output**: Detailed analysis of CSV data processing

#### 3. CSV Data Processing Tests
```bash
python -m pytest test_csv_data_processing.py -v
```
- **Purpose**: Comprehensive testing with real CSV data
- **Runtime**: ~45 seconds
- **Use case**: Validate privacy analysis with actual datasets
- **Features**: Privacy metrics, data transformations, risk assessment

#### 4. Core Logic Unit Tests
```bash
python -m pytest test_metaprivBIDS_core_logic.py -v
```
- **Purpose**: Unit testing of individual functions
- **Runtime**: ~20 seconds
- **Use case**: Isolated component validation

### Complete Test Suite

Run all tests:
```bash
python -m pytest . -v
```

Or run specific test patterns:
```bash
python -m pytest test_csv* -v     # Only CSV-related tests
python -m pytest test_cli* -v     # Only CLI-related tests
```

## Quick Start - Testing with CSV Data

### Immediate Verification
```bash
cd /path/to/metaprivBIDS/tests
# Activate your environment first
python demo_cli_usage.py
```

This demo script provides:
- Complete functionality demonstration
- Privacy analysis of the CSV data files
- Column contribution analysis  
- Data transformation examples
- Results interpretation

### Expected Results with `adult_mini.csv`
- **Dataset**: 200 rows × 9 columns (demographics + health data)
- **Basic Demographics** (age, sex, education):
  - k-anonymity: 1 (high privacy risk)
  - ℓ-diversity: 1 (low diversity)
  - Unique rows: ~65% of total
- **Column Impact**: Age contributes most to uniqueness
- **Transformations**: Rounding reduces unique values significantly

## Test Data

The tests use CSV files from `../Use_Case_Data/`:

### adult_mini.csv
- **Size**: 200 rows × 9 columns
- **Content**: Demographics, occupation, health data
- **Columns**: age, education, marital-status, occupation, relationship, sex, salary-class, disease, exercise_weekly_hours
- **Use case**: Testing privacy analysis on demographic data

### data_mod_noise.csv  
- **Size**: 200 rows × 9 columns
- **Content**: Modified version with noise added
- **Use case**: Comparing privacy metrics before/after noise addition

## Key Test Scenarios

### 1. Privacy Metrics Validation
```python
# k-anonymity calculation
k_anon = metapriv.calculate_k_anonymity(data, ['age', 'education', 'sex'])

# ℓ-diversity calculation  
l_div = metapriv.calculate_l_diversity(data, quasi_identifiers, 'salary-class')

# Unique rows analysis
stats = metapriv.calculate_unique_rows(data, selected_columns, sensitive_attr)
```

### 2. Data Transformation Testing
```python
# Rounding for numerical privacy
rounded_data = metapriv.round_values(data, 'age', precision=1)

# Noise addition
noisy_data = metapriv.add_noise(data, 'age', 'laplacian')

# Categorical value combination
combined_history = metapriv.combine_values(data, 'education')
```

### 3. Column Analysis
```python
# Identify columns contributing to uniqueness
results = metapriv.find_lowest_unique_columns(data, selected_columns)

# Combined column contribution analysis
contribution_df = metapriv.compute_combined_column_contribution(data, columns)
```

## Expected Test Results

### Successful Test Run Output
```
✓ Core logic imported successfully
✓ Sample data loaded successfully
✓ Privacy metrics calculated
✓ Data transformations applied
✓ Column analysis completed
✓ Error handling verified
```

### Privacy Analysis Results
- **k-anonymity**: Typically 1-5 for demographic data
- **ℓ-diversity**: Varies by sensitive attribute diversity
- **Unique rows**: Percentage of records that are unique
- **Risk assessment**: HIGH/MODERATE/LOW based on uniqueness

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'metaprivBIDS'
   ```
   - **Solution**: Ensure package is installed: `python install.py`
   - **Check**: Run from `/tests` directory

2. **Missing Data Files**
   ```
   FileNotFoundError: ../Use_Case_Data/adult_mini.csv
   ```
   - **Solution**: Verify CSV files exist in Use_Case_Data/
   - **Alternative**: Tests will skip missing files gracefully

3. **GUI-Related Errors**
   ```
   qt.qpa.plugin: Could not load the Qt platform plugin
   ```
   - **Solution**: Use CLI-only tests (test_cli_comprehensive.py)
   - **Note**: GUI functionality is intentionally avoided in tests

4. **Environment Issues**
   ```
   pkg_resources is deprecated
   ```
   - **Solution**: Warning is suppressed in test code
   - **Impact**: Does not affect functionality

### Test Environment Verification

Verify your environment:
```bash
# Check conda environment
conda list | grep metaprivBIDS

# Check Python path
python -c "import metaprivBIDS; print(metaprivBIDS.__file__)"

# Check test data
ls -la ../Use_Case_Data/
```

## Test Development Guidelines

### Adding New Tests

1. **Location**: Place in `/tests` directory
2. **Naming**: Use `test_*.py` pattern for pytest discovery
3. **Environment**: Always activate conda environment first
4. **Data**: Use existing CSV files or create test fixtures
5. **GUI**: Avoid GUI dependencies in tests

### Test Structure
```python
import pytest
import pandas as pd
from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic

class TestNewFeature:
    @pytest.fixture
    def metapriv_instance(self):
        return metaprivBIDS_core_logic()
    
    def test_feature(self, metapriv_instance):
        # Test implementation
        assert condition, "Test description"
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures for setup/teardown
3. **Assertions**: Clear, descriptive assertion messages
4. **Documentation**: Document test purpose and expected behavior
5. **Error Handling**: Test both success and failure cases

## Performance Expectations

- **Quick tests**: < 10 seconds
- **Comprehensive tests**: < 60 seconds  
- **Full test suite**: < 2 minutes
- **Memory usage**: < 500MB for test data

## Integration with CI/CD

Tests are designed to be:
- **Automated**: Can run without user interaction
- **Reliable**: Handle missing data gracefully
- **Fast**: Complete within reasonable time limits
- **Comprehensive**: Cover all major functionality

For automated testing:
```bash
#!/bin/bash
cd /path/to/metaprivBIDS/tests
# Activate your environment: conda activate your-env-name
python -m pytest . -v --tb=short
```
