#!/usr/bin/env python3
"""
Interactive GUI Test for metaprivBIDS
This script launches the actual GUI and asks the user to verify it's working correctly.
"""

import os
import sys
import time

def test_interactive_gui():
    """Launch the GUI and ask user to verify it's working."""
    
    print("="*70)
    print("metaprivBIDS Interactive GUI Test")
    print("="*70)
    print()
    print("This test will launch the actual GUI and ask you to verify it's working.")
    print("The GUI will run on VNC server port 5900.")
    print()
    print("To view the GUI:")
    print("1. Connect with VNC client to: localhost:5900")
    print("2. Or use command: vncviewer localhost:5900")
    print()
    
    input("Press Enter when you're ready to launch the GUI...")
    
    try:
        print("\n" + "="*70)
        print("LAUNCHING GUI...")
        print("="*70)
        
        # Set up environment for GUI launch
        os.environ['QT_QPA_PLATFORM'] = 'vnc'
        os.environ['QT_QPA_VNC_SCREEN'] = '1024x768'
        os.environ['QT_QPA_VNC_PORT'] = '5900'
        
        print("Importing GUI modules...")
        from metaprivBIDS.metaprivBIDS import metaprivBIDS
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        print("✓ GUI modules imported successfully")
        
        print("Creating Qt application...")
        app = QApplication.instance() or QApplication([])
        
        print("Creating main window...")
        window = metaprivBIDS()
        
        print("Displaying GUI window...")
        window.show()
        
        print("✓ GUI launched successfully!")
        print()
        print("🖥️  VNC Server is running on port 5900")
        print("   Connect with: vncviewer localhost:5900")
        print()
        print("The GUI should now be visible in your VNC client.")
        print()
        
        # Ask user to verify GUI is working
        print("="*70)
        print("USER VERIFICATION")
        print("="*70)
        print()
        print("Please check the following in your VNC client:")
        print("1. Can you see the metaprivBIDS window?")
        print("2. Can you see the main interface with buttons?")
        print("3. Are the buttons and text clearly visible?")
        print("4. Can you click on buttons (try 'Privacy Info' or 'Preview')?")
        print()
        
        # Keep GUI running until user responds
        response = input("Is the GUI working correctly? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            print()
            print("✅ SUCCESS: GUI is working correctly!")
            print()
            print("Additional test: Try these features in the GUI:")
            print("- Click 'Privacy Info' button")
            print("- Click 'Preview' button")
            print("- Click 'SUDA Info' button")
            print("- Navigate between different pages")
            print()
            
            more_tests = input("Would you like to test GUI navigation? (y/n): ").strip().lower()
            
            if more_tests in ['y', 'yes']:
                print()
                print("🔍 NAVIGATION TEST")
                print("Try clicking different buttons and navigating between pages.")
                print("Check if all pages load correctly and buttons respond.")
                print()
                input("Press Enter when you've finished testing navigation...")
                
                final_result = input("Did all GUI features work correctly? (y/n): ").strip().lower()
                
                if final_result in ['y', 'yes']:
                    print()
                    print("🎉 FULL SUCCESS: metaprivBIDS GUI is fully functional!")
                    success = True
                else:
                    print()
                    print("⚠️  PARTIAL SUCCESS: GUI launches but some features may have issues")
                    success = False
            else:
                success = True
        else:
            print()
            print("❌ FAILURE: GUI is not working correctly")
            print("Common issues to check:")
            print("- VNC client is connected to the correct port (5900)")
            print("- VNC client settings are correct")
            print("- Screen resolution is appropriate (1024x768)")
            success = False
        
        print()
        input("Press Enter to close the GUI...")
        
        # Close the application
        app.quit()
        
        print("✓ GUI closed successfully")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the interactive test."""
    
    print("Activating conda environment...")
    os.system('source /users/cyrilpernet/conda-envs/venv/bin/activate')
    
    success = test_interactive_gui()
    
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if success:
        print("✅ metaprivBIDS GUI is working correctly!")
        print("   The application can be launched using:")
        print("   conda activate /users/cyrilpernet/conda-envs/venv")
        print("   python run_metaprivBIDS_safe.py")
        print("   (Connect to VNC on port 5900 to view)")
    else:
        print("❌ metaprivBIDS GUI has issues that need to be resolved")
        print("   Check the error messages above for debugging information")
    
    print("="*70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
