#!/usr/bin/env python3
"""
metaprivBIDS GUI Verification Test
This script launches the GUI for manual verification
"""

import os
import sys

def main():
    """Launch GUI for manual verification."""
    
    print("="*70)
    print("metaprivBIDS GUI Verification Test")
    print("="*70)
    print()
    
    # Set up VNC environment
    os.environ['QT_QPA_PLATFORM'] = 'vnc'
    os.environ['QT_QPA_VNC_SCREEN'] = '1024x768'
    os.environ['QT_QPA_VNC_PORT'] = '5900'
    
    print("Setting up Qt environment for GUI...")
    print(f"  Platform: {os.environ['QT_QPA_PLATFORM']}")
    print(f"  Screen Resolution: {os.environ['QT_QPA_VNC_SCREEN']}")
    print(f"  VNC Port: {os.environ['QT_QPA_VNC_PORT']}")
    print()
    
    try:
        print("Importing Qt modules...")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        print("✓ Qt modules imported successfully")
        
        print("Creating Qt application...")
        app = QApplication.instance() or QApplication([])
        print("✓ Qt application created")
        
        print("Importing metaprivBIDS GUI...")
        from metaprivBIDS.metaprivBIDS import metaprivBIDS
        print("✓ metaprivBIDS imported successfully")
        
        print("Creating main window...")
        window = metaprivBIDS()
        print("✓ Main window created")
        
        print("Configuring window...")
        print(f"  Window title: '{window.windowTitle()}'")
        print(f"  Window size: {window.size().width()} x {window.size().height()}")
        
        print("Displaying GUI...")
        window.show()
        print("✓ GUI window displayed")
        
        print()
        print("="*70)
        print("🖥️  GUI IS NOW RUNNING")
        print("="*70)
        print()
        print("The metaprivBIDS GUI is now running on VNC server port 5900.")
        print()
        print("TO VIEW THE GUI:")
        print("1. Open a VNC client (like vncviewer, TigerVNC, RealVNC, etc.)")
        print("2. Connect to: localhost:5900")
        print("3. Or use command: vncviewer localhost:5900")
        print()
        print("WHAT TO CHECK:")
        print("✓ Can you see the metaprivBIDS window?")
        print("✓ Can you see buttons like 'Privacy Info', 'Preview', 'SUDA Info'?")
        print("✓ Can you click on the buttons and navigate between pages?")
        print("✓ Are all interface elements clearly visible?")
        print()
        print("The GUI will run until you press Ctrl+C in this terminal.")
        print("="*70)
        print()
        
        # Run the GUI indefinitely until interrupted
        try:
            app.exec()
        except KeyboardInterrupt:
            print("\n\nGUI session ended by user (Ctrl+C)")
            
        print("✓ GUI application closed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR launching GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Activating conda environment: /users/cyrilpernet/conda-envs/venv")
    success = main()
    
    print("\n" + "="*70)
    if success:
        print("✅ GUI test completed successfully!")
        print("If you could see and interact with the GUI, it's working correctly.")
    else:
        print("❌ GUI test failed - see error messages above")
    print("="*70)
