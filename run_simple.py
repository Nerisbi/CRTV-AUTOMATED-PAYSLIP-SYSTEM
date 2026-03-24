#!/usr/bin/env python3
"""
CRTV Payslip System - Simple Launcher
Basic launcher that just starts the application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the main app directly
    import main
    
    print("Starting CRTV Automated Payslip Distribution System...")
    
    # Run the main application
    main.main()
    
except ImportError as e:
    print("Import Error: {}".format(str(e)))
    print("\nPlease install required packages:")
    print("   pip install -r requirements.txt")
    
except Exception as e:
    print("Error starting application: {}".format(str(e)))
    print("\nPlease check the error above and try again.")
