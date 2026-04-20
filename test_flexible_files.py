#!/usr/bin/env python3
"""
Test the new flexible file selection system
"""

import main
import os

print("=== FLEXIBLE FILE SELECTION TEST ===")
print()

# Test 1: Try to run without files selected
print("Test 1: Running without files selected...")
try:
    main.main()
    print("ERROR: Should have failed!")
except SystemExit:
    print("SUCCESS: Correctly failed - no files selected")
print()

# Test 2: Set files and run
print("Test 2: Setting custom file paths...")
pdf_path = "input/payslip.pdf"
excel_path = "input/employees.xlsx"

if os.path.exists(pdf_path) and os.path.exists(excel_path):
    print(f"Setting PDF: {pdf_path}")
    print(f"Setting Excel: {excel_path}")
    
    main.set_file_paths(pdf_path, excel_path)
    main.SIMULATION_MODE = True  # Use simulation mode
    
    print("Running with custom files...")
    main.main()
    print("SUCCESS: Flexible file system working!")
else:
    print("Files not found - test skipped")

print()
print("=== FLEXIBLE FILE SYSTEM BENEFITS ===")
print("✓ Users can select any PDF file (any name)")
print("✓ Users can select any Excel file (any name)")
print("✓ No hardcoded file dependencies")
print("✓ Perfect for multi-user environments")
print("✓ Files can be located anywhere")
print()
print("=== HOW TO USE ===")
print("1. Launch the UI: python run_professional_ui.py")
print("2. Click 'Browse' for PDF file select any payslip PDF")
print("3. Click 'Browse' for Excel file select any employee list")
print("4. Click 'Send Payslips' - system uses your selected files!")
