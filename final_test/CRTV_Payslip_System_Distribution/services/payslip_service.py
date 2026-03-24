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

# Try to import OCR, but don't fail if not available
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    
    # Set Tesseract path for Windows (adjust if installed elsewhere)
    import os
    if os.name == 'nt':  # Windows
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print("Warning: Tesseract not found at default location. Please install or update path.")
        
        # Set Poppler path for Windows (adjust if installed elsewhere)
        poppler_path = r'C:\poppler-23.11.0\Library\bin'
        if os.path.exists(poppler_path):
            os.environ['PATH'] = poppler_path + ';' + os.environ.get('PATH', '')
        else:
            print("Warning: Poppler not found. OCR may not work without it.")
    
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not available. Install with: pip install pytesseract pdf2image Pillow")


class PayslipService:
    def __init__(self):
        self.simulation_mode = False  # Always send real emails
        self.input_pdf = "input/payslip.pdf"  # Back to single PDF
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
        """Validate all required files"""
        try:
            validation_results = {
                "input_pdf": os.path.exists(self.input_pdf),
                "input_excel": os.path.exists(self.input_excel),
                "stamp_image": os.path.exists(self.stamp_image),
                "output_dir": os.path.exists(self.output_dir)
            }
            
            # Create output directory if it doesn't exist
            if not validation_results["output_dir"]:
                os.makedirs(self.output_dir, exist_ok=True)
                validation_results["output_dir"] = True
                self.update_progress(f"Created output directory: {self.output_dir}", "info")
            
            all_valid = all(validation_results.values())
            
            if all_valid:
                self.update_progress("✅ All files validated successfully", "success")
            else:
                missing = [k for k, v in validation_results.items() if not v]
                self.update_progress(f"❌ Missing files: {', '.join(missing)}", "error")
            
            return all_valid, validation_results
            
        except Exception as e:
            self.update_progress(f"Error validating files: {e}", "error")
            return False, {}
    
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
        """Get total number of pages in the PDF file"""
        try:
            if not os.path.exists(self.input_pdf):
                return 0
            
            reader = PdfReader(self.input_pdf)
            return len(reader.pages)
        except Exception as e:
            self.update_progress(f"Error reading PDF file: {e}", "error")
            return 0
    
    def preview_process(self):
        """Generate preview of what will be processed - single PDF approach"""
        try:
            if not os.path.exists(self.input_excel) or not os.path.exists(self.input_pdf):
                return None
            
            employees = pd.read_excel(self.input_excel, engine="openpyxl")
            reader = PdfReader(self.input_pdf)
            
            preview = {
                "mode": "PRODUCTION",  # Always production now
                "total_employees": len(employees),
                "pdf_pages": len(reader.pages),
                "input_pdf": self.input_pdf,
                "output_dir": self.output_dir,
                "employees": []
            }
            
            self.update_progress("Analyzing PDF pages and matching with employees...", "info")
            
            for _, row in employees.iterrows():
                employee_name = str(row.get('Name', 'Unknown')).strip()
                matricule = str(row.get('Matricule', row.get('matricule', ''))).strip()
                email = str(row.get('Email', 'Unknown')).strip()
                
                # Find the page for this employee
                page_number = self.find_page_by_matricule(reader, matricule)
                page_found = page_number is not None
                
                preview["employees"].append({
                    "name": employee_name,
                    "email": email,
                    "matricule": matricule,
                    "page_found": page_found,
                    "page_number": page_number + 1 if page_found else "Not found"
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
        """Main payslip processing function - single PDF with multiple employees"""
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
            processed_pages = set()
            
            for index, row in employees.iterrows():
                # Check if processing should continue (for cancellation)
                if hasattr(self, '_cancelled') and self._cancelled:
                    self.update_progress("Processing cancelled by user", "warning")
                    return False, "Processing cancelled"
                
                try:
                    employee_name = str(row.get('Name', 'Unknown')).strip()
                    matricule = str(row.get('Matricule', row.get('matricule', ''))).strip()
                    email = str(row.get('Email', 'Unknown')).strip()
                    
                    self.update_progress(f"Processing {index + 1}/{total_employees}: {employee_name} (Mat: {matricule})", "info")
                    
                    if not matricule:
                        raise ValueError("No matricule found for employee")
                    
                    # Find the page for this employee by searching matricule in each page
                    page_number = self.find_page_by_matricule(reader, matricule)
                    if page_number is None:
                        raise ValueError(f"No page found for matricule {matricule}")
                    
                    if page_number in processed_pages:
                        raise ValueError(f"Page {page_number + 1} already used for another employee")
                    
                    processed_pages.add(page_number)
                    
                    # Clean name for filename
                    clean_name = re.sub(r"[^a-zA-Z0-9]", "_", employee_name)
                    
                    # Process the individual page: add stamp and save to output
                    output_file = self.process_individual_page(reader.pages[page_number], clean_name, matricule)
                    
                    self.update_progress(f"✅ Payslip generated for {employee_name} (Page {page_number + 1})", "success")
                    
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
                    self.update_progress(f"❌ Failed for {row.get('Name', 'Unknown')}: {e}", "error")
            
            # Summary
            summary = f"Processing complete: {success_count} successful, {error_count} failed"
            self.update_progress(summary, "success" if error_count == 0 else "warning")
            
            return error_count == 0, summary
            
        except Exception as e:
            error_msg = f"Critical error during processing: {e}"
            self.update_progress(error_msg, "error")
            return False, error_msg
    
    def extract_text_with_ocr(self, page, page_num):
        """Extract text from PDF page using OCR if regular extraction fails"""
        try:
            if not OCR_AVAILABLE:
                return None
            
            # Convert PDF page to image
            images = pdf2image.convert_from_path(
                self.input_pdf, 
                first_page=page_num + 1, 
                last_page=page_num + 1,
                dpi=200
            )
            
            if images:
                # Use OCR to extract text
                text = pytesseract.image_to_string(images[0])
                return text
            
        except Exception as e:
            self.update_progress(f"OCR extraction failed for page {page_num + 1}: {e}", "warning")
        
        return None
    
    def find_page_by_matricule(self, reader, matricule):
        """Find the page containing the specified matricule"""
        try:
            for page_num, page in enumerate(reader.pages):
                # Try regular text extraction first
                text = page.extract_text()
                
                # If no text found, try OCR
                if not text or not text.strip():
                    self.update_progress(f"🔍 No text on page {page_num + 1}, trying OCR...", "info")
                    text = self.extract_text_with_ocr(page, page_num)
                
                if text and matricule in text:
                    self.update_progress(f"🔍 Found matricule {matricule} on page {page_num + 1}", "info")
                    return page_num
            
            # Fallback: if OCR fails and no text found, match by order
            self.update_progress(f"⚠️ No text found for matricule {matricule}, using order-based matching", "warning")
            return None  # Let the main logic handle order-based fallback
            
        except Exception as e:
            self.update_progress(f"Error searching for matricule {matricule}: {e}", "error")
            return None
    
    def process_individual_page(self, page, employee_name, matricule):
        """Process individual PDF page: add stamp and save to output"""
        writer = PdfWriter()
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
