#!/usr/bin/env python3
"""
Launcher script for metaprivBIDS that sets up the proper Qt environment
and suppresses the pkg_resources deprecation warning.
"""

import os
import sys
import warnings
import subprocess


def setup_qt_environment():
    """Set up Qt environment variables for proper plugin loading."""
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if conda_prefix:
        # Try different possible Qt plugin paths
        possible_paths = [
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PySide6', 'Qt', 'plugins'),
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PyQt6', 'Qt6', 'plugins'),
            os.path.join(conda_prefix, 'lib', 'python3.13', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
            os.path.join(conda_prefix, 'plugins'),
            os.path.join(conda_prefix, 'lib', 'qt6', 'plugins'),
            os.path.join(conda_prefix, 'lib', 'qt5', 'plugins')
        ]
        
        qt_plugin_path = None
        for path in possible_paths:
            if os.path.exists(path):
                qt_plugin_path = path
                break
        
        if qt_plugin_path:
            # Set environment variables
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
            os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
            print(f"Qt plugin path set to: {qt_plugin_path}")
        
        # Add library path for better Qt loading
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        lib_path = os.path.join(conda_prefix, 'lib')
        if lib_path not in current_ld_path:
            os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{current_ld_path}" if current_ld_path else lib_path


def suppress_warnings():
    """Suppress known warnings that we can't fix (like pkg_resources deprecation)."""
    # Suppress pkg_resources deprecation warning
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")


def test_qt_platform(platform_name, timeout=5):
    """Test if a Qt platform works without hanging."""
    print(f"Testing Qt platform: {platform_name}")
    
    # Create a test script that tries to import Qt with the given platform
    test_script = f"""
import os
import sys
import warnings
os.environ['QT_QPA_PLATFORM'] = '{platform_name}'
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

try:
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    print("SUCCESS: {platform_name} platform works")
    app.quit()
    sys.exit(0)
except Exception as e:
    print(f"FAILED: {platform_name} platform failed: {{e}}")
    sys.exit(1)
"""
    
    try:
        # Run the test with a timeout
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], timeout=timeout, capture_output=True, text=True)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print(f"✓ {platform_name} platform works!")
            return True
        else:
            print(f"✗ {platform_name} platform failed")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {platform_name} platform timed out (likely hanging)")
        return False
    except Exception as e:
        print(f"✗ {platform_name} platform error: {e}")
        return False


def find_working_qt_platform():
    """Find a working Qt platform that doesn't hang."""
    # Test platforms in order of preference
    platforms = ['offscreen', 'minimal', 'wayland', 'xcb']
    
    for platform in platforms:
        if test_qt_platform(platform):
            return platform
    
    return None


def main():
    """Main launcher function."""
    print("Setting up metaprivBIDS environment...")
    
    # Set up Qt environment (basic setup)
    setup_qt_environment()
    
    # Suppress known warnings
    suppress_warnings()
    
    print("Launching metaprivBIDS GUI...")
    try:
        # Use the comprehensive Qt setup from the main module (includes VNC support)
        from metaprivBIDS.metaprivBIDS import setup_qt_environment as comprehensive_qt_setup
        from metaprivBIDS.metaprivBIDS import main as metapriv_main
        
        # Use the comprehensive setup that includes VNC and platform detection
        comprehensive_qt_setup()
        
        # Check if display is available for VNC message
        has_display = bool(os.environ.get('DISPLAY'))
        qt_platform = os.environ.get('QT_QPA_PLATFORM', '').lower()
        
        if qt_platform == 'vnc':
            vnc_port = os.environ.get("QT_QPA_VNC_PORT", "5900")
            print(f"🖥️  GUI will be accessible via VNC on port {vnc_port}")
            print(f"   To view the GUI, connect with: vncviewer localhost:{vnc_port}")
            print(f"   Or use any VNC client to connect to your server:{vnc_port}")
        elif has_display:
            print("🖥️  GUI starting in display mode")
        else:
            print("🖥️  GUI starting in headless mode")
            
        metapriv_main()
        
    except Exception as e:
        print(f"Error running GUI: {e}")
        print("Trying fallback platform detection...")
        
        # Fallback to the old method if the comprehensive setup fails
        working_platform = find_working_qt_platform()
        
        if working_platform:
            print(f"Using fallback Qt platform: {working_platform}")
            os.environ['QT_QPA_PLATFORM'] = working_platform
            
            try:
                from metaprivBIDS.metaprivBIDS import main as metapriv_main
                metapriv_main()
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                print("Try using the CLI mode instead.")
        else:
            print("Warning: No working Qt platform found. The GUI cannot start.")
            print("This is likely due to missing system dependencies.")
        
    # Offer CLI-only mode
    print("\n" + "="*60)
    print("CLI MODE AVAILABLE")
    print("="*60)
    print("You can still use metaprivBIDS via command-line interface:")
    print("\nExample Python code:")
    print("```python")
    print("from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic")
    print("metapriv = metaprivBIDS_core_logic()")
    print("data_info = metapriv.load_data('path/to/your/data.csv')")
    print("print(data_info['column_types'])")
    print("```")
    
    try:
        from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
        print("\n✓ metaprivBIDS core logic is available for CLI use!")
    except ImportError as e:
        print(f"\n✗ Error importing core logic: {e}")


if __name__ == "__main__":
    main()
