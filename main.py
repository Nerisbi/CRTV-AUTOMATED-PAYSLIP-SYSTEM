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

# ================== MODE ==================
# True  = simulation (NO real emails sent)
# False = production (real emails sent)
SIMULATION_MODE = False   # SET TRUE IF TESTING ONLY

# ================== PATH CONFIG ==================
INPUT_PDF = ""  # Will be set from UI
INPUT_EXCEL = ""  # Will be set from UI
STAMP_IMAGE = "input/Stamp.png"
OUTPUT_DIR = "output/sent_payslips"

# Global variables to store file paths
current_pdf_path = ""
current_excel_path = ""

def set_file_paths(pdf_path, excel_path):
    """Set file paths from UI"""
    global current_pdf_path, current_excel_path
    current_pdf_path = pdf_path
    current_excel_path = excel_path

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== GMAIL SMTP CONFIG ==================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "nerisbi801@gmail.com"      # Sender Gmail
EMAIL_PASSWORD = "qmpp eqym rclo bave"       # Gmail App Password

# ================== EMAIL FUNCTION ==================
def send_email(receiver_email, employee_name, pdf_path):
    if SIMULATION_MODE:
        print(f"[SIMULATION] Email prepared for {receiver_email} with {os.path.basename(pdf_path)}")
        return

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

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def send_multiple_emails(email1, email2, employee_name, pdf_path):
    """Send payslip to multiple email addresses for the same employee"""
    emails_sent = []
    
    # Send to first email
    if email1 and email1.strip():
        email1 = email1.strip()
        try:
            send_email(email1, employee_name, pdf_path)
            emails_sent.append(email1)
            if not SIMULATION_MODE:
                print(f"EMAIL SENT: Payslip sent to {email1}")
        except Exception as e:
            print(f"ERROR: Failed to send to {email1}: {e}")
    
    # Send to second email
    if email2 and email2.strip():
        email2 = email2.strip()
        try:
            send_email(email2, employee_name, pdf_path)
            emails_sent.append(email2)
            if not SIMULATION_MODE:
                print(f"EMAIL SENT: Payslip sent to {email2}")
        except Exception as e:
            print(f"ERROR: Failed to send to {email2}: {e}")
    
    return emails_sent

# ================== STAMP FUNCTION ==================
def add_stamp_to_page(original_page, stamp_path):
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

# ================== OCR FUNCTION FOR SCANNED PDFS ==================
def extract_text_from_pdf_page(page, page_num):
    """Extract text from PDF page using multiple methods including OCR"""
    
    # Method 1: Try direct text extraction first
    text = page.extract_text()
    if text and text.strip():
        return text
    
    # Method 2: Use PyMuPDF for better text extraction
    try:
        doc = fitz.open(current_pdf_path)
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
        doc = fitz.open(current_pdf_path)
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

# ================== STRICT MATRICULE MATCHING ==================
def find_employee_page(employee_matricule, reader):
    """Find the exact PDF page containing employee's matricule"""
    
    if not employee_matricule:
        return None, "No matricule provided for employee"
    
    print(f"Searching for matricule: '{employee_matricule}'")
    
    for page_idx in range(len(reader.pages)):
        # Extract text using OCR-capable function
        page_text = extract_text_from_pdf_page(reader.pages[page_idx], page_idx)
        
        # Clean and normalize text for matching
        cleaned_text = page_text.replace(' ', '').replace('\n', '').upper()
        cleaned_matricule = employee_matricule.replace(' ', '').upper()
        
        # Check for exact matricule match
        if cleaned_matricule in cleaned_text:
            print(f"SECURITY: Found exact match for matricule '{employee_matricule}' on page {page_idx + 1}")
            return page_idx, f"Exact matricule match found on page {page_idx + 1}"
    
    # No match found - SECURITY VIOLATION
    return None, f"SECURITY ALERT: No matching matricule '{employee_matricule}' found in any payslip"

