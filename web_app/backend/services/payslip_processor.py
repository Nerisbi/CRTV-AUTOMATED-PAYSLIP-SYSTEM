"""
Payslip Processing Service - Migrated from desktop application
Handles PDF processing, Excel validation, and email sending
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import smtplib
from email.message import EmailMessage
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import re
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import existing modules
try:
    from individual_retrieval import retrieve_individual_payslip, validate_employee, find_employee_page
    from multi_pdf_aggregator import retrieve_historical_payslips
    INDIVIDUAL_MODULES_AVAILABLE = True
except ImportError:
    INDIVIDUAL_MODULES_AVAILABLE = False
    print("Warning: Individual retrieval modules not available")

# OCR imports (optional)
try:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class PayslipProcessor:
    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        self.upload_dir = Path("uploads")
        self.output_dir = Path("outputs")
        self.stamp_image = "input/Stamp.png"
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.email_address = "nerisbi801@gmail.com"
        self.email_password = "qmpp eqym rclo bave"
        
        # Ensure directories exist
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def validate_files(self, pdf_path: str, excel_path: str) -> Tuple[bool, str, Dict]:
        """Validate PDF and Excel files"""
        try:
            # Check if files exist
            pdf_file = self.upload_dir / pdf_path
            excel_file = self.upload_dir / excel_path
            
            if not pdf_file.exists():
                return False, "PDF file not found", {}
            
            if not excel_file.exists():
                return False, "Excel file not found", {}
            
            # Validate PDF
            try:
                with open(pdf_file, 'rb') as f:
                    pdf_reader = PdfReader(f)
                    if len(pdf_reader.pages) == 0:
                        return False, "PDF file is empty", {}
            except Exception as e:
                return False, f"Invalid PDF file: {str(e)}", {}
            
            # Validate Excel
            try:
                df = pd.read_excel(excel_file)
                required_columns = ['matricule', 'name', 'email']
                missing_columns = [col for col in required_columns if col not in df.columns.str.lower()]
                
                if missing_columns:
                    return False, f"Excel missing required columns: {', '.join(missing_columns)}", {}
                
                employee_count = len(df)
                
            except Exception as e:
                return False, f"Invalid Excel file: {str(e)}", {}
            
            return True, f"Files validated successfully. Found {employee_count} employees", {
                "employee_count": employee_count,
                "pdf_pages": len(pdf_reader.pages)
            }
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", {}
    
    def process_bulk_payslips(self, pdf_path: str, excel_path: str) -> Tuple[bool, str, Dict]:
        """Process bulk payslip distribution"""
        try:
            pdf_file = self.upload_dir / pdf_path
            excel_file = self.upload_dir / excel_path
            
            # Read employee data
            df = pd.read_excel(excel_file)
            
            # Read PDF
            with open(pdf_file, 'rb') as f:
                pdf_reader = PdfReader(f)
            
            results = {
                "total": len(df),
                "processed": 0,
                "sent": 0,
                "failed": 0,
                "errors": []
            }
            
            # Process each employee
            for index, employee in df.iterrows():
                try:
                    # Get employee details (handle different column names)
                    matricule = str(employee.get('matricule', employee.get('Matricule', '')))
                    name = str(employee.get('name', employee.get('Name', employee.get('Employee Name', ''))))
                    email = str(employee.get('email', employee.get('Email', '')))
                    email2 = str(employee.get('email2', employee.get('Email2', '')))
                    
                    if not matricule or not email:
                        results["errors"].append(f"Row {index + 1}: Missing matricule or email")
                        results["failed"] += 1
                        continue
                    
                    # Find employee page in PDF
                    page_number, page_message = self._find_employee_page(matricule, pdf_reader)
                    
                    if page_number is None:
                        results["errors"].append(f"{name}: {page_message}")
                        results["failed"] += 1
                        continue
                    
                    # Create individual payslip PDF
                    output_file = self._create_individual_payslip(
                        pdf_reader, page_number, name, matricule
                    )
                    
                    # Send email
                    if self._send_email(email, name, output_file, email2):
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["processed"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Row {index + 1}: {str(e)}")
                    results["failed"] += 1
            
            success = results["failed"] == 0
            message = f"Processed {results['processed']}/{results['total']} employees. Sent: {results['sent']}, Failed: {results['failed']}"
            
            return success, message, results
            
        except Exception as e:
            return False, f"Processing error: {str(e)}", {}
    
    def process_individual_retrieval(self, matricule: str, email: str, pdf_files: List[str]) -> Tuple[bool, str, Optional[str]]:
        """Process individual payslip retrieval"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            return False, "Individual retrieval modules not available", None
        
        try:
            # Convert filenames to full paths
            pdf_paths = [str(self.upload_dir / pdf_file) for pdf_file in pdf_files]
            excel_path = str(self.upload_dir / "employees.xlsx")  # Default excel file
            
            # Use existing individual retrieval function
            success, message, output_file = retrieve_individual_payslip(
                matricule, email, pdf_paths, excel_path, self.simulation_mode
            )
            
            return success, message, output_file
            
        except Exception as e:
            return False, f"Individual retrieval error: {str(e)}", None
    
    def _find_employee_page(self, matricule: str, pdf_reader: PdfReader) -> Tuple[Optional[int], str]:
        """Find employee page in PDF"""
        try:
            for page_idx in range(len(pdf_reader.pages)):
                # Extract text from page
                page = pdf_reader.pages[page_idx]
                text = page.extract_text()
                
                if text:
                    # Clean and normalize text
                    cleaned_text = text.replace(' ', '').replace('\n', '').upper()
                    cleaned_matricule = matricule.replace(' ', '').upper()
                    
                    # Check for exact match
                    if cleaned_matricule in cleaned_text:
                        return page_idx, f"Found matricule {matricule} on page {page_idx + 1}"
            
            return None, f"Matricule {matricule} not found in PDF"
            
        except Exception as e:
            return None, f"Error searching PDF: {str(e)}"
    
    def _create_individual_payslip(self, pdf_reader: PdfReader, page_number: int, name: str, matricule: str) -> str:
        """Create individual payslip PDF"""
        writer = PdfWriter()
        
        # Get the employee's page
        page = pdf_reader.pages[page_number]
        
        # Add stamp if available
        if os.path.exists(self.stamp_image):
            page = self._add_stamp_to_page(page, self.stamp_image)
        
        writer.add_page(page)
        
        # Create output file
        safe_name = name.replace(' ', '_').replace('/', '_')
        output_filename = f"Individual_Payslip_{safe_name}_{matricule}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = self.output_dir / output_filename
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return str(output_path)
    
    def _add_stamp_to_page(self, page, stamp_path: str):
        """Add stamp to PDF page"""
        try:
            packet = io.BytesIO()
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Stamp position and size
            x = page_width - 160
            y = 60
            width = 120
            height = 120
            
            c.drawImage(stamp_path, x, y, width, height, mask="auto")
            c.save()
            
            packet.seek(0)
            stamp_pdf = PdfReader(packet)
            page.merge_page(stamp_pdf.pages[0])
            
            return page
            
        except Exception as e:
            print(f"Warning: Could not add stamp: {e}")
            return page
    
    def _send_email(self, email: str, name: str, pdf_path: str, email2: str = "") -> bool:
        """Send payslip email"""
        try:
            if self.simulation_mode:
                print(f"[SIMULATION] Email prepared for {email} with {os.path.basename(pdf_path)}")
                return True
            
            msg = EmailMessage()
            msg["Subject"] = "Your Monthly Payslip"
            msg["From"] = "CRTV HR <no-reply@crtv.cm>"
            msg["To"] = email
            
            msg.set_content(
                f"Dear {name},\n\n"
                "Please find attached your monthly payslip.\n\n"
                "Regards,\n"
                "CRTV Human Resources"
            )
            
            # Attach PDF
            with open(pdf_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(pdf_path)
                )
            
            # Send email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            # Send to second email if provided
            if email2 and email2.strip():
                msg["To"] = email2.strip()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.login(self.email_address, self.email_password)
                    server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
            return False

# Global processor instance
processor = None

def get_processor(simulation_mode: bool = False) -> PayslipProcessor:
    """Get or create processor instance"""
    global processor
    if processor is None or processor.simulation_mode != simulation_mode:
        processor = PayslipProcessor(simulation_mode)
    return processor
