#!/usr/bin/env python3
"""
Safe launcher for metaprivBIDS that avoids Qt hanging issues.
This script tries to detect Qt compatibility issues and provides fallback options.
"""

import os
import sys
import warnings
import signal
import subprocess
import time
from contextlib import contextmanager

def suppress_warnings():
    """Suppress known warnings that we can't fix."""
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

def setup_qt_environment():
    """Set up Qt environment variables for proper plugin loading."""
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if conda_prefix:
        possible_paths = [
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PySide6', 'Qt', 'plugins'),
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PyQt6', 'Qt6', 'plugins'),
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = path
                os.environ['QT_PLUGIN_PATH'] = path
                break
        
        # Add library path
        lib_path = os.path.join(conda_prefix, 'lib')
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{current_ld_path}" if current_ld_path else lib_path

@contextmanager
def timeout(duration):
    """Context manager for timeout operations."""
    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out")
    
    # Set the signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)

def test_qt_import():
    """Test if Qt can be imported without hanging."""
    print("Testing Qt import...")
    try:
        with timeout(10):  # 10 second timeout
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            print("✓ Qt import successful")
            return True
    except TimeoutError:
        print("✗ Qt import timed out")
        return False
    except ImportError as e:
        print(f"✗ Qt import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Qt import error: {e}")
        return False

def test_qt_application():
    """Test if Qt application can be created without hanging."""
    print("Testing Qt application creation...")
    try:
        with timeout(15):  # 15 second timeout
            # Set minimal Qt platform
            os.environ['QT_QPA_PLATFORM'] = 'minimal'
            from PySide6.QtWidgets import QApplication
            
            # Try to create a minimal application
            app = QApplication([])
            print("✓ Qt application creation successful")
            app.quit()
            return True
    except TimeoutError:
        print("✗ Qt application creation timed out")
        return False
    except Exception as e:
        print(f"✗ Qt application creation failed: {e}")
        return False

def run_cli_mode():
    """Run metaprivBIDS in CLI-only mode."""
    print("\n" + "="*60)
    print("RUNNING METAPRIVBIDS IN CLI MODE")
    print("="*60)
    print("Qt GUI is not available, but you can use the core functionality:")
    print()
    
    try:
        from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
        
        print("Example usage:")
        print("```python")
        print("from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic")
        print("metapriv = metaprivBIDS_core_logic()")
        print("data_info = metapriv.load_data('your_data.csv')")
        print("print(data_info['column_types'])")
        print("```")
        print()
        
        # Test with sample data
        print("Testing with sample data...")
        metapriv = metaprivBIDS_core_logic()
        data_info = metapriv.load_data('Use_Case_Data/adult_mini.csv')
        print(f"✓ Sample data loaded: {data_info['data'].shape[0]} rows, {data_info['data'].shape[1]} columns")
        print("✓ Core functionality is working!")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI mode failed: {e}")
        return False

def run_gui_mode():
    """Attempt to run metaprivBIDS in GUI mode."""
    print("\n" + "="*60)
    print("ATTEMPTING TO LAUNCH METAPRIVBIDS GUI")
    print("="*60)
    
    # Setup environment
    setup_qt_environment()
    suppress_warnings()
    
    try:
        with timeout(30):  # 30 second timeout for GUI startup
            # Try minimal platform first
            os.environ['QT_QPA_PLATFORM'] = 'minimal'
            
            print("Importing metaprivBIDS GUI...")
            from metaprivBIDS.metaprivBIDS import main as metapriv_main
            
            print("Starting GUI application...")
            metapriv_main()
            
    except TimeoutError:
        print("✗ GUI startup timed out (likely hanging)")
        print("The GUI has compatibility issues with your system.")
        return False
    except Exception as e:
        print(f"✗ GUI failed: {e}")
        return False
    
    return True

def main():
    """Main launcher function with fallback options."""
    print("=" * 60)
    print("metaprivBIDS Safe Launcher")
    print("=" * 60)
    
    # Always test CLI mode first (most reliable)
    print("\n1. Testing CLI functionality...")
    cli_works = run_cli_mode()
    
    if not cli_works:
        print("✗ CLI mode failed - there may be installation issues")
        return 1
    
    # Ask user if they want to try GUI
    print("\n" + "-" * 60)
    try:
        response = input("Do you want to try launching the GUI? (y/N): ").strip().lower()
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    
    if response in ['y', 'yes']:
        print("\n2. Testing Qt compatibility...")
        
        # Test Qt import
        if not test_qt_import():
            print("Qt import failed - GUI not available")
            return 0
        
        # Test Qt application
        if not test_qt_application():
            print("Qt application creation failed - GUI not available")
            return 0
        
        # Try to run GUI
        print("\n3. Attempting GUI launch...")
        gui_success = run_gui_mode()
        
        if not gui_success:
            print("\nGUI failed to start. Use CLI mode instead.")
            return 0
    else:
        print("\nSticking with CLI mode - this is the most reliable option.")
    
    print("\nLauncher completed successfully!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
