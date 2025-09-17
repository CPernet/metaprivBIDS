#!/usr/bin/env python3
"""
Direct GUI Launch Test - Shows the actual GUI state
"""

import os
import sys

def launch_gui_directly():
    """Launch GUI and keep it running for manual verification."""
    
    print("="*60)
    print("DIRECT GUI LAUNCH TEST")
    print("="*60)
    
    # Set up VNC environment
    os.environ['QT_QPA_PLATFORM'] = 'vnc'
    os.environ['QT_QPA_VNC_SCREEN'] = '1024x768'
    os.environ['QT_QPA_VNC_PORT'] = '5900'
    
    try:
        print("1. Setting up Qt environment...")
        print(f"   Platform: {os.environ['QT_QPA_PLATFORM']}")
        print(f"   Screen: {os.environ['QT_QPA_VNC_SCREEN']}")
        print(f"   Port: {os.environ['QT_QPA_VNC_PORT']}")
        
        print("\n2. Importing GUI components...")
        from metaprivBIDS.metaprivBIDS import metaprivBIDS
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        print("   ✓ Imports successful")
        
        print("\n3. Creating QApplication...")
        app = QApplication.instance() or QApplication([])
        print("   ✓ QApplication created")
        
        print("\n4. Creating main window...")
        window = metaprivBIDS()
        print("   ✓ Main window created")
        
        print("\n5. Checking window properties...")
        print(f"   Window title: {window.windowTitle()}")
        print(f"   Window size: {window.size().width()}x{window.size().height()}")
        print(f"   Window visible: {window.isVisible()}")
        
        print("\n6. Displaying window...")
        window.show()
        print(f"   Window visible after show(): {window.isVisible()}")
        
        print("\n7. Checking GUI components...")
        if hasattr(window, 'stacked_widget'):
            print("   ✓ Stacked widget exists")
            print(f"   Current page index: {window.stacked_widget.currentIndex()}")
            print(f"   Total pages: {window.stacked_widget.count()}")
        
        if hasattr(window, 'main_page'):
            print("   ✓ Main page exists")
        if hasattr(window, 'privacy_info_page'):
            print("   ✓ Privacy info page exists")
        if hasattr(window, 'preview_page'):
            print("   ✓ Preview page exists")
        if hasattr(window, 'suda_info_page'):
            print("   ✓ SUDA info page exists")
            
        print("\n" + "="*60)
        print("GUI LAUNCH STATUS: SUCCESS")
        print("="*60)
        print("🖥️  VNC Server should be running on port 5900")
        print("   To view GUI: vncviewer localhost:5900")
        print("   Or connect with any VNC client to port 5900")
        print()
        print("GUI will run for 30 seconds for manual verification...")
        print("Check your VNC client to see if the interface is visible.")
        
        # Set up a timer to quit after 30 seconds
        QTimer.singleShot(30000, app.quit)  # 30 seconds
        
        print("\nStarting Qt event loop...")
        app.exec()
        
        print("\n✓ GUI session completed")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = launch_gui_directly()
    if success:
        print("\n✅ GUI test completed - check VNC client for visual confirmation")
    else:
        print("\n❌ GUI test failed")
    sys.exit(0 if success else 1)
