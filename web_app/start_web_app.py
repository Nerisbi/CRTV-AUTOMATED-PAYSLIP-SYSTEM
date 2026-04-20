#!/usr/bin/env python3
"""
CRTV Payslip Distribution System - Web Application Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'PyPDF2', 'pandas', 'reportlab',
        'Pillow', 'python-multipart'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install fastapi uvicorn PyPDF2 pandas reportlab Pillow python-multipart")
        return False
    
    print("✅ All dependencies are installed")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'outputs', 'input']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("📁 Created necessary directories")

def start_web_app():
    """Start the web application"""
    print("\n🚀 Starting CRTV Payslip Distribution System Web Application")
    print("=" * 60)
    print("📱 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Start the FastAPI application
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web application stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting web application: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🔧 CRTV Payslip Distribution System - Web App Launcher")
    print("=" * 55)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    # Start web application
    return start_web_app()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
