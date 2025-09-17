#!/usr/bin/env python3
"""
Simple test script to debug metaprivBIDS issues.
"""

print("=== metaprivBIDS Debug Test ===")
print("1. Testing basic imports...")

try:
    import sys
    import os
    print("✓ sys and os imported")
except Exception as e:
    print(f"✗ Basic imports failed: {e}")
    sys.exit(1)

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

print("\n2. Testing metaprivBIDS core import...")
try:
    from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
    print("✓ Core logic imported successfully")
except Exception as e:
    print(f"✗ Core logic import failed: {e}")
    sys.exit(1)

print("\n3. Testing core functionality...")
try:
    metapriv = metaprivBIDS_core_logic()
    print("✓ Core logic initialized")
except Exception as e:
    print(f"✗ Core logic initialization failed: {e}")
    sys.exit(1)

print("\n4. Testing data loading...")
try:
    data_info = metapriv.load_data('Use_Case_Data/adult_mini.csv')
    print(f"✓ Data loaded: {data_info['data'].shape}")
except Exception as e:
    print(f"✗ Data loading failed: {e}")
    # Don't exit here, data file might not exist

print("\n=== Test Complete ===")
print("Core functionality is working!")
print("\nTo use metaprivBIDS in CLI mode:")
print("```python")
print("from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic")
print("metapriv = metaprivBIDS_core_logic()")
print("data_info = metapriv.load_data('your_data.csv')")
print("print(data_info['column_types'])")
print("```")
