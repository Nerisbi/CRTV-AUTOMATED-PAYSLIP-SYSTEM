#!/usr/bin/env python3
"""
Simple test to check if the UI can be created
"""

import sys
import os

print("=== CRTV Payslip System Test ===")
print(f"Python: {sys.version}")
print(f"Directory: {os.getcwd()}")

try:
    # Test basic imports
    import tkinter as tk
    print("SUCCESS: tkinter imported")
    
    from tkinter import filedialog, messagebox
    print("SUCCESS: tkinter.filedialog imported")
    
    # Test importing the UI
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ui.fixed_compact_ui import FixedCompactUI
    print("SUCCESS: UI imported successfully")
    
    # Test creating the UI
    print("Creating UI...")
    app = FixedCompactUI()
    print("SUCCESS: UI created successfully")
    
    # Show a simple window to test
    print("Showing test window...")
    app.root.after(2000, app.root.quit)  # Close after 2 seconds
    app.run()
    print("SUCCESS: UI test completed successfully")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")

print("=== Test Complete ===")
