#!/usr/bin/env python3
"""
Minimal GUI test without R dependencies
"""

import os
import sys

# Setup Qt environment
os.environ.setdefault("QT_QPA_PLATFORM", "vnc")

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication

class MinimalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MetaprivBIDS - Minimal Test')
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF;")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add some basic widgets
        title = QLabel("MetaprivBIDS GUI Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)
        
        platform_info = QLabel(f"Qt Platform: {QGuiApplication.platformName()}")
        platform_info.setStyleSheet("color: #FFFFFF; padding: 10px;")
        layout.addWidget(platform_info)
        
        button = QPushButton("Test Button")
        button.setStyleSheet("""
            QPushButton {
                background-color: #94127e; 
                color: white; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 5px; 
                padding: 10px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #b0529c;
            }
        """)
        button.clicked.connect(lambda: print("Button clicked!"))
        layout.addWidget(button)
        
        status = QLabel("✓ GUI is working!")
        status.setStyleSheet("color: #00FF00; padding: 10px;")
        layout.addWidget(status)

def main():
    platform = os.environ.get("QT_QPA_PLATFORM", "").lower()
    print(f"Starting GUI with platform: {platform}")
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MinimalGUI()
    window.show()
    
    # Auto-quit after 10 seconds for testing
    QTimer.singleShot(10000, lambda: (print("Auto-quitting..."), app.quit()))
    
    print("GUI should be visible now...")
    print("QVncServer will be created on port 5900")
    print("Application will auto-quit in 10 seconds...")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
