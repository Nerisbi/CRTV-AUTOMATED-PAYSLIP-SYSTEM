#!/usr/bin/env python3
"""
CRTV Payslip System - Presentation Ready Launcher
Uses the exact same email configuration as your working main.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🚀 Starting CRTV Automated Payslip Distribution System...")
    print("📋 Using production email configuration from main.py...")
    print("📧 Gmail: nerisbi801@gmail.com")
    print("🔐 SMTP: smtp.gmail.com:465")
    print()
    
    from ui.app_clean import CRTVPayslipApp
    
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
