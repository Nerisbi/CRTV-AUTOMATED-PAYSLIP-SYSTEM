import os
import io
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from logger import log_info, log_error
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re

# ================== CONFIGURATION ==================
SIMULATION_MODE = False   # SET TRUE IF TESTING ONLY
STAMP_IMAGE = "input/Stamp.png"
OUTPUT_DIR = "output/individual_payslips"

# Email configuration (same as main.py)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "nerisbi801@gmail.com"
EMAIL_PASSWORD = "qmpp eqym rclo bave"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== EMPLOYEE VALIDATION ==================
def validate_employee(matricule, email, excel_path):
    """
    Validate employee matricule and email against Excel file
    Returns: (is_valid, employee_data, message)
    """
    try:
        if not os.path.exists(excel_path):
            return False, None, f"Employee Excel file not found: {excel_path}"
        
        employees = pd.read_excel(excel_path, engine="openpyxl")
        
        # Clean input matricule
        clean_matricule = str(matricule).strip().upper()
        
        # Search for employee by matricule
        employee_row = None
        for idx, row in employees.iterrows():
            excel_matricule = str(row.get('Matricule', '')).strip().upper()
            if excel_matricule == clean_matricule:
                employee_row = row
                break
        
        if employee_row is None:
            return False, None, f"No employee found with matricule: {matricule}"
        
        # Get employee data
        employee_data = {
            'name': str(employee_row["Name"]).strip(),
            'matricule': clean_matricule,
            'email1': str(employee_row.get('Email', '')).strip(),
            'email2': str(employee_row.get('Email 2', '')).strip(),
            'row_index': employee_row.name
        }
        
        # Validate email
        clean_email = str(email).strip().lower()
        if not clean_email:
            return False, employee_data, "Email address is required"
        
        # Check if provided email matches any employee email
        employee_emails = [emp_email.lower() for emp_email in [employee_data['email1'], employee_data['email2']] if emp_email]
        
        if clean_email not in employee_emails:
            return False, employee_data, f"Email {email} does not match records for {employee_data['name']}"
        
        log_info(f"Employee validated: {employee_data['name']} ({employee_data['matricule']})")
        return True, employee_data, "Employee validated successfully"
        
    except Exception as e:
        log_error(f"Error validating employee: {e}")
        return False, None, f"Error validating employee: {str(e)}"

