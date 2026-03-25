#!/usr/bin/env python3
"""
CRTV Animated Payslip System Launcher
Launches with professional loading animation
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.simple_animated_ui import main
    print("Starting CRTV Payslip System with Animation...")
    main()
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install pandas openpyxl PyPDF2 reportlab pillow")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error starting application: {e}")
    input("Press Enter to exit...")
