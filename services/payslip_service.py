"""
Payslip Service - Backend functionality for UI integration
Handles payslip processing, PDF generation, and email sending
"""

import os
import io
import re
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from logger import log_info, log_error


class PayslipService:
    def __init__(self):
        self.simulation_mode = False  # Always send real emails
        self.payslip_folder = "input/payslips/"
        self.input_excel = "input/employees - 1.xlsx"
        self.stamp_image = "input/Stamp.png"
        self.output_dir = "output/sent_payslips"
        
        # Gmail SMTP config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.email_address = "nerisbi801@gmail.com"
        self.email_password = "qmpp eqym rclo bave"
        
        # Progress callback
        self.progress_callback = None
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_email_connection(self):
        """Test email connection and send test email"""
        try:
            if self.simulation_mode:
                self.update_progress("📧 [SIMULATION] Email connection test skipped", "info")
                return True
                
            self.update_progress("🔧 Testing email connection...", "info")
            
            # Create test message
            msg = EmailMessage()
            msg["Subject"] = "CRTV System Test"
            msg["From"] = "CRTV HR <no-reply@crtv.cm>"
            msg["To"] = self.email_address  # Send to self for testing
            
            msg.set_content(
                "This is a test email from CRTV Payslip System.\\n"
                "If you receive this, email configuration is working correctly.\\n\\n"
                "Regards,\\n"
                "CRTV System"
            )
            
            # Test connection and send
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                self.update_progress("🔐 Connecting to Gmail SMTP...", "info")
                server.login(self.email_address, self.email_password)
                self.update_progress("📤 Sending test email...", "info")
                server.send_message(msg)
            
            self.update_progress("✅ Test email sent successfully!", "success")
            return True
            
        except Exception as e:
            error_msg = f"❌ Email test failed: {str(e)}"
            self.update_progress(error_msg, "error")
            return False
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message, status="info"):
        """Update progress through callback if available"""
        if self.progress_callback:
            self.progress_callback(message, status)
        print(message)  # Also print to console
    
    def validate_files(self):
        """Validate all required files/folders exist"""
        validation_results = {
            "payslip_folder": os.path.exists(self.payslip_folder) and os.path.isdir(self.payslip_folder),
            "employee_excel": os.path.exists(self.input_excel),
            "stamp_image": os.path.exists(self.stamp_image)
        }
        
        # Check if folder contains PDF files
        if validation_results["payslip_folder"]:
            pdf_files = [f for f in os.listdir(self.payslip_folder) if f.lower().endswith('.pdf')]
            validation_results["payslip_folder"] = len(pdf_files) > 0
        
        all_valid = all(validation_results.values())
        
        if all_valid:
            self.update_progress("✅ All files validated successfully", "success")
        else:
            missing = [k for k, v in validation_results.items() if not v]
            self.update_progress(f"❌ Missing files/empty folder: {', '.join(missing)}", "error")
        
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
        """Get total number of PDF files in the folder"""
        try:
            if not os.path.exists(self.payslip_folder) or not os.path.isdir(self.payslip_folder):
                return 0
            
            pdf_files = [f for f in os.listdir(self.payslip_folder) if f.lower().endswith('.pdf')]
            return len(pdf_files)
        except Exception as e:
            self.update_progress(f"Error reading PDF folder: {e}", "error")
            return 0
    
    def preview_process(self):
        """Generate preview of what will be processed - PDF-driven approach"""
        try:
            if not os.path.exists(self.input_excel):
                return None
            
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            
            # Get all PDF files in folder
            pdf_files = [f for f in os.listdir(self.payslip_folder) if f.lower().endswith('.pdf')]
            
            preview = {
                "mode": "PRODUCTION",  # Always production now
                "total_employees": len(employees),
                "pdf_files": len(pdf_files),
                "payslip_folder": self.payslip_folder,
                "output_dir": self.output_dir,
                "pdfs_found": []
            }
            
            self.update_progress("Analyzing PDF files and matching with employees...", "info")
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(self.payslip_folder, pdf_file)
                
                # Extract matricule from PDF
                matricule = self.extract_matricule_from_pdf_content(pdf_path)
                if not matricule:
                    matricule = self.extract_matricule_from_filename(pdf_file)
                
                # Find matching employee
                employee = None
                employee_name = "Unknown"
                email = "Not found"
                match_status = "❌ No matricule found"
                
                if matricule:
                    employee = self.find_employee_by_matricule(matricule, employees)
                    if employee:
                        employee_name = str(employee.get('Name', 'Unknown')).strip()
                        email = str(employee.get('Email', 'Unknown')).strip()
                        match_status = "✅ Match found"
                    else:
                        match_status = f"❌ No employee with matricule {matricule}"
                
                preview["pdfs_found"].append({
                    "pdf_file": pdf_file,
                    "matricule": matricule or "Not found",
                    "employee_name": employee_name,
                    "email": email,
                    "match_status": match_status
                })
            
            return preview
            
        except Exception as e:
            self.update_progress(f"Error generating preview: {e}", "error")
            return None
    
    def extract_matricule_from_pdf_content(self, pdf_path):
        """Extract matricule from PDF content - primary method"""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Look for matricule patterns in the text
                    patterns = [
                        r'MATRICULE[_\s]*:?[_\s]*(\d+)',
                        r'MAT[_\s]*:?[_\s]*(\d+)',
                        r'ID[_\s]*:?[_\s]*(\d+)',
                        r'MATRICULE[_\s]*(\d+)',
                        r'MAT[_\s]*(\d+)',
                        r'ID[_\s]*(\d+)',
                        r'Matricule[_\s]*:?[_\s]*(\d+)',  # Capitalized variants
                        r'Mat[_\s]*:?[_\s]*(\d+)',
                        r'Id[_\s]*:?[_\s]*(\d+)',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            matricule = match.group(1)
                            self.update_progress(f"🔍 Found matricule {matricule} in {os.path.basename(pdf_path)}", "info")
                            return matricule
        except Exception as e:
            self.update_progress(f"Error reading PDF content {pdf_path}: {e}", "error")
        
        return None
    
    def find_employee_by_matricule(self, matricule, employees_df):
        """Find employee in Excel by matricule"""
        try:
            matricule_str = str(matricule).strip()
            self.update_progress(f"🔍 Looking for matricule '{matricule_str}' in employee database", "info")
            
            # Try different column names for matricule
            matricule_columns = ['Matricule', 'matricule', 'MATRICULE', 'Mat', 'mat', 'ID', 'Id']
            
            for col in matricule_columns:
                if col in employees_df.columns:
                    self.update_progress(f"🔍 Checking column '{col}'", "info")
                    # Create a copy to avoid modifying the original
                    df_copy = employees_df.copy()
                    # Convert to string and strip whitespace for comparison
                    df_copy[col] = df_copy[col].astype(str).str.strip()
                    
                    # Simple iteration to avoid pandas Series issues
                    for index, row in df_copy.iterrows():
                        if str(row[col]) == matricule_str:
                            # Convert Series to dictionary to avoid pandas issues
                            employee = dict(row)
                            self.update_progress(f"✅ Matched matricule {matricule} to employee: {employee.get('Name', 'Unknown')}", "success")
                            return employee
            
            self.update_progress(f"❌ No employee found with matricule {matricule}", "warning")
            return None
        except Exception as e:
            self.update_progress(f"Error finding employee for matricule {matricule}: {e}", "error")
            return None
    
    def extract_matricule_from_filename(self, filename):
        """Extract matricule from PDF filename - backup method only"""
        # Remove extension and split by common delimiters
        name_without_ext = os.path.splitext(filename)[0]
        
        # Try different patterns to extract matricule
        patterns = [
            r'(\d+)',  # Any sequence of digits
            r'MAT(\d+)',  # MAT followed by digits
            r'MATRICULE[_\s]?(\d+)',  # MATRICULE followed by digits
            r'ID[_\s]?(\d+)',  # ID followed by digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                return match.group(1)
        
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
        """Send payslip email to employee"""
        try:
            if self.simulation_mode:
                self.update_progress(f"📨 [SIMULATION] Email prepared for {receiver_email}", "info")
                return True
            
            msg = EmailMessage()
            msg["Subject"] = "Your Monthly Payslip"
            msg["From"] = "CRTV HR <no-reply@crtv.cm>"
            msg["To"] = receiver_email
            
            msg.set_content(
                f"Dear {employee_name},\n\n"
                "Please find attached your monthly payslip.\n\n"
                "Regards,\n"
                "CRTV Human Resources"
            )
            
            with open(pdf_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(pdf_path)
                )
            
            # Use the original working configuration
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            self.update_progress(f"📨 Email sent to {receiver_email}", "success")
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to send email to {receiver_email}: {str(e)}"
            self.update_progress(error_msg, "error")
            return False
    
    def process_payslips(self):
        """Main payslip processing function - PDF-driven approach"""
        try:
            # Validate files first
            all_valid, validation = self.validate_files()
            if not all_valid:
                return False, "File validation failed"
            
            # Read employee data
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            
            # Get all PDF files in folder
            pdf_files = [f for f in os.listdir(self.payslip_folder) if f.lower().endswith('.pdf')]
            total_pdf_files = len(pdf_files)
            
            self.update_progress(f"Starting processing: {total_pdf_files} PDF files, {len(employees)} employees in database", "info")
            
            success_count = 0
            error_count = 0
            
            for index, pdf_file in enumerate(pdf_files):
                # Check if processing should continue (for cancellation)
                if hasattr(self, '_cancelled') and self._cancelled:
                    self.update_progress("Processing cancelled by user", "warning")
                    return False, "Processing cancelled"
                
                try:
                    pdf_path = os.path.join(self.payslip_folder, pdf_file)
                    self.update_progress(f"Processing PDF {index + 1}/{total_pdf_files}: {pdf_file}", "info")
                    
                    # Extract matricule from PDF content (primary method)
                    matricule = self.extract_matricule_from_pdf_content(pdf_path)
                    
                    if not matricule:
                        # Backup: try filename
                        matricule = self.extract_matricule_from_filename(pdf_file)
                        if matricule:
                            self.update_progress(f"⚠️ Used filename to get matricule {matricule}", "warning")
                    
                    if not matricule:
                        raise ValueError("No matricule found in PDF")
                    
                    # Find matching employee in Excel
                    employee = self.find_employee_by_matricule(matricule, employees)
                    if not employee:
                        raise ValueError(f"No employee found with matricule {matricule}")
                    
                    # Get employee details
                    employee_name = str(employee.get('Name', 'Unknown')).strip()
                    email = str(employee.get('Email', '')).strip()
                    
                    # Check if email is valid
                    if not email or email.lower() in ['nan', 'none', '']:
                        raise ValueError(f"No valid email for employee {employee_name}")
                    
                    # Process the PDF: add stamp and save to output
                    clean_name = re.sub(r"[^a-zA-Z0-9]", "_", employee_name)
                    output_file = self.process_individual_pdf(pdf_path, clean_name, matricule)
                    
                    self.update_progress(f"✅ Payslip ready for {employee_name} (Mat: {matricule})", "success")
                    
                    # Send email
                    self.update_progress(f"📧 Sending email to {email}...", "info")
                    if self.send_email(email, employee_name, output_file):
                        success_count += 1
                        self.update_progress(f"✅ Email sent successfully to {employee_name}", "success")
                    else:
                        error_count += 1
                        self.update_progress(f"❌ Failed to send email to {employee_name}", "error")
                    
                except Exception as e:
                    error_count += 1
                    self.update_progress(f"❌ Failed for {pdf_file}: {e}", "error")
            
            # Summary
            summary = f"Processing complete: {success_count} successful, {error_count} failed"
            self.update_progress(summary, "success" if error_count == 0 else "warning")
            
            return error_count == 0, summary
            
        except Exception as e:
            error_msg = f"Critical error during processing: {e}"
            self.update_progress(error_msg, "error")
            return False, error_msg
    
    def process_individual_pdf(self, pdf_path, employee_name, matricule):
        """Process individual PDF file: add stamp and save to output"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Add stamp to each page and copy to writer
        for page in reader.pages:
            stamped_page = self.add_stamp_to_page(page)
            writer.add_page(stamped_page)
        
        # Create output filename
        output_file = f"{self.output_dir}/Payslip_{employee_name}_{matricule}.pdf"
        
        # Save the processed PDF
        with open(output_file, "wb") as f:
            writer.write(f)
        
        return output_file
    
    def cancel_processing(self):
        """Cancel the current processing"""
        self._cancelled = True