# ================== EMAIL FUNCTIONS ==================
def send_individual_email(receiver_email, employee_name, pdf_path, simulation_mode=False):
    """Send individual payslip email"""
    if simulation_mode:
        print(f"[SIMULATION] Individual email prepared for {receiver_email} with {os.path.basename(pdf_path)}")
        return True, "Email prepared successfully (simulation mode)"
    
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Payslip - Individual Request"
        msg["From"] = "CRTV HR <no-reply@crtv.cm>"
        msg["To"] = receiver_email

        msg.set_content(
            f"Dear {employee_name},\n\n"
            "Please find attached your requested payslip.\n\n"
            "This is an individual retrieval request processed by CRTV HR system.\n\n"
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
        
        log_info(f"Individual payslip sent to {receiver_email}")
        return True, "Email sent successfully"
        
    except Exception as e:
        log_error(f"Failed to send individual email: {e}")
        return False, f"Failed to send email: {str(e)}"

# ================== PDF PROCESSING ==================
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

def find_employee_page(employee_matricule, pdf_path):
    """Find the exact PDF page containing employee's matricule"""
    
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
        return None, f"No matching matricule '{employee_matricule}' found in payslip"
        
    except Exception as e:
        return None, f"Error processing PDF: {str(e)}"

# ================== MAIN INDIVIDUAL RETRIEVAL FUNCTION ==================
def retrieve_individual_payslip(matricule, email, pdf_paths, excel_path, simulation_mode=False):
    """
    Main function to retrieve and send individual payslip from multiple PDF files
    Returns: (success, message, output_file_path)
    """
    
    # Step 1: Validate employee
    is_valid, employee_data, validation_message = validate_employee(matricule, email, excel_path)
    if not is_valid:
        return False, validation_message, None
    
    # Handle both single file path and list of paths
    if isinstance(pdf_paths, str):
        pdf_paths = [pdf_paths]
    
    # Step 2: Find employee's payslip pages in all PDF files
    found_pages = []
    page_messages = []
    
    for pdf_path in pdf_paths:
        page_number, page_message = find_employee_page(employee_data['matricule'], pdf_path)
        if page_number is not None:
            found_pages.append((pdf_path, page_number))
            page_messages.append(page_message)
            print(f"Found employee {employee_data['matricule']} on page {page_number} in {os.path.basename(pdf_path)}")
    
    if not found_pages:
        return False, f"No matching matricule '{employee_data['matricule']}' found in any of the selected PDF files", None
    
    # Step 3: Create individual payslip PDF with all found pages
    try:
        writer = PdfWriter()
        
        # Add all found pages with stamps
        for pdf_path, page_number in found_pages:
            reader = PdfReader(pdf_path)
            page = reader.pages[page_number]
            page = add_stamp_to_page(page, STAMP_IMAGE)
            writer.add_page(page)
        
        # Create output file
        output_file = f"{OUTPUT_DIR}/Individual_Payslip_{employee_data['name'].replace(' ', '_')}_{employee_data['matricule']}.pdf"
        with open(output_file, "wb") as f:
            writer.write(f)
        
        print(f"Individual payslip created with {len(found_pages)} pages: {output_file}")
        
        # Step 4: Send email
        email_success, email_message = send_individual_email(email, employee_data['name'], output_file, simulation_mode)
        
        if email_success:
            log_info(f"Individual payslip retrieval successful for {employee_data['name']} from {len(found_pages)} files")
            combined_message = f"Success: {validation_message}. Found in {len(found_pages)} files. {'; '.join(page_messages)}. {email_message}"
            return True, combined_message, output_file
        else:
            return False, f"Payslip created but email failed: {email_message}", output_file
            
    except Exception as e:
        log_error(f"Error creating individual payslip: {e}")
        return False, f"Error creating payslip: {str(e)}", None

# ================== EMPLOYEE DATA EDITING ==================
def update_employee_email(matricule, new_email, excel_path):
    """
    Update employee email in Excel file
    Returns: (success, message)
    """
    try:
        if not os.path.exists(excel_path):
            return False, f"Excel file not found: {excel_path}"
        
        # Read Excel file
        employees = pd.read_excel(excel_path, engine="openpyxl")
        
        # Find employee by matricule
        clean_matricule = str(matricule).strip().upper()
        employee_found = False
        
        for idx, row in employees.iterrows():
            excel_matricule = str(row.get('Matricule', '')).strip().upper()
            if excel_matricule == clean_matricule:
                # Update primary email
                employees.at[idx, 'Email'] = new_email
                employee_found = True
                break
        
        if not employee_found:
            return False, f"Employee with matricule {matricule} not found"
        
        # Save updated Excel file
        employees.to_excel(excel_path, index=False, engine='openpyxl')
        
        log_info(f"Email updated for employee {matricule}: {new_email}")
        return True, f"Email updated successfully for {matricule}"
        
    except Exception as e:
        log_error(f"Error updating employee email: {e}")
        return False, f"Error updating email: {str(e)}"

def get_employee_by_matricule(matricule, excel_path):
    """
    Get employee information by matricule
    Returns: (found, employee_data)
    """
    try:
        if not os.path.exists(excel_path):
            return False, None
        
        employees = pd.read_excel(excel_path, engine="openpyxl")
        clean_matricule = str(matricule).strip().upper()
        
        for idx, row in employees.iterrows():
            excel_matricule = str(row.get('Matricule', '')).strip().upper()
            if excel_matricule == clean_matricule:
                employee_data = {
                    'name': str(row["Name"]).strip(),
                    'matricule': clean_matricule,
                    'email1': str(row.get('Email', '')).strip(),
                    'email2': str(row.get('Email 2', '')).strip(),
                    'row_index': idx
                }
                return True, employee_data
        
        return False, None
        
    except Exception as e:
        log_error(f"Error getting employee data: {e}")
        return False, None
