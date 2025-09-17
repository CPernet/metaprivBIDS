# metaprivBIDS

[![Documentation Status](https://readthedocs.org/projects/metaprivbids/badge/?version=latest)](https://metaprivbids.readthedocs.io/en/latest/?badge=latest)




This Python build tool enables a given user to calculate a variety of different data privacy metrics on tabular data from a user interface. 

# Methods

#### Assessing Privacy risk:

- K-anonymity [^1]
- ℓ-diversity [^2]
- Sample Unique Detection Algorithm (SUDA) [^3]
- Privacy Information Factor (PIF) [^4]

[^1]: Sweeney, L. (2002). k-Anonymity: A Model for Protecting Privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(05), 557-570.
[^2]: Machanavajjhala, A., Kifer, D., Gehrke, J., & Venkitasubramaniam, M. (2007). ℓ-Diversity: Privacy Beyond k-Anonymity. *ACM Transactions on Knowledge Discovery from Data (TKDD)*, 1(1), 3-es.
[^3]: Elliott, M. J., & Skinner, C. J. (2000). Identifying population uniques using limited information. *Proceedings of the Annual Meeting of the American Statistical Association*.
[^4]: Information Governance ANZ. (2019). *Privacy Impact Assessment eReport.* [Link](https://www.infogovanz.com/wp-content/uploads/2020/01/191202-ACS-Privacy-eReport.pdf)


#### Mitigating Privacy Risk

- Noise addition
- Field generalisation
- Rounded Approximation 


# Input data format

Input can be in either CSV or TSV format.
For meta information, an option to load a JSON file is available.

# Software installation


### Option 1
The metaprivBIDS software runs on multiple platforms (e.g. Linux, macOS, Windows) that have a Python 3 installation.
It is recommended (but not required) to first create a virtual environment.

  
 In the event of permission issues for system dependent files, you might want to set the pkgs_dirs option in Conda's configuration to use a directory that is writable by you.
 
```console 
conda config --add pkgs_dirs ~/conda_pkgs
```
Creates the environment. 

Graphviz requires system-level dependencies as well as rpy2 and can be installed directly when building the virtual environment. The `pygraphviz` package is optional and only needed for advanced graph visualization. On Windows you can skip installing `pygraphviz` to avoid requiring Microsoft C++ build tools.

```console
conda create --name venv -c conda-forge "python>=3.7" graphviz r-base r-sdcMicro rpy2
# Optional: conda install pygraphviz
# (the provided install.py script will also prompt about this dependency)
```

on windows, pif execute some command in sh terminal so also do
```console
conda install m2-bash   
```

Activates the environment. 

```console
conda activate your-env-name  # or source your-venv/bin/activate
```

You can then install metaprivBIDS by first cloning the git repository.

```console
git clone https://github.com/CPernet/metaprivBIDS.git
```

cd into the MetaprivBIDS folder  

```console
cd MetaprivBIDS
```
and then run

```console
python install.py
```
The script will ask whether to install the optional `pygraphviz` package.
This script installs the package and prompts whether to include the optional
`pygraphviz` dependency.


### Option 2 


```console 
python -m venv venv
source venv/bin/activate
```

You can then install metaprivBIDS by cloning the git repository.

```console
git clone https://github.com/CPernet/metaprivBIDS.git
```


# Installation

## Prerequisites
- Python 3.7+ (tested with Python 3.13)
- Conda environment (recommended)

## Step 1: Setup Environment
First, activate your conda environment:

```console
conda activate your-env-name  # or source your-venv/bin/activate
```

## Step 2: Install Dependencies
Navigate to the MetaprivBIDS directory and run the interactive installer:

```console
cd metaprivBIDS
python install.py
```

The installer will:
- ✅ **Fix pkg_resources deprecation warning** (automatically pins setuptools<81 if needed)
- ✅ **Install Qt dependencies** (attempts to resolve GUI compatibility issues)
- ❓ **Ask about pygraphviz** (optional package for advanced graph visualization)

## Known Issues & Solutions

### Qt GUI Compatibility Issues
On some systems, the Qt GUI may hang due to missing X11/XCB libraries or platform compatibility issues. The installer provides several launch options:

# Usage Options

## Option 1: Safe Launcher (Recommended)
Use the intelligent launcher that tests Qt compatibility and provides fallbacks:

```console
python run_metaprivBIDS_safe.py
```

This launcher will:
1. Test CLI functionality first
2. Ask if you want to try the GUI
3. Test Qt compatibility with timeouts
4. Provide fallback to CLI mode if GUI fails

## Option 2: CLI-Only Mode (Most Reliable)
If you only need the core functionality without GUI:

```console
python test_cli.py
```

## Option 3: Direct GUI Launch (May Hang)
For direct GUI access (use with caution):

```console
python run_metaprivBIDS.py
```

**If this hangs**, use Ctrl+C to interrupt and try the safe launcher.

## Option 4: GUI with Platform Fallbacks
If the GUI hangs, try these Qt platform alternatives:

```console
# Minimal platform (no visual output but functional)
QT_QPA_PLATFORM=minimal python run_metaprivBIDS.py

# Offscreen platform (for headless servers)
QT_QPA_PLATFORM=offscreen python run_metaprivBIDS.py
```

# Command-Line Execution

After following the installation guide, the metrics within the MetaprivBIDS tool can be called through an import statement without making use of the GUI.

## Core Logic Usage

```python
from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
metapriv = metaprivBIDS_core_logic()

# Load the data
data_info = metapriv.load_data('Use_Case_Data/adult_mini.csv')

# Inspect {column, unique value count, column type}
data = data_info["data"]
print("Column Types:", '\n')
print(data_info["column_types"], '\n')

# Select Quasi-Identifiers
selected_columns = ["age", "education", "marital-status", "occupation", "relationship", "sex", "salary-class"]
results_k_global = metapriv.find_lowest_unique_columns(data, selected_columns)
print('Find Influential Columns:', '\n')
print(results_k_global)

# Compute Personal Information Factor 
pif_value, cig_df = metapriv.compute_cig(data, selected_columns)
print("PIF Value:", pif_value)
print("CIG DataFrame:")
print(cig_df)

# Run SUDA2 computation
results_suda = metapriv.compute_suda2(data, selected_columns, sample_fraction=0.3, missing_value=-999)

# Access results
data_with_scores = results_suda["data_with_scores"]
attribute_contributions = results_suda["attribute_contributions"]
attribute_level_contributions = results_suda["attribute_level_contributions"]
```

## Testing from Tests Folder

To run tests, navigate to the tests folder and activate your environment:

```console
cd tests
conda activate your-env-name  # or source your-venv/bin/activate
python test_metaprivBIDS_core_logic.py
```

Note: Install pytest if needed: `pip install pytest`

# Troubleshooting

## Common Issues and Solutions

### 1. pkg_resources Deprecation Warning
```
UserWarning: pkg_resources is deprecated as an API
```
**Solution**: The installer automatically fixes this by pinning setuptools<81. If you see this warning, run:
```console
pip install "setuptools<81"
```

### 2. Qt Platform Plugin Errors
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
This plugin does not support propagateSizeHints()
```
**Solutions**:
1. Use the safe launcher: `python run_metaprivBIDS_safe.py`
2. Use CLI-only mode: `python test_cli.py`
3. Try platform fallbacks:
   - `QT_QPA_PLATFORM=minimal python run_metaprivBIDS.py`
   - `QT_QPA_PLATFORM=offscreen python run_metaprivBIDS.py`

### 3. Application Hangs
If the GUI hangs, press `Ctrl+C` to interrupt and use:
- Safe launcher: `python run_metaprivBIDS_safe.py`
- CLI mode: `python test_cli.py`

### 4. Import Errors
If you get module import errors, ensure:
1. Your conda environment is activated
2. The package is installed: `python install.py`
3. You're in the correct directory

### 5. Missing Test Dependencies
For running tests:
```console
pip install pytest
cd tests
python test_metaprivBIDS_core_logic.py
```

### 6. Permission Issues
If you cannot install system packages (sudo access), the CLI mode will work without additional system dependencies.

## Support

For additional support:
- Use CLI mode for core functionality: `python test_cli.py`
- Check the debug script: `python debug_test.py`
- The core logic is fully functional without GUI dependencies




## Related tools








