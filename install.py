#!/usr/bin/env python3
"""Interactive installer for metaprivBIDS.

This script prompts the user whether the optional ``pygraphviz``
dependency should be installed.  ``pygraphviz`` is used for
advanced graph visualisation but can be troublesome to install
on Windows systems.  If the user declines, installation proceeds
without it.
"""

import platform
import subprocess
import sys
import os


def check_qt_installed():
    """Check if Qt and PyQt are already installed."""
    try:
        import PyQt6
        print("PyQt6 is already installed.")
        return True
    except ImportError:
        pass
    
    try:
        import PyQt5
        print("PyQt5 is already installed.")
        return True
    except ImportError:
        pass
    
    return False


def install_qt_dependencies():
    """Install Qt dependencies through conda to resolve platform plugin issues."""
    if check_qt_installed():
        print("Qt/PyQt already available, skipping installation.")
        return
    
    print("Installing Qt dependencies through conda...")
    try:
        # Install core Qt packages that are more likely to be available
        subprocess.check_call([
            "conda", "install", "-y", "-c", "conda-forge",
            "qt-main", "pyqt"
        ])
        print("Core Qt dependencies installed successfully.")
        
        # Try to install additional X11 support packages if available
        try:
            subprocess.check_call([
                "conda", "install", "-y", "-c", "conda-forge",
                "libxcb", "xcb-util", "libxkbcommon"
            ])
            print("Additional X11 support packages installed.")
        except subprocess.CalledProcessError:
            print("Some X11 packages not available via conda, but core Qt should work.")
            
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install Qt dependencies via conda: {e}")
        print("You may need to install system packages manually or use a different display backend.")
        print("The application might still work with PySide6 which is already installed.")


def check_setuptools_version():
    """Check if setuptools version needs to be fixed."""
    try:
        import setuptools
        version = setuptools.__version__
        major_version = int(version.split('.')[0])
        if major_version >= 81:
            return False  # Needs fixing
        else:
            print(f"Setuptools version {version} is compatible (< 81).")
            return True  # Already compatible
    except (ImportError, ValueError, AttributeError):
        return False  # Needs fixing


def fix_pkg_resources():
    """Fix pkg_resources deprecation warning by pinning setuptools version."""
    if check_setuptools_version():
        print("Setuptools version is already compatible, skipping fix.")
        return
    
    print("Fixing pkg_resources deprecation warning...")
    try:
        # Pin setuptools to avoid pkg_resources deprecation
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools<81"])
        print("Setuptools pinned to compatible version.")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to pin setuptools: {e}")


def set_qt_environment():
    """Set Qt environment variables for proper plugin loading."""
    print("Setting Qt environment variables...")
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
        else:
            print("Warning: Could not find Qt plugin directory.")
        
        # Set fallback platform options
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        
        # Add library path for better Qt loading
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        lib_path = os.path.join(conda_prefix, 'lib')
        if lib_path not in current_ld_path:
            os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{current_ld_path}" if current_ld_path else lib_path
        
    else:
        print("Warning: CONDA_PREFIX not found, Qt environment may not be properly configured.")


def main() -> None:
    system = platform.system()
    
    # Fix pkg_resources issue first
    fix_pkg_resources()
    
    # Install Qt dependencies
    if system == "Linux":
        install_qt_dependencies()
        set_qt_environment()
    
    # Handle pygraphviz installation
    prompt = (
        "Install optional 'pygraphviz' dependency for advanced graph "
        "visualization? [y/N]: "
    )
    if system == "Windows":
        print("pygraphviz often requires additional build tools on Windows.")
    choice = input(prompt).strip().lower()
    extra = "[pygraphviz]" if choice in {"y", "yes"} else ""
    if extra:
        print("Including pygraphviz in installation.")
    else:
        print("Skipping pygraphviz installation.")
    
    # Install the main package
    subprocess.check_call([sys.executable, "-m", "pip", "install", f".{extra}"])
    
    print("\n" + "="*70)
    print("INSTALLATION COMPLETE!")
    print("="*70)
    print("\n🎯 RECOMMENDED USAGE (in order of reliability):")
    print("\n1. 🛡️  SAFE LAUNCHER (Recommended):")
    print("   python run_metaprivBIDS_safe.py")
    print("   → Tests Qt compatibility, provides fallbacks")
    
    print("\n2. 💻 CLI-ONLY MODE (Most Reliable):")
    print("   python test_cli.py")
    print("   → Full functionality, no GUI dependencies")
    
    print("\n3. 🖥️  DIRECT GUI (May hang on some systems):")
    print("   python run_metaprivBIDS.py")
    print("   → Direct GUI launch, use Ctrl+C if hangs")
    
    print("\n🔧 If GUI hangs, try these Qt platform fallbacks:")
    print("   QT_QPA_PLATFORM=minimal python run_metaprivBIDS.py")
    print("   QT_QPA_PLATFORM=offscreen python run_metaprivBIDS.py")
    
    print("\n📚 Quick reference: See QUICK_START.md")
    print("\n✅ Issues resolved:")
    print("   • pkg_resources deprecation warning → Fixed")
    print("   • Qt platform compatibility issues → Multiple fallback options")
    print("="*70)


if __name__ == "__main__":
    main()
