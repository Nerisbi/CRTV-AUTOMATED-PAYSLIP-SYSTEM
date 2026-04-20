import os
import io
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from logger import log_info, log_error
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from datetime import datetime
import re

# ================== CONFIGURATION ==================
SIMULATION_MODE = True   # SET TRUE IF TESTING ONLY
STAMP_IMAGE = "input/Stamp.png"
OUTPUT_DIR = "output/historical_payslips"

# Email configuration (same as main.py)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "nerisbi801@gmail.com"
EMAIL_PASSWORD = "qmpp eqym rclo bave"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== PDF PROCESSING FUNCTIONS ==================
def add_stamp_to_page(original_page, stamp_path):
    """Add stamp to PDF page (same as main.py)"""
    packet = io.BytesIO()
    page_width = float(original_page.mediabox.width)
    page_height = float(original_page.mediabox.height)
    c = canvas.Canvas(packet, pagesize=(page_width,page_height))

    # Stamp position & size
    x = page_width -160
    y = 60
    width = 120
    height = 120

    c.drawImage(stamp_path, x, y, width, height, mask="auto")
    c.save()

    packet.seek(0)
    stamp_pdf = PdfReader(packet)
    original_page.merge_page(stamp_pdf.pages[0])
    return original_page

def extract_text_from_pdf_page(page, page_num, pdf_path):
    """Extract text from PDF page using multiple methods including OCR"""
    
    # Method 1: Try direct text extraction first
    text = page.extract_text()
    if text and text.strip():
        return text
    
    # Method 2: Use PyMuPDF for better text extraction
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        text = page.get_text()
        if text and text.strip():
            doc.close()
            return text
        doc.close()
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")
    
    # Method 3: OCR for scanned PDFs
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # Convert page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Use Tesseract OCR
        text = pytesseract.image_to_string(img)
        doc.close()
        
        if text and text.strip():
            return text
            
    except Exception as e:
        print(f"OCR extraction failed: {e}")
    
    return ""

def find_employee_page_in_pdf(employee_matricule, pdf_path):
    """Find the exact PDF page containing employee's matricule in a specific PDF"""
    
    if not employee_matricule:
        return None, "No matricule provided"
    
    if not os.path.exists(pdf_path):
        return None, f"PDF file not found: {pdf_path}"
    
    print(f"Searching for matricule '{employee_matricule}' in {os.path.basename(pdf_path)}")
    
    try:
        reader = PdfReader(pdf_path)
        
        for page_idx in range(len(reader.pages)):
            # Extract text using OCR-capable function
            page_text = extract_text_from_pdf_page(reader.pages[page_idx], page_idx, pdf_path)
            
            # Clean and normalize text for matching
            cleaned_text = page_text.replace(' ', '').replace('\n', '').upper()
            cleaned_matricule = employee_matricule.replace(' ', '').upper()
            
            # Check for exact matricule match
            if cleaned_matricule in cleaned_text:
                print(f"Found exact match for matricule '{employee_matricule}' on page {page_idx + 1}")
                return page_idx, f"Matricule match found on page {page_idx + 1}"
        
        # No match found
        return None, f"No matching matricule '{employee_matricule}' found in {os.path.basename(pdf_path)}"
        
    except Exception as e:
        return None, f"Error processing {os.path.basename(pdf_path)}: {str(e)}"

# ================== MULTI-PDF AGGREGATION ==================
def search_multiple_pdfs(employee_matricule, pdf_paths):
    """
    Search for employee matricule across multiple PDF files
    Returns: list of (pdf_path, page_number, message) for each match
    """
    matches = []
    
    for pdf_path in pdf_paths:
        page_number, message = find_employee_page_in_pdf(employee_matricule, pdf_path)
        if page_number is not None:
            matches.append((pdf_path, page_number, message))
            print(f"MATCH: {os.path.basename(pdf_path)} - Page {page_number + 1}")
        else:
            print(f"NO MATCH: {os.path.basename(pdf_path)} - {message}")
    
    return matches

def create_cover_page(employee_name, employee_matricule, pdf_files, output_path):
    """Create a cover page for the consolidated payslip"""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "Consolidated Payslip Report")
    
    # Employee info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 700, f"Employee: {employee_name}")
    c.drawString(50, 675, f"Matricule: {employee_matricule}")
    
    # Date
    c.setFont("Helvetica", 12)
    c.drawString(50, 640, f"Generated on: {datetime.now().strftime('%d %B %Y')}")
    
    # Payslip files included
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, "Included Payslips:")
    
    c.setFont("Helvetica", 10)
    y_position = 575
    for i, pdf_file in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_file)
        # Try to extract date from filename
        date_match = re.search(r'(\d{4}|\d{1,2})', filename)
        if date_match:
            date_str = date_match.group(1)
            c.drawString(70, y_position, f"{i}. {filename} (Period: {date_str})")
        else:
            c.drawString(70, y_position, f"{i}. {filename}")
        y_position -= 20
    
    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(50, 50, "Generated by CRTV Automated Payslip Distribution System")
    c.drawString(50, 35, "This document contains confidential employee information")
    
    c.save()
    packet.seek(0)
    
    # Add the cover page to the output
    cover_reader = PdfReader(packet)
    return cover_reader.pages[0]

