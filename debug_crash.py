#!/usr/bin/env python3
"""
Debug the crash issue step by step
"""

print("=== CRASH DEBUG ===")
print("Step 1: Testing basic imports...")

try:
    import tkinter as tk
    print("SUCCESS: tkinter imported")
except Exception as e:
    print(f"ERROR: tkinter failed: {e}")
    exit(1)

try:
    from tkinter import ttk, filedialog, messagebox
    print("SUCCESS: tkinter components imported")
except Exception as e:
    print(f"ERROR: tkinter components failed: {e}")
    exit(1)

try:
    import os
    print("SUCCESS: os imported")
except Exception as e:
    print(f"ERROR: os failed: {e}")
    exit(1)

try:
    import pandas as pd
    print("SUCCESS: pandas imported")
except Exception as e:
    print(f"ERROR: pandas failed: {e}")
    exit(1)

try:
    from datetime import datetime
    print("SUCCESS: datetime imported")
except Exception as e:
    print(f"ERROR: datetime failed: {e}")
    exit(1)

print("\nStep 2: Testing UI import...")

try:
    from ui.fixed_compact_ui import FixedCompactUI
    print("SUCCESS: UI class imported")
except Exception as e:
    print(f"ERROR: UI import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 3: Testing UI creation...")

try:
    app = FixedCompactUI()
    print("SUCCESS: UI instance created")
except Exception as e:
    print(f"ERROR: UI creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 4: Testing UI window creation...")

try:
    # Try to access the root window
    root = app.root
    print("SUCCESS: Root window accessible")
    print(f"Window title: {root.title()}")
except Exception as e:
    print(f"ERROR: Root window access failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 5: All tests passed!")
print("The crash might be happening when app.run() is called.")
print("This could be due to:")
print("- Missing display/graphics drivers")
print("- Tkinter display issues")
print("- System-specific problems")

print("\nTry running: python -c \"from ui.fixed_compact_ui import FixedCompactUI; app = FixedCompactUI(); print('UI ready')\"")
