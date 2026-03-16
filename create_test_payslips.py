import os
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def create_sample_payslips():
    # Create sample payslips folder
    folder = 'input/payslips'
    os.makedirs(folder, exist_ok=True)
    
    # Sample employee data
    employees = [
        {'name': 'John Doe', 'matricule': '1001'},
        {'name': 'Jane Smith', 'matricule': '1002'},
        {'name': 'Bob Wilson', 'matricule': '1003'}
    ]
    
    print("Creating sample payslip PDFs...")
    
    for emp in employees:
        # Create a simple PDF
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.drawString(100, 750, f'PAYSLIP - {emp["name"]}')
        c.drawString(100, 720, f'MATRICULE: {emp["matricule"]}')
        c.drawString(100, 690, 'Month: March 2026')
        c.drawString(100, 660, 'Basic Salary: 200,000 XAF')
        c.drawString(100, 630, 'Net Salary: 180,000 XAF')
        c.save()
        
        # Move to beginning of buffer
        packet.seek(0)
        
        # Create output PDF
        writer = PdfWriter()
        reader = PdfReader(packet)
        writer.add_page(reader.pages[0])
        
        # Save with matricule in filename
        filename = f'{folder}/Payslip_MAT{emp["matricule"]}_{emp["name"].replace(" ", "_")}.pdf'
        with open(filename, 'wb') as f:
            writer.write(f)
        
        print(f'Created: {filename}')
    
    print(f'\n✅ Sample payslips created in: {folder}')
    print('Now select this folder in the UI to test the system!')

if __name__ == "__main__":
    create_sample_payslips()
