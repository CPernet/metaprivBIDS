# metaprivBIDS Quick Start Guide

## Installation
```bash
cd metaprivBIDS
# Activate your conda/virtual environment first
# conda activate your-env-name  # or source your-venv/bin/activate
python install.py
```

## Launch Options (in order of reliability)

### 1. Safe Launcher (Recommended) ⭐
```bash
python run_metaprivBIDS_safe.py
```
- Tests Qt compatibility first
- Provides CLI fallback if GUI fails
- Interactive prompt for GUI attempt

### 2. CLI-Only Mode (Most Reliable) ✅
```bash
python test_cli.py
```
- Bypasses Qt entirely
- Full core functionality available
- No GUI dependencies needed

### 3. Direct GUI (May Hang) ⚠️
```bash
python run_metaprivBIDS.py
```
- Direct GUI launch
- May hang on some systems
- Use Ctrl+C to interrupt if needed

### 4. Platform Fallbacks 🔧
If GUI hangs, try:
```bash
QT_QPA_PLATFORM=minimal python run_metaprivBIDS.py
QT_QPA_PLATFORM=offscreen python run_metaprivBIDS.py
```

## Core Functionality (CLI)
```python
from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic

# Initialize
metapriv = metaprivBIDS_core_logic()

# Load data
data_info = metapriv.load_data('Use_Case_Data/adult_mini.csv')

# Get column types
print(data_info['column_types'])

# Compute metrics
selected_cols = ["age", "education", "marital-status"]
pif_value, cig_df = metapriv.compute_cig(data_info['data'], selected_cols)
```

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| GUI hangs | `python run_metaprivBIDS_safe.py` or `python test_cli.py` |
| pkg_resources warning | Already fixed by installer |
| Qt platform errors | Use CLI mode: `python test_cli.py` |
| Import errors | Check conda environment and installation |
| Test failures | `cd tests && pip install pytest` |

## Key Files
- `install.py` - Interactive installer with automatic fixes
- `run_metaprivBIDS_safe.py` - Safe launcher with Qt testing
- `test_cli.py` - CLI-only mode (most reliable)
- `debug_test.py` - Diagnostic script
- `run_metaprivBIDS.py` - Direct GUI launcher
