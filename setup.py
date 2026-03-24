#!/usr/bin/env python3
"""
CRTV Payslip System - cx_Freeze Setup
Creates a professional installer package
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies required for the application
build_exe_options = {
    "packages": [
        "tkinter", 
        "ttkbootstrap",
        "pandas", 
        "openpyxl",
        "PyPDF2", 
        "reportlab",
        "Pillow",
        "smtplib",
        "email",
        "os",
        "io",
        "re"
    ],
    "excludes": ["matplotlib", "numpy", "scipy"],
    "include_files": [
        ("input/", "input/"),
        ("output/", "output/"),
        ("logs/", "logs/"),
        ("services/", "services/"),
        ("ui/", "ui/"),
        ("logger.py", "logger.py"),
        ("requirements.txt", "requirements.txt")
    ],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Base configuration for Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # This prevents console window from appearing

setup(
    name="CRTV Payslip Distribution System",
    version="1.0.0",
    description="Automated payslip distribution system for CRTV",
    author="CRTV IT Department",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "run_ui.py",
            base=base,
            target_name="CRTV-Payslip-System.exe",
            icon=None,  # You can add an icon file here if you have one
            shortcut_name="CRTV Payslip System",
            shortcut_dir="Desktop"
        )
    ]
)
