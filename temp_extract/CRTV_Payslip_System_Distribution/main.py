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

# ================== MODE ==================
# True  = simulation (NO real emails sent)
# False = production (real emails sent)
SIMULATION_MODE = True    # 🔴 SET TRUE IF TESTING ONLY

# ================== PATH CONFIG ==================
INPUT_PDF = "input/payslip.pdf"
INPUT_EXCEL = "input/employees - 1.xlsx"
STAMP_IMAGE = "input/Stamp.png"
OUTPUT_DIR = "output/sent_payslips"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== GMAIL SMTP CONFIG ==================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "nerisbi801@gmail.com"      # Sender Gmail
EMAIL_PASSWORD = "qmpp eqym rclo bave"       # Gmail App Password

# ================== EMAIL FUNCTION ==================
def send_email(receiver_email, employee_name, pdf_path):
    if SIMULATION_MODE:
        print(f"📨 [SIMULATION] Email prepared for {receiver_email} with {os.path.basename(pdf_path)}")
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

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# ================== STAMP FUNCTION ==================
def add_stamp_to_page(original_page, stamp_path):
    packet = io.BytesIO()

    page_width = float(original_page.mediabox.width)
    page_height = float(original_page.mediabox.height)

    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Stamp position & size
    x = page_width - 160
    y = 60
    width = 120
    height = 120

    c.drawImage(stamp_path, x, y, width, height, mask="auto")
    c.save()

    packet.seek(0)
    stamp_pdf = PdfReader(packet)

    original_page.merge_page(stamp_pdf.pages[0])
    return original_page

# ================== DEBUG PDF FUNCTION ==================
def debug_pdf_content(reader):
    """Debug function to show PDF content and page count"""
    print(f"\n🔍 PDF DEBUG: Total pages = {len(reader.pages)}")
    
    for i, page in enumerate(reader.pages):
        text = extract_text_from_page(page)
        print(f"\n--- PAGE {i+1} ---")
        print(f"Text length: {len(text)} characters")
        print(f"First 200 chars: {text[:200]}")
        if len(text) > 200:
            print("...")
    
    print(f"\n🔍 END PDF DEBUG\n")

# ================== TEXT EXTRACTION FUNCTION ==================
def extract_text_from_page(page):
    """Extract text from a PDF page"""
    return page.extract_text()

# ================== FIND EMPLOYEE PAGE BY MATRICULE ==================
def find_employee_page_by_matricule(reader, matricule):
    """Find the page number containing the employee's matricule"""
    matricule_str = str(matricule).strip()
    
    for page_num, page in enumerate(reader.pages):
        text = extract_text_from_page(page)
        if matricule_str in text:
            print(f"🔍 Found matricule {matricule_str} on page {page_num + 1}")
            return page_num
    
    print(f"❌ Matricule {matricule_str} not found in any page")
    return None

# ================== MAIN LOGIC ==================
def main():
    if not os.path.exists(INPUT_PDF):
        print("❌ Payslip PDF not found.")
        return

    if not os.path.exists(INPUT_EXCEL):
        print("❌ Employees Excel file not found.")
        return

    if not os.path.exists(STAMP_IMAGE):
        print("❌ Stamp image not found.")
        return

    employees = pd.read_excel(INPUT_EXCEL, engine="openpyxl")
    reader = PdfReader(INPUT_PDF)

    print(f"Total pages in PDF: {len(reader.pages)}")
    print(f"Total employees: {len(employees)}")
    
    # Debug PDF content
    debug_pdf_content(reader)

    # Track used pages to prevent duplicates
    used_pages = set()

    for _, row in employees.iterrows():
        try:
            # Get employee matricule
            matricule = row["Matricule"] if "Matricule" in row else row.get("matricule", "")
            if not matricule:
                print(f"❌ No matricule found for {row.get('Name', 'Unknown')}")
                continue
            
            # Find page by matricule
            page_number = find_employee_page_by_matricule(reader, matricule)
            if page_number is None:
                print(f"❌ No page found for matricule {matricule} ({row.get('Name', 'Unknown')})")
                continue
            
            # Check if page already used
            if page_number in used_pages:
                print(f"⚠️  Page {page_number + 1} already used for another employee. Skipping {row.get('Name', 'Unknown')}")
                continue
            
            used_pages.add(page_number)
            name = re.sub(r"[^a-zA-Z0-9]", "_", str(row["Name"]).strip())
            email = str(row["Email"]).strip()

            writer = PdfWriter()
            page = reader.pages[page_number]
            page = add_stamp_to_page(page, STAMP_IMAGE)
            writer.add_page(page)

            output_file = f"{OUTPUT_DIR}/Payslip_{name}_{matricule}.pdf"
            with open(output_file, "wb") as f:
                writer.write(f)

            print(f"✔ Payslip generated for {name} (Matricule: {matricule}) - Page {page_number + 1}")

            send_email(email, name, output_file)

            if not SIMULATION_MODE:
                print(f"📨 Email sent to {email}")

        except Exception as e:
            print(f"❌ Failed for {row.get('Name', 'Unknown')}: {e}")
    
    print(f"\n📊 Summary: Used {len(used_pages)} out of {len(reader.pages)} pages")

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    main()
