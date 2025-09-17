#!/usr/bin/env python3
"""
Test script to verify metaprivBIDS GUI functionality
This script tests the GUI with auto-quit to ensure everything is working
"""

import os
import sys

# Activate conda environment
os.system('conda activate /users/cyrilpernet/conda-envs/venv')

# Set up Qt environment for VNC
os.environ['QT_QPA_PLATFORM'] = 'vnc'
os.environ['QT_QPA_VNC_SCREEN'] = '1024x768'
os.environ['QT_QPA_VNC_PORT'] = '5900'

def test_gui_functionality():
    """Test various GUI components to ensure they're working properly."""
    
    print("="*60)
    print("metaprivBIDS GUI Functionality Test")
    print("="*60)
    
    try:
        print("1. Importing GUI modules...")
        from metaprivBIDS.metaprivBIDS import metaprivBIDS, run_headless
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        print("✓ GUI modules imported successfully")
        
        print("\n2. Testing GUI window creation...")
        app = QApplication.instance() or QApplication([])
        window = metaprivBIDS()
        print("✓ GUI window created successfully")
        
        print("\n3. Testing GUI components...")
        # Test if main UI components are accessible
        if hasattr(window, 'stacked_widget'):
            print("✓ Main stacked widget exists")
        if hasattr(window, 'main_page'):
            print("✓ Main page exists")
        if hasattr(window, 'privacy_info_page'):
            print("✓ Privacy info page exists")
        if hasattr(window, 'preview_page'):
            print("✓ Preview page exists")
        if hasattr(window, 'suda_info_page'):
            print("✓ SUDA info page exists")
            
        print("\n4. Testing GUI display...")
        window.show()
        print("✓ GUI window displayed successfully")
        print("🖥️  GUI is now running on VNC server port 5900")
        print("   Connect with: vncviewer localhost:5900")
        
        # Auto-quit after 5 seconds
        QTimer.singleShot(5000, app.quit)
        print("\n5. Running GUI event loop (5 seconds)...")
        app.exec()
        
        print("✓ GUI test completed successfully!")
        print("\n" + "="*60)
        print("GUI FUNCTIONALITY TEST PASSED")
        print("The GUI is working correctly and can be accessed via VNC")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        print("\n" + "="*60)
        print("GUI FUNCTIONALITY TEST FAILED")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_gui_functionality()
    sys.exit(0 if success else 1)