def merge_employee_payslips(employee_matricule, employee_name, pdf_paths, output_filename=None):
    """
    Merge all payslips for an employee from multiple PDF files
    Returns: (success, message, output_file_path)
    """
    try:
        print(f"Starting multi-PDF aggregation for {employee_name} ({employee_matricule})")
        
        # Search for matches across all PDFs
        matches = search_multiple_pdfs(employee_matricule, pdf_paths)
        
        if not matches:
            return False, f"No payslips found for matricule {employee_matricule} in any of the provided files", None
        
        # Create output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = re.sub(r'[^\w\s-]', '', employee_name).strip().replace(' ', '_')
            output_filename = f"Consolidated_Payslips_{safe_name}_{employee_matricule}_{timestamp}.pdf"
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Create PDF writer
        writer = PdfWriter()
        
        # Add cover page
        cover_page = create_cover_page(employee_name, employee_matricule, [match[0] for match in matches], output_path)
        writer.add_page(cover_page)
        
        # Add matching payslip pages
        for pdf_path, page_number, message in matches:
            try:
                reader = PdfReader(pdf_path)
                page = reader.pages[page_number]
                
                # Add stamp
                if os.path.exists(STAMP_IMAGE):
                    page = add_stamp_to_page(page, STAMP_IMAGE)
                
                writer.add_page(page)
                print(f"Added page from {os.path.basename(pdf_path)}")
                
            except Exception as e:
                print(f"Error adding page from {pdf_path}: {e}")
                continue
        
        # Write the merged PDF
        with open(output_path, "wb") as f:
            writer.write(f)
        
        success_msg = f"Successfully created consolidated payslip with {len(matches)} payslips"
        print(success_msg)
        log_info(f"Multi-PDF aggregation successful for {employee_name}: {len(matches)} payslips merged")
        
        return True, success_msg, output_path
        
    except Exception as e:
        error_msg = f"Error during multi-PDF aggregation: {str(e)}"
        print(error_msg)
        log_error(error_msg)
        return False, error_msg, None

# ================== EMAIL FUNCTIONS ==================
def send_consolidated_email(receiver_email, employee_name, pdf_path, payslip_count):
    """Send consolidated payslip email"""
    if SIMULATION_MODE:
        print(f"[SIMULATION] Consolidated email prepared for {receiver_email} with {payslip_count} payslips")
        return True, "Email prepared successfully (simulation mode)"
    
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Your Consolidated Payslips - {payslip_count} Periods"
        msg["From"] = "CRTV HR <no-reply@crtv.cm>"
        msg["To"] = receiver_email

        msg.set_content(
            f"Dear {employee_name},\n\n"
            f"Please find attached your consolidated payslip report containing {payslip_count} payslip periods.\n\n"
            "This document includes a cover page with details of all included payslips.\n\n"
            "This is a historical payslip request processed by CRTV HR system.\n\n"
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

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        log_info(f"Consolidated payslips sent to {receiver_email}")
        return True, "Email sent successfully"
        
    except Exception as e:
        log_error(f"Failed to send consolidated email: {e}")
        return False, f"Failed to send email: {str(e)}"

# ================== MAIN MULTI-PDF RETRIEVAL FUNCTION ==================
def retrieve_historical_payslips(matricule, email, pdf_paths, excel_path):
    """
    Main function to retrieve and send historical payslips from multiple PDFs
    Returns: (success, message, output_file_path)
    """
    
    # Import validation function from individual_retrieval
    from individual_retrieval import validate_employee
    
    # Step 1: Validate employee
    is_valid, employee_data, validation_message = validate_employee(matricule, email, excel_path)
    if not is_valid:
        return False, validation_message, None
    
    # Step 2: Merge payslips from multiple PDFs
    success, merge_message, output_file = merge_employee_payslips(
        employee_data['matricule'], 
        employee_data['name'], 
        pdf_paths
    )
    
    if not success:
        return False, merge_message, None
    
    # Step 3: Send consolidated email
    payslip_count = len(search_multiple_pdfs(employee_data['matricule'], pdf_paths))
    email_success, email_message = send_consolidated_email(
        email, 
        employee_data['name'], 
        output_file, 
        payslip_count
    )
    
    if email_success:
        final_message = f"Success: {validation_message}. {merge_message}. {email_message}"
        log_info(f"Historical payslip retrieval successful for {employee_data['name']}")
        return True, final_message, output_file
    else:
        return False, f"Payslips merged but email failed: {email_message}", output_file

# ================== UTILITY FUNCTIONS ==================
def get_pdf_info(pdf_paths):
    """Get information about PDF files"""
    pdf_info = []
    
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            try:
                reader = PdfReader(pdf_path)
                file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
                pdf_info.append({
                    'path': pdf_path,
                    'name': os.path.basename(pdf_path),
                    'pages': len(reader.pages),
                    'size_mb': round(file_size, 2)
                })
            except Exception as e:
                pdf_info.append({
                    'path': pdf_path,
                    'name': os.path.basename(pdf_path),
                    'pages': 0,
                    'size_mb': 0,
                    'error': str(e)
                })
        else:
            pdf_info.append({
                'path': pdf_path,
                'name': os.path.basename(pdf_path),
                'pages': 0,
                'size_mb': 0,
                'error': 'File not found'
            })
    
    return pdf_info

def validate_pdf_files(pdf_paths):
    """Validate that all PDF files exist and are readable"""
    valid_files = []
    invalid_files = []
    
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            try:
                reader = PdfReader(pdf_path)
                if len(reader.pages) > 0:
                    valid_files.append(pdf_path)
                else:
                    invalid_files.append(f"{os.path.basename(pdf_path)}: Empty PDF")
            except Exception as e:
                invalid_files.append(f"{os.path.basename(pdf_path)}: {str(e)}")
        else:
            invalid_files.append(f"{os.path.basename(pdf_path)}: File not found")
    
    return valid_files, invalid_files
