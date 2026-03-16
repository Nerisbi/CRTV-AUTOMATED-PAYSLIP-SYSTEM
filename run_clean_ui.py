#!/usr/bin/env python3
"""
CRTV Payslip System - Clean Professional UI Launcher
Professional interface for payslip distribution without simulation modes
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.app_clean import CRTVPayslipApp
    
    print("🚀 Starting CRTV Automated Payslip Distribution System...")
    print("📋 Loading professional UI...")
    
    app = CRTVPayslipApp()
    app.mainloop()
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n📦 Please install required packages:")
    print("   pip install -r requirements.txt")
    print("\n🔧 If ttkbootstrap is not found, install it separately:")
    print("   pip install ttkbootstrap")
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("\n🐛 Please check the error above and try again.")

print("\n👋 Application closed.")
