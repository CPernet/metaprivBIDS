#!/usr/bin/env python3
"""
Test Qt fixes for metaprivBIDS GUI.
This test file verifies that the Qt fixes are working properly.
"""

import pytest
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set up Qt environment variables as per Fix A
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_OPENGL", "software")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication

# Import after setting environment
from metaprivBIDS.metaprivBIDS import metaprivBIDS, run_headless


def test_headless_environment_detection():
    """Test that headless environment is properly detected"""
    # Check if the environment variables are set correctly
    assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"
    assert os.environ.get("QT_OPENGL") == "software"


def test_qt_platform_name():
    """Test that QGuiApplication correctly identifies the platform"""
    app = QApplication.instance() or QApplication([])
    platform_name = QGuiApplication.platformName()
    print(f"Platform name: {platform_name}")
    assert platform_name in {"offscreen", "minimal"}


def test_gui_smoke_with_pytest_qt(qtbot):
    """Test GUI smoke test using pytest-qt (Fix B)"""
    win = metaprivBIDS()
    qtbot.addWidget(win)
    win.show()
    
    # Basic widget tests
    assert win.windowTitle() == 'MetaprivBIDS'
    assert win.isVisible()
    
    # Test that the stacked widget exists
    assert win.stacked_widget is not None
    
    # Test that main components exist
    assert hasattr(win, 'main_page')
    assert hasattr(win, 'preview_page')
    assert hasattr(win, 'privacy_info_page')
    assert hasattr(win, 'suda_info_page')


def test_run_headless_function():
    """Test the run_headless function (Fix A/B combination)"""
    # This should not hang and should complete quickly
    window = run_headless()
    
    # Basic assertions
    assert window is not None
    assert isinstance(window, metaprivBIDS)
    assert window.windowTitle() == 'MetaprivBIDS'


def test_splash_screen_headless_handling():
    """Test that splash screen is handled properly in headless mode"""
    app = QApplication.instance() or QApplication([])
    window = metaprivBIDS()
    
    # Check if the platform is detected as offscreen
    is_offscreen = QGuiApplication.platformName() in {"offscreen", "minimal"}
    assert is_offscreen, "Should be running in offscreen mode"
    
    # The splash screen should be handled gracefully
    window.show_splash_screen()
    
    # Should not crash and window should still be functional
    assert window.windowTitle() == 'MetaprivBIDS'


if __name__ == "__main__":
    print("="*60)
    print("Qt Fixes Test Suite")
    print("="*60)
    
    # Run the tests
    try:
        test_headless_environment_detection()
        print("✓ Environment detection test passed")
        
        test_qt_platform_name()
        print("✓ Qt platform name test passed")
        
        test_run_headless_function()
        print("✓ Run headless function test passed")
        
        test_splash_screen_headless_handling()
        print("✓ Splash screen handling test passed")
        
        print("\n✓ All Qt fixes tests passed!")
        print("The GUI should now work better in headless environments.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
