#!/usr/bin/env python3
"""
Simple debug script to check CRTV 01.pdf content
"""

import os
from PyPDF2 import PdfReader

def check_pdf():
    pdf_path = "input/payslip.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"🔍 Checking: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        print(f"📄 Total pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"\n--- PAGE {i+1} ---")
            print(f"Text length: {len(text)} characters")
            if text.strip():
                print(f"First 300 chars: {text[:300]}")
            else:
                print("❌ No text found on this page")
                
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

if __name__ == "__main__":
    check_pdf()
