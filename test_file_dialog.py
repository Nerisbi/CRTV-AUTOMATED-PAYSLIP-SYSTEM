#!/usr/bin/env python3
"""
Test script to verify file dialog functionality
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os

def test_file_dialog():
    """Test the file dialog functionality"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        print("🧪 Testing file dialog...")
        
        # Test PDF file dialog
        print("📄 Testing PDF file selection...")
        pdf_file = filedialog.askopenfilename(
            parent=root,
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if pdf_file:
            print(f"✅ PDF selected: {pdf_file}")
        else:
            print("❌ No PDF selected")
        
        # Test Excel file dialog
        print("📊 Testing Excel file selection...")
        excel_file = filedialog.askopenfilename(
            parent=root,
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if excel_file:
            print(f"✅ Excel selected: {excel_file}")
        else:
            print("❌ No Excel selected")
        
        # Test Image file dialog
        print("🖼️ Testing Image file selection...")
        image_file = filedialog.askopenfilename(
            parent=root,
            title="Select Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if image_file:
            print(f"✅ Image selected: {image_file}")
        else:
            print("❌ No Image selected")
        
        messagebox.showinfo("Test Complete", "File dialog test completed!\n\nCheck the console for results.")
        
    except Exception as e:
        print(f"❌ Error testing file dialog: {e}")
        messagebox.showerror("Error", f"File dialog test failed: {str(e)}")
    
    finally:
        root.destroy()

if __name__ == "__main__":
    test_file_dialog()