# ================== MAIN LOGIC ==================
def main():
    global current_pdf_path, current_excel_path
    
    if not current_pdf_path:
        print("ERROR: No PDF file selected. Please select a PDF file from the UI.")
        return

    if not current_excel_path:
        print("ERROR: No Excel file selected. Please select an Excel file from the UI.")
        return

    if not os.path.exists(current_pdf_path):
        print(f"ERROR: Payslip PDF not found at {current_pdf_path}")
        return

    if not os.path.exists(current_excel_path):
        print(f"ERROR: Employees Excel file not found at {current_excel_path}")
        return

    if not os.path.exists(STAMP_IMAGE):
        print("ERROR: Stamp image not found.")
        return

    employees = pd.read_excel(current_excel_path, engine="openpyxl")
    reader = PdfReader(current_pdf_path)

    print(f"Total pages in PDF: {len(reader.pages)}")
    print(f"Total employees: {len(employees)}")
    print("SECURITY MODE: Strict matricule matching - NO FALLBACKS")
    print("=" * 60)

    # Security validation
    if len(employees) != len(reader.pages):
        print(f"SECURITY WARNING: Employee count ({len(employees)}) != PDF page count ({len(reader.pages)})")
        print("Each employee must have exactly one matching payslip page.")
    
    successful_matches = 0
    failed_matches = 0

    for index, row in employees.iterrows():
        try:
            # Get employee data
            employee_matricule = str(row.get('Matricule', '')).strip()
            name = str(row["Name"]).strip()
            email1 = str(row.get('Email', '')).strip()
            email2 = str(row.get('Email 2', '')).strip()  # Handle space in column name
            
            print(f"\nProcessing: {name} (matricule: '{employee_matricule}')")
            print(f"Emails: '{email1}' | '{email2}'")
            
            # Validate at least one email exists
            if not email1 and not email2:
                print("SECURITY FAILURE: No email addresses provided for employee")
                failed_matches += 1
                continue
            
            # STRICT SECURITY: Find exact matricule match - NO FALLBACK
            page_number, match_message = find_employee_page(employee_matricule, reader)
            
            if page_number is None:
                # SECURITY VIOLATION - Do NOT send payslip
                print(f"SECURITY FAILURE: {match_message}")
                print(f"ACTION: Payslip NOT sent to {name} - matricule verification failed")
                failed_matches += 1
                continue
            
            # Security passed - process payslip
            print(f"SECURITY PASSED: {match_message}")
            
            writer = PdfWriter()
            page = reader.pages[page_number]
            page = add_stamp_to_page(page, STAMP_IMAGE)
            writer.add_page(page)

            output_file = f"{OUTPUT_DIR}/Payslip_{name}_Verified.pdf"
            with open(output_file, "wb") as f:
                writer.write(f)

            print(f"SUCCESS: Secure payslip generated for {name}")
            successful_matches += 1

            # Send to multiple email addresses
            emails_sent = send_multiple_emails(email1, email2, name, output_file)
            
            if emails_sent:
                print(f"EMAIL SUMMARY: Payslip sent to {len(emails_sent)} address(es): {', '.join(emails_sent)}")
            else:
                print("EMAIL SUMMARY: No emails sent (all failed)")

        except Exception as e:
            print(f"ERROR: Failed for {row.get('Name', 'Unknown')}: {e}")
            failed_matches += 1

    # Security summary
    print("\n" + "=" * 60)
    print("SECURITY SUMMARY:")
    print(f"  Successful matches: {successful_matches}")
    print(f"  Failed matches: {failed_matches}")
    print(f"  Total employees: {len(employees)}")
    
    if failed_matches > 0:
        print(f"\nSECURITY ALERT: {failed_matches} payslips were NOT sent due to matricule mismatches!")
        print("This protects employee confidentiality and data integrity.")
    else:
        print(f"\nSECURITY SUCCESS: All payslips verified and sent securely!")
    
    print("=" * 60)

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    main()
