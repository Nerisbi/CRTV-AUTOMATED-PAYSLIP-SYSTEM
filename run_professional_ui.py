#!/usr/bin/env python3
"""
CRTV Professional Payslip System Launcher
Launches the professional UI for director presentation
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.fixed_compact_ui import FixedCompactUI
    print("Starting CRTV Professional Payslip System...")
    
    app = FixedCompactUI()
    app.run()
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install pandas openpyxl PyPDF2 reportlab pillow")
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
