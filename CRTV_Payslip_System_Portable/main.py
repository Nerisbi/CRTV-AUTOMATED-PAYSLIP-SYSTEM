import os
import io
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import smtplib
import pikepdf
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from logger import log_info, log_error

# ================== MODE ==================
# True  = simulation (NO real emails sent)
# False = production (real emails sent)
SIMULATION_MODE = False   # 🔴 SET TRUE IF TESTING ONLY

# ================== PATH CONFIG ==================
INPUT_PDF = "input/payslips.pdf"
INPUT_EXCEL = "input/employees.xlsx"
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

# ================== MAIN LOGIC ==================
def main():
    if not os.path.exists(INPUT_PDF):
        print("ERROR: Payslip PDF not found.")
        return

    if not os.path.exists(INPUT_EXCEL):
        print("ERROR: Employees Excel file not found.")
        return

    if not os.path.exists(STAMP_IMAGE):
        print("ERROR: Stamp image not found.")
        return

    employees = pd.read_excel(INPUT_EXCEL, engine="openpyxl")
    reader = PdfReader(INPUT_PDF)

    print(f"Total pages in PDF: {len(reader.pages)}")
    print(f"Total employees: {len(employees)}")

    # Safety check
    if len(employees) > len(reader.pages):
        print(f"WARNING: More employees ({len(employees)}) than PDF pages ({len(reader.pages)})")
        print("Some employees will not receive payslips.")
    
    if len(reader.pages) > len(employees):
        print(f"INFO: More PDF pages ({len(reader.pages)}) than employees ({len(employees)})")
        print("Some pages will be ignored.")

    for index, row in employees.iterrows():
        try:
            # Use sequential page assignment (no matching needed)
            page_number = index
            
            # Check if page exists
            if page_number >= len(reader.pages):
                print(f"WARNING: Skipping {row.get('Name', 'Unknown')} - no page available")
                continue
                
            name = str(row["Name"]).strip()
            email = str(row["Email"]).strip()

            writer = PdfWriter()
            page = reader.pages[page_number]
            page = add_stamp_to_page(page, STAMP_IMAGE)
            writer.add_page(page)

            output_file = f"{OUTPUT_DIR}/Payslip_{name}.pdf"
            with open(output_file, "wb") as f:
                writer.write(f)

            print(f"SUCCESS: Payslip generated for {name}")

            send_email(email, name, output_file)

            if not SIMULATION_MODE:
                print(f"EMAIL SENT: Email sent to {email}")

        except Exception as e:
            print(f"ERROR: Failed for {row.get('Name', 'Unknown')}: {e}")

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    main()
