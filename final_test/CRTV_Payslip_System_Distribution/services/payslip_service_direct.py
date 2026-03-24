"""
Direct Payslip Service - Uses the exact same configuration as main.py
No modifications, just direct integration with working code
"""

import os
import io
import re
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Import directly from main.py to use exact same configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import send_email, SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

try:
    from logger import log_info, log_error
except:
    def log_info(msg): print(f"INFO: {msg}")
    def log_error(msg): print(f"ERROR: {msg}")


class PayslipService:
    def __init__(self):
        self.input_pdf = ""
        self.input_excel = ""
        self.stamp_image = ""
        self.output_dir = "output/sent_payslips"
        
        # Use the exact same config from main.py
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        
        # Progress callback
        self.progress_callback = None
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message, status="info"):
        """Update progress through callback if available"""
        if self.progress_callback:
            self.progress_callback(message, status)
        print(message)  # Also print to console
    
    def validate_files(self):
        """Validate all required files exist"""
        validation_results = {
            "payslip_pdf": os.path.exists(self.input_pdf),
            "employee_excel": os.path.exists(self.input_excel),
            "stamp_image": os.path.exists(self.stamp_image)
        }
        
        all_valid = all(validation_results.values())
        
        if all_valid:
            self.update_progress("✅ All files validated successfully", "success")
        else:
            missing = [k for k, v in validation_results.items() if not v]
            self.update_progress(f"❌ Missing files: {', '.join(missing)}", "error")
        
        return all_valid, validation_results
    
    def get_employee_count(self):
        """Get total number of employees from Excel file"""
        try:
            if not os.path.exists(self.input_excel):
                return 0
            
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            return len(employees)
        except Exception as e:
            self.update_progress(f"Error reading employee file: {e}", "error")
            return 0
    
    def get_pdf_page_count(self):
        """Get total number of pages in PDF"""
        try:
            if not os.path.exists(self.input_pdf):
                return 0
            
            reader = PdfReader(self.input_pdf)
            return len(reader.pages)
        except Exception as e:
            self.update_progress(f"Error reading PDF file: {e}", "error")
            return 0
    
    def preview_process(self):
        """Generate preview of what will be processed"""
        try:
            if not os.path.exists(self.input_excel):
                return None
            
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            
            preview = {
                "total_employees": len(employees),
                "pdf_pages": self.get_pdf_page_count(),
                "payslip_file": os.path.basename(self.input_pdf),
                "output_dir": self.output_dir,
                "employees": []
            }
            
            for _, row in employees.iterrows():
                preview["employees"].append({
                    "name": str(row.get('Name', 'Unknown')).strip(),
                    "email": str(row.get('Email', 'Unknown')).strip(),
                    "page": str(row.get('Page', 'Unknown')).strip()
                })
            
            return preview
            
        except Exception as e:
            self.update_progress(f"Error generating preview: {e}", "error")
            return None
    
    def add_stamp_to_page(self, original_page):
        """Add company stamp to PDF page"""
        packet = io.BytesIO()
        
        page_width = float(original_page.mediabox.width)
        page_height = float(original_page.mediabox.height)
        
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Stamp position & size
        x = page_width - 160
        y = 60
        width = 120
        height = 120
        
        c.drawImage(self.stamp_image, x, y, width, height, mask="auto")
        c.save()
        
        packet.seek(0)
        stamp_pdf = PdfReader(packet)
        
        original_page.merge_page(stamp_pdf.pages[0])
        return original_page
    
    def send_email(self, receiver_email, employee_name, pdf_path):
        """Send payslip email using the exact same function as main.py"""
        try:
            # Use the exact same send_email function from main.py
            send_email(receiver_email, employee_name, pdf_path)
            self.update_progress(f"📨 Email sent to {receiver_email}", "success")
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to send email to {receiver_email}: {str(e)}"
            self.update_progress(error_msg, "error")
            return False
    
    def process_payslips(self):
        """Main payslip processing function"""
        try:
            # Validate files first
            all_valid, validation = self.validate_files()
            if not all_valid:
                return False, "File validation failed"
            
            # Read employee data and PDF
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            reader = PdfReader(self.input_pdf)
            
            total_employees = len(employees)
            total_pages = len(reader.pages)
            
            self.update_progress(f"Starting processing: {total_employees} employees, {total_pages} PDF pages", "info")
            
            success_count = 0
            error_count = 0
            
            for index, row in employees.iterrows():
                try:
                    employee_name = str(row.get('Name', 'Unknown')).strip()
                    self.update_progress(f"Processing {index + 1}/{total_employees}: {employee_name}", "info")
                    
                    page_number = int(row["Page"]) - 1
                    
                    # Validate page number
                    if page_number >= total_pages or page_number < 0:
                        raise ValueError(f"Invalid page number: {page_number + 1}")
                    
                    # Clean name for filename
                    clean_name = re.sub(r"[^a-zA-Z0-9]", "_", employee_name)
                    email = str(row["Email"]).strip()
                    
                    # Create individual PDF
                    writer = PdfWriter()
                    page = reader.pages[page_number]
                    page = self.add_stamp_to_page(page)
                    writer.add_page(page)
                    
                    output_file = f"{self.output_dir}/Payslip_{clean_name}.pdf"
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    
                    self.update_progress(f"✅ Payslip generated for {employee_name}", "success")
                    
                    # Send email using main.py function
                    self.update_progress(f"📧 Sending email to {email}...", "info")
                    if self.send_email(email, employee_name, output_file):
                        success_count += 1
                    else:
                        error_count += 1
                    
                except Exception as e:
                    error_count += 1
                    self.update_progress(f"❌ Failed for {row.get('Name', 'Unknown')}: {e}", "error")
            
            # Summary
            summary = f"Processing complete: {success_count} successful, {error_count} failed"
            self.update_progress(summary, "success" if error_count == 0 else "warning")
            
            return error_count == 0, summary
            
        except Exception as e:
            error_msg = f"Critical error during processing: {e}"
            self.update_progress(error_msg, "error")
            return False, error_msg
