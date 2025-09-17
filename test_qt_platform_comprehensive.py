#!/usr/bin/env python3
"""
Comprehensive Qt Platform Testing Script
Tests the new adaptive Qt environment setup across different scenarios.
"""

import os
import sys
import subprocess
import tempfile
from contextlib import contextmanager

@contextmanager
def mock_environment(**env_vars):
    """Context manager to temporarily set environment variables."""
    old_env = {}
    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    
    try:
        yield
    finally:
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value

def test_environment_detection():
    """Test different environment detection scenarios."""
    print("=== Testing Environment Detection ===\n")
    
    # Import the setup function
    sys.path.insert(0, '/indirect/staff/cyrilpernet/metaprivBIDS')
    from metaprivBIDS.metaprivBIDS import setup_qt_environment
    
    scenarios = [
        {
            'name': 'Headless Server (no DISPLAY)',
            'env': {'DISPLAY': None, 'QT_QPA_PLATFORM': None},
            'expected': 'offscreen'
        },
        {
            'name': 'SSH X11 Forwarding',
            'env': {'DISPLAY': ':10.0', 'SSH_CONNECTION': '1.2.3.4 1234 5.6.7.8 22', 'QT_QPA_PLATFORM': None},
            'expected': 'xcb or vnc'
        },
        {
            'name': 'ThinLinc VNC Session',
            'env': {'DISPLAY': ':15.0', 'QT_QPA_PLATFORM': None},
            'expected': 'xcb'
        },
        {
            'name': 'Wayland Desktop',
            'env': {'DISPLAY': ':0', 'WAYLAND_DISPLAY': 'wayland-0', 'XDG_SESSION_TYPE': 'wayland', 'QT_QPA_PLATFORM': None},
            'expected': 'wayland'
        },
        {
            'name': 'Local X11 Desktop',
            'env': {'DISPLAY': ':0', 'QT_QPA_PLATFORM': None},
            'expected': 'xcb'
        },
        {
            'name': 'Explicitly Set Platform',
            'env': {'DISPLAY': ':0', 'QT_QPA_PLATFORM': 'minimal'},
            'expected': 'minimal'
        },
        {
            'name': 'Testing Environment',
            'env': {'DISPLAY': ':0', 'QT_QPA_PLATFORM': None},
            'testing': True,
            'expected': 'offscreen'
        }
    ]
    
    for scenario in scenarios:
        print(f"Testing: {scenario['name']}")
        
        with mock_environment(**scenario['env']):
            # Mock testing environment if needed
            if scenario.get('testing'):
                sys.modules['pytest'] = type(sys)('pytest')  # Mock pytest module
            
            try:
                setup_qt_environment()
                actual_platform = os.environ.get('QT_QPA_PLATFORM', 'not set')
                print(f"  Result: {actual_platform}")
                print(f"  Expected: {scenario['expected']}")
                
                if scenario['expected'] in actual_platform or actual_platform in scenario['expected']:
                    print("  ✅ PASS")
                else:
                    print("  ❌ FAIL")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
            finally:
                # Clean up mock pytest
                if 'pytest' in sys.modules and scenario.get('testing'):
                    del sys.modules['pytest']
        
        print()

def test_platform_availability():
    """Test which Qt platforms are actually available in this environment."""
    print("=== Testing Platform Availability ===\n")
    
    platforms = ['xcb', 'wayland', 'vnc', 'offscreen', 'minimal']
    
    for platform in platforms:
        test_script = f'''
import os
import sys
os.environ["QT_QPA_PLATFORM"] = "{platform}"
try:
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    print("SUCCESS")
    app.quit()
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_script)
                f.flush()
                
                # Run with conda
                result = subprocess.run([
                    'conda', 'run', '-p', '/users/cyrilpernet/conda-envs/venv',
                    'python', f.name
                ], capture_output=True, text=True, timeout=15)
                
                os.unlink(f.name)
                
                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    print(f"  {platform}: ✅ Available")
                else:
                    print(f"  {platform}: ❌ Not available ({result.stderr.strip() or result.stdout.strip()})")
                    
        except subprocess.TimeoutExpired:
            print(f"  {platform}: ⏰ Timeout")
        except Exception as e:
            print(f"  {platform}: ❌ Error: {e}")

def test_actual_gui_launch():
    """Test launching the actual GUI with the new setup."""
    print("=== Testing Actual GUI Launch ===\n")
    
    test_script = '''
import os
import sys
sys.path.insert(0, "/indirect/staff/cyrilpernet/metaprivBIDS")

# Import and run setup
from metaprivBIDS.metaprivBIDS import setup_qt_environment
setup_qt_environment()

print(f"Selected platform: {os.environ.get('QT_QPA_PLATFORM')}")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
    from PySide6.QtCore import QTimer
    
    app = QApplication(sys.argv)
    
    # Create a simple test window
    window = QMainWindow()
    window.setWindowTitle("Qt Platform Test")
    window.resize(300, 100)
    
    label = QLabel("Qt Platform Test - GUI Working!")
    window.setCentralWidget(label)
    
    window.show()
    
    # Close after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    print("GUI test window created successfully")
    result = app.exec()
    print(f"App exec completed with code: {result}")
    
except Exception as e:
    print(f"GUI test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            f.flush()
            
            print("Launching GUI test...")
            result = subprocess.run([
                'conda', 'run', '-p', '/users/cyrilpernet/conda-envs/venv',
                'python', f.name
            ], timeout=30)
            
            os.unlink(f.name)
            
            if result.returncode == 0:
                print("✅ GUI test completed successfully")
            else:
                print(f"❌ GUI test failed with return code: {result.returncode}")
                
    except subprocess.TimeoutExpired:
        print("⏰ GUI test timed out")
    except Exception as e:
        print(f"❌ GUI test error: {e}")

def main():
    """Run all tests."""
    print("Qt Platform Comprehensive Test Suite")
    print("=" * 50)
    print()
    
    test_environment_detection()
    test_platform_availability()
    test_actual_gui_launch()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")

if __name__ == "__main__":
    main()
