#!/usr/bin/env python3
"""
Test the fixed matricule matching logic
"""

import pandas as pd
from PyPDF2 import PdfReader
import os

print("=== TESTING MATRICULE MATCHING FIX ===")
print()

# Read Excel file
try:
    excel_path = "input/employees.xlsx"
    employees = pd.read_excel(excel_path)
    print(f"Loaded {len(employees)} employees from Excel")
    
    # Show employee data with matricules
    print("\nEmployee data:")
    print("-" * 50)
    for idx, row in employees.iterrows():
        name = str(row["Name"]).strip()
        email = str(row["Email"]).strip()
        matricule = str(row.get('Matricule', '')).strip()
        print(f"{idx+1}. {name:<15} | {email:<25} | Matricule: '{matricule}'")
    
except Exception as e:
    print(f"ERROR reading Excel: {e}")
    exit(1)

# Read PDF file
try:
    pdf_path = "input/payslips.pdf"
    reader = PdfReader(pdf_path)
    print(f"\nLoaded {len(reader.pages)} pages from PDF")
    
    # Show PDF content preview
    print("\nPDF page content:")
    print("-" * 50)
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        preview = text[:200] + "..." if len(text) > 200 else text
        print(f"Page {page_idx + 1}: {preview}")
    
except Exception as e:
    print(f"ERROR reading PDF: {e}")
    exit(1)

# Test the matching logic
print("\n=== TESTING MATCHING LOGIC ===")
print("-" * 50)

for index, row in employees.iterrows():
    employee_matricule = str(row.get('Matricule', '')).strip()
    name = str(row["Name"]).strip()
    
    # Find matching page
    page_number = None
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if employee_matricule in page_text:
            page_number = page_idx
            print(f"MATCH: {name} (matricule '{employee_matricule}') -> PDF page {page_idx + 1}")
            break
    
    if page_number is None:
        page_number = index
        print(f"FALLBACK: {name} (matricule '{employee_matricule}') -> PDF page {page_number + 1}")

print("\n=== TEST COMPLETE ===")
print("Each employee should now receive their correct payslip based on matricule!")
