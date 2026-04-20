import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
from datetime import datetime
import sys
import io
import smtplib
from email.message import EmailMessage
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

# Import new modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from individual_retrieval import retrieve_individual_payslip, get_employee_by_matricule, update_employee_email
    from excel_editor import open_excel_editor
    from multi_pdf_aggregator import retrieve_historical_payslips, get_pdf_info, validate_pdf_files
    INDIVIDUAL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Individual retrieval modules not available: {e}")
    INDIVIDUAL_MODULES_AVAILABLE = False

# Add OCR imports (optional - will handle gracefully)
try:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ================== COPIED FROM main.py - ADVANCED FUNCTIONS ==================

# Global variables
SIMULATION_MODE = True
current_pdf_path = ""
current_excel_path = ""

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

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login("nerisbi801@gmail.com", "qmpp eqym rclo bave")
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

def extract_text_from_pdf_page(page, page_num):
    """Extract text from PDF page using multiple methods including OCR"""
    
    # Method 1: Try direct text extraction first
    text = page.extract_text()
    if text and text.strip():
        return text
    
    # Method 2: Use PyMuPDF for better text extraction (if available)
    if OCR_AVAILABLE:
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

class FixedCompactUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Window configuration
        self.root.title("CRTV Payslip Distribution System")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # Center window
        self.center_window()
        
        # Professional Color Palette
        self.bg_color = '#f8fafc'  # Light gray background
        self.card_color = '#ffffff'  # Pure white cards
        self.primary_color = '#1e40af'  # Deep blue - professional
        self.success_color = '#059669'  # Emerald green
        self.warning_color = '#d97706'  # Amber
        self.danger_color = '#dc2626'  # Red (kept for errors)
        self.info_color = '#0891b2'  # Cyan blue
        self.text_primary = '#1e293b'  # Dark slate text
        self.text_secondary = '#64748b'  # Medium slate text
        self.border_color = '#e2e8f0'  # Light border
        self.hover_color = '#f1f5f9'  # Hover state
        self.shadow_color = '#0f172a'  # Shadow base
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.pdf_path = tk.StringVar(value="")  # Start empty - user must select
        self.excel_path = tk.StringVar(value="")  # Start empty - user must select
        self.simulation_mode = tk.BooleanVar(value=False)
        self.processing = False
        self.stats = {
            'total_employees': 0,
            'processed': 0,
            'sent': 0,
            'failed': 0
        }
        
        # Create UI
        self.create_main_layout()
        self.create_header()
        self.create_dashboard()
        self.create_file_section()
        self.create_control_section()
        self.create_log_section()
        self.create_individual_retrieval_ui()
        
        # Initialize
        self.update_file_status()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.bulk_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.individual_frame = tk.Frame(self.notebook, bg=self.bg_color)
        
        self.notebook.add(self.bulk_frame, text="Bulk Distribution")
        self.notebook.add(self.individual_frame, text="Individual Retrieval")
        
        # Store reference for bulk operations
        self.current_frame = self.bulk_frame
        
    def create_header(self):
        # Modern header with subtle gradient effect
        header_frame = tk.Frame(self.bulk_frame, bg=self.primary_color, height=40, relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Add subtle border bottom
        border_frame = tk.Frame(header_frame, bg=self.border_color, height=1)
        border_frame.place(relx=0, rely=1, relwidth=1)
        
        # Main title with better spacing
        title_container = tk.Frame(header_frame, bg=self.primary_color)
        title_container.pack(side=tk.LEFT, padx=10, pady=8)
        
        tk.Label(
            title_container, 
            text="CRTV Payslip Distribution System",
            font=('Segoe UI', 20, 'bold'),
            bg=self.primary_color,
            fg='white'
        ).pack()
        
        tk.Label(
            title_container,
            text="Professional Employee Payslip Management",
            font=('Segoe UI', 9),
            bg=self.primary_color,
            fg='#e2e8f0'
        ).pack()
        
        # Status indicator with modern styling
        status_container = tk.Frame(header_frame, bg=self.primary_color)
        status_container.pack(side=tk.RIGHT, padx=10, pady=8)
        
        self.status_label = tk.Label(
            status_container,
            text="● Ready",
            font=('Segoe UI', 11, 'bold'),
            bg=self.primary_color,
            fg='#94a3b8'
        )
        self.status_label.pack()
        
    def create_dashboard(self):
        # Modern dashboard with subtle shadow and border
        dashboard_frame = tk.Frame(self.bulk_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        dashboard_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add subtle border and shadow effect
        border_frame = tk.Frame(dashboard_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Dashboard title with better styling
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=10, pady=(8, 3))
        
        tk.Label(
            title_frame,
            text="📊 Dashboard Overview",
            font=('Segoe UI', 14, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Real-time payslip distribution metrics",
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(2, 0))
        
        # Modern cards container
        cards_frame = tk.Frame(border_frame, bg=self.card_color)
        cards_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.create_modern_stat_card(cards_frame, "Total Employees", "0", self.info_color, 0)
        self.create_modern_stat_card(cards_frame, "Processed", "0", self.warning_color, 1)
        self.create_modern_stat_card(cards_frame, "Sent", "0", self.success_color, 2)
        self.create_modern_stat_card(cards_frame, "Failed", "0", self.danger_color, 3)
        
    def create_modern_stat_card(self, parent, title, value, color, column):
        # Modern card with subtle border and better spacing
        card = tk.Frame(parent, bg=self.card_color, relief=tk.FLAT, bd=0, width=200)
        card.grid(row=0, column=column, padx=8, sticky="ew", pady=5)
        parent.grid_columnconfigure(column, weight=1)
        
        # Add subtle border
        border = tk.Frame(card, bg=self.border_color, relief=tk.FLAT, bd=1)
        border.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Main content with rounded corner effect simulation
        content_frame = tk.Frame(border, bg=self.card_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Top section with icon and title
        top_frame = tk.Frame(content_frame, bg=self.card_color)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Icon/indicator
        icon_label = tk.Label(
            top_frame,
            text="●",
            font=('Segoe UI', 12),
            bg=self.card_color,
            fg=color
        )
        icon_label.pack(side=tk.LEFT)
        
        # Title
        title_label = tk.Label(
            top_frame, 
            text=title, 
            font=('Segoe UI', 9, 'bold'),
            bg=self.card_color,
            fg=self.text_secondary
        )
        title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Value with emphasis
        value_label = tk.Label(
            content_frame, 
            text=value, 
            font=('Segoe UI', 18, 'bold'),
            bg=self.card_color,
            fg=color
        )
        value_label.pack(anchor=tk.W)
        
        # Store reference with updated naming
        attr_name = f"{title.lower().replace(' ', '_').replace('total_', '')}_label"
        setattr(self, attr_name, value_label)
    
    def create_stat_card(self, parent, title, value, color, column):
        # Keep for backward compatibility, delegate to modern version
        self.create_modern_stat_card(parent, title, value, color, column)
        
    def create_file_section(self):
        # Modern file section with subtle border
        file_frame = tk.Frame(self.bulk_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Add border
        border_frame = tk.Frame(file_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="📁 File Management",
            font=('Segoe UI', 14, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Select payslip PDF and employee Excel files",
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(2, 0))
        
        # ACTION BUTTONS - Direct placement below file selection comment
        button_frame = tk.Frame(border_frame, bg=self.card_color)
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        self.validate_btn = tk.Button(
            button_frame,
            text="✓ Validate Files",
            command=self.validate_files,
            font=('Segoe UI', 11, 'bold'),
            bg=self.warning_color,
            fg='white',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_btn = tk.Button(
            button_frame,
            text="⚡ Process Data",
            command=self.start_processing,
            font=('Segoe UI', 11, 'bold'),
            bg=self.success_color,
            fg='white',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.send_btn = tk.Button(
            button_frame,
            text="📤 Send Payslips",
            command=self.send_payslips,
            font=('Segoe UI', 11, 'bold'),
            bg=self.primary_color,
            fg='white',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        self.send_btn.pack(side=tk.LEFT)
        
        # Modern file controls container
        file_controls = tk.Frame(border_frame, bg=self.card_color)
        file_controls.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # PDF Row with modern styling
        pdf_container = tk.Frame(file_controls, bg=self.hover_color, relief=tk.FLAT, bd=1)
        pdf_container.pack(fill=tk.X, pady=(0, 10))
        
        pdf_row = tk.Frame(pdf_container, bg=self.hover_color)
        pdf_row.pack(fill=tk.X, padx=12, pady=10)
        
        tk.Label(pdf_row, text="📄", font=('Segoe UI', 12), bg=self.hover_color, fg=self.info_color).pack(side=tk.LEFT)
        tk.Label(pdf_row, text="Payslip PDF:", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_primary).pack(side=tk.LEFT, padx=(8, 15))
        self.pdf_path_label = tk.Label(pdf_row, text="No file selected", bg=self.hover_color, fg=self.text_secondary, font=('Segoe UI', 9))
        self.pdf_path_label.pack(side=tk.LEFT, padx=(0, 15))
        self.pdf_status = tk.Label(pdf_row, text="●", bg=self.hover_color, fg=self.text_secondary, font=('Arial', 10))
        self.pdf_status.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(pdf_row, text="Browse Files", command=self.browse_pdf, font=('Segoe UI', 9, 'bold'), bg=self.primary_color, fg='white', padx=12, pady=6, relief=tk.FLAT, bd=0).pack(side=tk.LEFT)
        
        # Excel Row with modern styling
        excel_container = tk.Frame(file_controls, bg=self.hover_color, relief=tk.FLAT, bd=1)
        excel_container.pack(fill=tk.X, pady=(0, 10))
        
        excel_row = tk.Frame(excel_container, bg=self.hover_color)
        excel_row.pack(fill=tk.X, padx=12, pady=10)
        
        tk.Label(excel_row, text="📊", font=('Segoe UI', 12), bg=self.hover_color, fg=self.success_color).pack(side=tk.LEFT)
        tk.Label(excel_row, text="Employee Excel:", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_primary).pack(side=tk.LEFT, padx=(8, 15))
        self.excel_path_label = tk.Label(excel_row, text="No file selected", bg=self.hover_color, fg=self.text_secondary, font=('Segoe UI', 9))
        self.excel_path_label.pack(side=tk.LEFT, padx=(0, 15))
        self.excel_status = tk.Label(excel_row, text="●", bg=self.hover_color, fg=self.text_secondary, font=('Arial', 10))
        self.excel_status.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(excel_row, text="Browse Files", command=self.browse_excel, font=('Segoe UI', 9, 'bold'), bg=self.primary_color, fg='white', padx=12, pady=6, relief=tk.FLAT, bd=0).pack(side=tk.LEFT)
        
        # Modern info label
        self.file_info_label = tk.Label(border_frame, text="Please select both files to continue", font=('Segoe UI', 9), bg=self.card_color, fg=self.text_secondary)
        self.file_info_label.pack(anchor=tk.W, padx=20, pady=(0, 15))
        
    def create_control_section(self):
        # Modern control section with subtle border
        control_frame = tk.Frame(self.bulk_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Add border
        border_frame = tk.Frame(control_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="⚙️ Control Panel",
            font=('Segoe UI', 14, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Configure settings and manage payslip distribution",
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(2, 0))
        
        # Modern settings section
        settings_frame = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        settings_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        settings_content = tk.Frame(settings_frame, bg=self.hover_color)
        settings_content.pack(fill=tk.X, padx=15, pady=12)
        
        tk.Checkbutton(
            settings_content,
            text="🔍 Simulation Mode (Uncheck for REAL emails)",
            variable=self.simulation_mode,
            bg=self.hover_color,
            font=('Segoe UI', 10, 'bold'),
            fg=self.text_primary,
            selectcolor=self.hover_color,
            activebackground=self.hover_color
        ).pack(side=tk.LEFT)
        
        tk.Button(
            settings_content,
            text="📧 Email Settings",
            command=self.show_email_config,
            font=('Segoe UI', 9, 'bold'),
            bg=self.info_color,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.RIGHT)
        
        # Modern progress bar section
        progress_frame = tk.Frame(border_frame, bg=self.card_color)
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(
            progress_frame,
            text="Progress",
            font=('Segoe UI', 10, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        progress_container = tk.Frame(progress_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            variable=self.progress_var,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(padx=10, pady=8)
        
        # SEND PAYSLIPS BUTTON - Direct placement for visibility
        self.send_btn = tk.Button(
            border_frame,
            text="📤 SEND ALL PAYSLIPS",
            command=self.send_payslips,
            font=('Segoe UI', 12, 'bold'),
            bg='#dc2626',
            fg='white',
            padx=30,
            pady=12,
            relief=tk.RAISED,
            bd=2
        )
        self.send_btn.pack(pady=10)
        
        # Primary action buttons
        primary_buttons = tk.Frame(border_frame, bg=self.card_color)
        primary_buttons.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.validate_btn = tk.Button(
            primary_buttons,
            text="✓ Validate Files",
            command=self.validate_files,
            font=('Segoe UI', 10, 'bold'),
            bg=self.warning_color,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_btn = tk.Button(
            primary_buttons,
            text="⚡ Process Data",
            command=self.start_processing,
            font=('Segoe UI', 10, 'bold'),
            bg=self.success_color,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            width=15
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.send_btn = tk.Button(
            primary_buttons,
            text="📤 Send Payslips",
            command=self.send_payslips,
            font=('Segoe UI', 10, 'bold'),
            bg=self.primary_color,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            width=18
        )
        self.send_btn.pack(side=tk.LEFT)
        
        # Secondary controls
        secondary_frame = tk.Frame(control_frame, bg=self.card_color)
        secondary_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.stop_btn = tk.Button(
            secondary_frame,
            text="⏹ Stop Process",
            command=self.stop_processing,
            font=('Segoe UI', 9),
            bg=self.danger_color,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            width=15,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status display
        self.processing_status = tk.Label(
            secondary_frame,
            text="● Ready",
            font=('Segoe UI', 10, 'bold'),
            bg=self.card_color,
            fg=self.text_secondary
        )
        self.processing_status.pack(side=tk.RIGHT, padx=(10, 0))
        
    def create_log_section(self):
        # Modern log section with subtle border
        log_frame = tk.Frame(self.bulk_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add border
        border_frame = tk.Frame(log_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="📋 Activity Log",
            font=('Segoe UI', 14, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Real-time system activity and events",
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(
            title_frame,
            text="🗑️ Clear",
            command=self.clear_log,
            font=('Segoe UI', 9, 'bold'),
            bg=self.danger_color,
            fg='white',
            padx=12,
            pady=6,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.RIGHT)
        
        # Modern log container
        log_container = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        self.log_text = tk.Text(
            log_container,
            height=5,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=self.card_color,
            fg=self.text_primary,
            relief=tk.FLAT,
            bd=0,
            selectbackground=self.primary_color
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        self.add_log("System ready", "success")
        
    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select Payslip PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            display_name = os.path.basename(filename)
            if len(display_name) > 30:
                display_name = display_name[:27] + "..."
            self.pdf_path_label.config(text=display_name)
            self.update_file_status()
            
    def browse_excel(self):
        filename = filedialog.askopenfilename(
            title="Select Employee Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path.set(filename)
            display_name = os.path.basename(filename)
            if len(display_name) > 30:
                display_name = display_name[:27] + "..."
            self.excel_path_label.config(text=display_name)
            self.update_file_status()
            
    def update_file_status(self):
        pdf_exists = os.path.exists(self.pdf_path.get())
        excel_exists = os.path.exists(self.excel_path.get())
        
        self.pdf_status.config(fg=self.success_color if pdf_exists else self.danger_color)
        self.excel_status.config(fg=self.success_color if excel_exists else self.danger_color)
        
        if pdf_exists and excel_exists:
            try:
                df = pd.read_excel(self.excel_path.get())
                employee_count = len(df)
                self.stats['total_employees'] = employee_count
                self.employees_label.config(text=str(employee_count))
                
                from PyPDF2 import PdfReader
                reader = PdfReader(self.pdf_path.get())
                page_count = len(reader.pages)
                
                self.file_info_label.config(
                    text=f"OK {employee_count} employees, {page_count} PDF pages",
                    fg=self.success_color
                )
            except Exception as e:
                self.file_info_label.config(
                    text=f"Error: {str(e)[:30]}...",
                    fg=self.danger_color
                )
        else:
            self.file_info_label.config(
                text="! Select PDF and Excel files",
                fg=self.warning_color
            )
            
    def validate_files(self):
        self.add_log("Validating files...", "info")
        self.update_file_status()
        
        if os.path.exists(self.pdf_path.get()) and os.path.exists(self.excel_path.get()):
            try:
                df = pd.read_excel(self.excel_path.get())
                required_columns = ['Name', 'Email']
                missing = [col for col in required_columns if col not in df.columns]
                
                if missing:
                    self.add_log(f"Missing columns: {missing}", "error")
                    messagebox.showerror("Error", f"Missing columns: {missing}")
                else:
                    self.add_log(f"OK Valid: {len(df)} employees", "success")
                    messagebox.showinfo("Success", f"Files ready!\nEmployees: {len(df)}")
                    
            except Exception as e:
                self.add_log(f"Validation failed: {e}", "error")
                messagebox.showerror("Error", f"Validation failed: {e}")
        else:
            self.add_log("Files not found", "error")
            messagebox.showerror("Error", "Select both files first")
            
    def start_processing(self):
        if not os.path.exists(self.pdf_path.get()) or not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Error", "Select valid files first")
            return
            
        self.processing = True
        self.process_btn.config(state='disabled')
        self.send_btn.config(state='disabled')
        self.validate_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_var.set(0)
        
        self.add_log(f"Starting processing - Simulation: {self.simulation_mode.get()}", "info")
        self.status_label.config(text="Processing", fg='#fbbf24')
        
        # Run directly without threading
        self.process_thread_direct()
        
    def process_thread_direct(self):
        """Process payslips directly without threading"""
        try:
            self.progress_var.set(10)
            self.processing_status.config(text="Reading data...")
            
            df = pd.read_excel(self.excel_path.get())
            total = len(df)
            
            self.progress_var.set(30)
            processed = sent = failed = 0
            
            for i, row in df.iterrows():
                if not self.processing:
                    break
                    
                try:
                    name = str(row["Name"]).strip()
                    email = str(row["Email"]).strip()
                    
                    progress = 30 + (70 * (i + 1) / total)
                    self.progress_var.set(progress)
                    
                    processed += 1
                    if not self.simulation_mode.get():
                        sent += 1
                    
                    self.add_log(f"OK {name}", "success")
                    self.stats['processed'] = processed
                    self.stats['sent'] = sent
                    self.update_stats_display()
                    
                except Exception as e:
                    failed += 1
                    self.stats['failed'] = failed
                    self.add_log(f"ERROR {row.get('Name', '?')}: {e}", "error")
                    self.update_stats_display()
                    
            if self.processing:
                self.progress_var.set(100)
                self.processing_status.config(text="Done!")
                self.add_log(f"Complete: {processed} processed, {sent} sent, {failed} failed", "success")
                self.status_label.config(text="Complete", fg=self.success_color)
                
                messagebox.showinfo(
                    "Complete",
                    f"Processing done!\n\nTotal: {total}\nProcessed: {processed}\nSent: {sent}\nFailed: {failed}"
                )
            
        except Exception as e:
            self.add_log(f"Error: {e}", "error")
            messagebox.showerror("Error", f"Processing failed: {e}")
            self.status_label.config(text="Error", fg=self.danger_color)
            
        finally:
            self.processing = False
            self.process_btn.config(state='normal')
            self.send_btn.config(state='normal')
            self.validate_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
        
    def send_payslips(self):
        """Advanced payslip sending with OCR, matricule matching, and security"""
        if not os.path.exists(self.pdf_path.get()) or not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Error", "Select valid files first")
            return

        if not self.simulation_mode.get():
            confirm = messagebox.askyesno(
                "Confirm Sending",
                "This will send REAL emails to all employees.\nProceed?"
            )
            if not confirm:
                return

        self.processing = True
        self.process_btn.config(state='disabled')
        self.send_btn.config(state='disabled')
        self.validate_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_var.set(0)

        try:
            # Set global variables for OCR functions
            global current_pdf_path, current_excel_path, SIMULATION_MODE
            current_pdf_path = self.pdf_path.get()
            current_excel_path = self.excel_path.get()
            SIMULATION_MODE = self.simulation_mode.get()

            # Create output directory
            os.makedirs("output/sent_payslips", exist_ok=True)

            # Read files
            df = pd.read_excel(current_excel_path)
            reader = PdfReader(current_pdf_path)

            total = len(df)
            successful_matches = 0
            failed_matches = 0

            self.add_log(f"Starting secure processing: {total} employees", "info")
            self.add_log(f"PDF pages: {len(reader.pages)}", "info")

            # Security validation
            if len(df) != len(reader.pages):
                self.add_log(f"WARNING: Employee count ({len(df)}) != PDF pages ({len(reader.pages)})", "warning")

            for i, row in df.iterrows():
                if not self.processing:
                    break

                try:
                    # Get employee data
                    employee_matricule = str(row.get('Matricule', '')).strip()
                    name = str(row["Name"]).strip()
                    email1 = str(row.get('Email', '')).strip()
                    email2 = str(row.get('Email 2', '')).strip()

                    self.add_log(f"Processing: {name} (matricule: '{employee_matricule}')", "info")

                    # Validate at least one email exists
                    if not email1 and not email2:
                        self.add_log(f"FAILED: {name} - No email addresses", "error")
                        failed_matches += 1
                        continue

                    # SECURITY: Find exact matricule match
                    page_number, match_message = find_employee_page(employee_matricule, reader)

                    if page_number is None:
                        # SECURITY VIOLATION - Do NOT send payslip
                        self.add_log(f"SECURITY FAILURE: {name} - {match_message}", "error")
                        failed_matches += 1
                        continue

                    # Security passed - process payslip
                    self.add_log(f"SECURITY PASSED: {name} - {match_message}", "success")

                    # Create stamped payslip
                    writer = PdfWriter()
                    page = reader.pages[page_number]
                    stamp_path = "input/Stamp.png"
                    if os.path.exists(stamp_path):
                        page = add_stamp_to_page(page, stamp_path)
                    writer.add_page(page)

                    output_file = f"output/sent_payslips/Payslip_{name}_Verified.pdf"
                    with open(output_file, "wb") as f:
                        writer.write(f)

                    # Send to multiple email addresses
                    emails_sent = send_multiple_emails(email1, email2, name, output_file)

                    if emails_sent:
                        self.add_log(f"SUCCESS: {name} - Sent to {len(emails_sent)} address(es)", "success")
                        successful_matches += 1
                    else:
                        self.add_log(f"FAILED: {name} - All emails failed", "error")
                        failed_matches += 1

                except Exception as e:
                    self.add_log(f"ERROR: {row.get('Name', 'Unknown')} - {e}", "error")
                    failed_matches += 1

                # Update progress
                progress = ((i + 1) / total) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            # Final summary
            self.add_log(f"SECURITY SUMMARY: {successful_matches} successful, {failed_matches} failed", "success")
            
            if failed_matches > 0:
                self.add_log(f"ALERT: {failed_matches} payslips NOT sent for security", "warning")
            else:
                self.add_log("SUCCESS: All payslips verified and sent securely!", "success")

            messagebox.showinfo(
                "Processing Complete",
                f"Total Employees: {total}\n"
                f"Successful: {successful_matches}\n"
                f"Failed: {failed_matches}\n"
                f"Mode: {'Simulation' if self.simulation_mode.get() else 'Real Emails'}\n\n"
                f"Check output/sent_payslips/ for generated files."
            )

        except Exception as e:
            self.add_log(f"Critical Error: {e}", "error")
            messagebox.showerror("Error", str(e))

        finally:
            self.processing = False
            self.process_btn.config(state='normal')
            self.send_btn.config(state='normal')
            self.validate_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
        
    def stop_processing(self):
        self.processing = False
        self.add_log("Stopped by user", "warning")
        self.status_label.config(text="● Stopped", fg=self.warning_color)
        
    def update_stats_display(self):
        self.processed_label.config(text=str(self.stats['processed']))
        self.sent_label.config(text=str(self.stats['sent']))
        self.failed_label.config(text=str(self.stats['failed']))
        
    def show_email_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Email Settings")
        config_window.geometry("400x300")
        config_window.transient(self.root)
        config_window.grab_set()
        config_window.configure(bg=self.bg_color)
        
        tk.Label(config_window, text="Email Configuration", font=('Segoe UI', 12, 'bold'), bg=self.bg_color, fg=self.primary_color).pack(pady=15)
        
        config_frame = tk.Frame(config_window, bg=self.card_color, relief=tk.RAISED, bd=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        fields = [
            ("SMTP:", "smtp.gmail.com"),
            ("Port:", "465"),
            ("Email:", "nerisbi801@gmail.com"),
            ("Password:", "qmpp eqym rclo bave")
        ]
        
        for i, (label, default) in enumerate(fields):
            tk.Label(config_frame, text=label, font=('Segoe UI', 10, 'bold'), bg=self.card_color).grid(row=i, column=0, sticky=tk.W, padx=15, pady=8)
            entry = tk.Entry(config_frame, font=('Segoe UI', 9), width=25)
            entry.insert(0, default)
            if "Password" in label:
                entry.config(show="*")
            entry.grid(row=i, column=1, sticky=tk.EW, padx=(0, 15), pady=8)
        
        config_frame.grid_columnconfigure(1, weight=1)
        
        button_frame = tk.Frame(config_window, bg=self.bg_color)
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Test", font=('Segoe UI', 9), bg=self.info_color, fg='white', width=8).pack(side=tk.LEFT, padx=3)
        tk.Button(button_frame, text="Save", font=('Segoe UI', 9, 'bold'), bg=self.success_color, fg='white', width=8, command=config_window.destroy).pack(side=tk.LEFT, padx=3)
        tk.Button(button_frame, text="Cancel", font=('Segoe UI', 9), bg='#6b7280', fg='white', width=8, command=config_window.destroy).pack(side=tk.LEFT, padx=3)
        
    def add_log(self, message, log_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": self.info_color,
            "success": self.success_color, 
            "error": self.danger_color,
            "warning": self.warning_color
        }
        
        icons = {
            "info": "",
            "success": "✓ ",
            "error": "✗ ",
            "warning": "! "
        }
        
        color = colors.get(log_type, "#374151")
        icon = icons.get(log_type, "")
        
        log_entry = f"[{timestamp}] {icon}{message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.tag_add(log_type, f"end-2c linestart", f"end-1c")
        self.log_text.tag_config(log_type, foreground=color)
        self.log_text.see(tk.END)
        
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 500:
            self.log_text.delete("1.0", "50.0")
            
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.add_log("Log cleared", "info")
    
    def create_individual_retrieval_ui(self):
        """Create the individual retrieval UI components"""
        # Modern header for individual tab
        header_frame = tk.Frame(self.individual_frame, bg=self.primary_color, height=35, relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 3))
        header_frame.pack_propagate(False)
        
        # Add subtle border bottom
        border_frame = tk.Frame(header_frame, bg=self.border_color, height=1)
        border_frame.place(relx=0, rely=1, relwidth=1)
        
        # Title container
        title_container = tk.Frame(header_frame, bg=self.primary_color)
        title_container.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(
            title_container, 
            text="Individual Payslip Retrieval",
            font=('Segoe UI', 18, 'bold'),
            bg=self.primary_color,
            fg='white'
        ).pack()
        
        tk.Label(
            title_container,
            text="Single employee payslip management",
            font=('Segoe UI', 9),
            bg=self.primary_color,
            fg='#e2e8f0'
        ).pack()
        
        tk.Button(
            header_frame,
            text="✏️ Edit Employee Data",
            command=self.open_employee_editor,
            font=('Segoe UI', 10, 'bold'),
            bg=self.card_color,
            fg=self.primary_color,
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Modern input section
        input_frame = tk.Frame(self.individual_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add border
        border_frame = tk.Frame(input_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(8, 5))
        
        tk.Label(
            title_frame,
            text="👤 Employee Information",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Enter employee details for payslip retrieval",
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # Modern input fields
        fields_frame = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        fields_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        fields_content = tk.Frame(fields_frame, bg=self.hover_color)
        fields_content.pack(fill=tk.X, padx=15, pady=8)
        
        # Matricule field with modern styling
        matricule_frame = tk.Frame(fields_content, bg=self.hover_color)
        matricule_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(matricule_frame, text="🔢 Matricule:", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_primary, width=15, anchor='w').pack(side=tk.LEFT)
        self.individual_matricule = tk.StringVar()
        tk.Entry(matricule_frame, textvariable=self.individual_matricule, font=('Segoe UI', 10), width=25, relief=tk.FLAT, bd=1, bg=self.card_color).pack(side=tk.LEFT, padx=5)
        
        # Email field with modern styling
        email_frame = tk.Frame(fields_content, bg=self.hover_color)
        email_frame.pack(fill=tk.X)
        
        tk.Label(email_frame, text="📧 Email:", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_primary, width=15, anchor='w').pack(side=tk.LEFT)
        self.individual_email = tk.StringVar()
        tk.Entry(email_frame, textvariable=self.individual_email, font=('Segoe UI', 10), width=35, relief=tk.FLAT, bd=1, bg=self.card_color).pack(side=tk.LEFT, padx=5)
        
        # Modern file selection section
        file_frame = tk.Frame(self.individual_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        file_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Add border
        border_frame = tk.Frame(file_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(8, 5))
        
        tk.Label(
            title_frame,
            text="📄 Payslip File",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Select the payslip PDF file for processing",
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # Modern file controls
        file_controls = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        file_controls.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        file_content = tk.Frame(file_controls, bg=self.hover_color)
        file_content.pack(fill=tk.X, padx=15, pady=12)
        
        tk.Label(file_content, text="📁 PDF File:", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_primary, width=12, anchor='w').pack(side=tk.LEFT)
        self.individual_pdf_label = tk.Label(file_content, text="No file selected", bg=self.hover_color, fg=self.text_secondary, font=('Segoe UI', 9))
        self.individual_pdf_label.pack(side=tk.LEFT, padx=(8, 15))
        tk.Button(file_content, text="📂 Browse Files", command=self.browse_individual_pdf, font=('Segoe UI', 9, 'bold'), bg=self.primary_color, fg='white', padx=12, pady=6, relief=tk.FLAT, bd=0).pack(side=tk.LEFT)
        tk.Button(file_content, text="➕ Add Multiple PDFs", command=self.add_multiple_pdfs, font=('Segoe UI', 9, 'bold'), bg=self.info_color, fg='white', padx=12, pady=6, relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=(5, 0))
        
        # PDF List Display Section
        pdf_list_frame = tk.Frame(border_frame, bg=self.card_color)
        pdf_list_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        tk.Label(pdf_list_frame, text="📋 Selected PDF Files:", font=('Segoe UI', 10, 'bold'), bg=self.card_color, fg=self.text_primary).pack(anchor=tk.W, pady=(0, 5))
        
        # Create listbox with scrollbar for PDF files
        list_container = tk.Frame(pdf_list_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        list_container.pack(fill=tk.X, pady=(0, 5))
        
        pdf_scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        pdf_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.individual_pdf_listbox = tk.Listbox(
            list_container,
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg=self.text_primary,
            selectmode=tk.MULTIPLE,
            height=3,
            relief=tk.FLAT,
            bd=0,
            selectbackground=self.primary_color,
            yscrollcommand=pdf_scrollbar.set
        )
        self.individual_pdf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        pdf_scrollbar.config(command=self.individual_pdf_listbox.yview)
        
        # Clear PDFs button
        tk.Button(pdf_list_frame, text="🗑️ Clear All PDFs", command=self.clear_individual_pdfs, font=('Segoe UI', 9, 'bold'), bg=self.danger_color, fg='white', padx=12, pady=6, relief=tk.FLAT, bd=0).pack(anchor=tk.W)
        
        # Initialize PDF list
        self.individual_pdf_files = []
        
        # Modern action buttons section
        action_frame = tk.Frame(self.individual_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        action_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Add border
        border_frame = tk.Frame(action_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(8, 5))
        
        tk.Label(
            title_frame,
            text="⚡ Actions",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Validate employee and retrieve payslip",
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # Modern buttons container
        buttons_frame = tk.Frame(border_frame, bg=self.card_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        # Primary action buttons
        primary_buttons = tk.Frame(buttons_frame, bg=self.card_color)
        primary_buttons.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            primary_buttons,
            text="✓ Validate Employee",
            command=self.validate_individual_employee,
            font=('Segoe UI', 10, 'bold'),
            bg=self.warning_color,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            primary_buttons,
            text="📤 Retrieve & Send Payslip",
            command=self.retrieve_individual_payslip,
            font=('Segoe UI', 10, 'bold'),
            bg=self.success_color,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            width=22
        ).pack(side=tk.LEFT)
        
        # Status display
        status_frame = tk.Frame(buttons_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X)
        
        self.individual_status = tk.Label(status_frame, text="● Ready", font=('Segoe UI', 10, 'bold'), bg=self.hover_color, fg=self.text_secondary)
        self.individual_status.pack(anchor=tk.W, padx=15, pady=10)
        
        # Modern individual log section
        log_frame = tk.Frame(self.individual_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Add border
        border_frame = tk.Frame(log_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(8, 5))
        
        tk.Label(
            title_frame,
            text="📋 Individual Retrieval Log",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Individual payslip processing events",
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(
            title_frame,
            text="🗑️ Clear",
            command=self.clear_individual_log,
            font=('Segoe UI', 9, 'bold'),
            bg=self.danger_color,
            fg='white',
            padx=12,
            pady=6,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.RIGHT)
        
        # Modern log container
        log_container = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        self.individual_log_text = tk.Text(
            log_container,
            font=('Consolas', 9),
            bg=self.card_color,
            fg=self.text_primary,
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            height=4,
            selectbackground=self.primary_color
        )
        
        individual_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.individual_log_text.yview)
        self.individual_log_text.configure(yscrollcommand=individual_scroll.set)
        
        self.individual_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        individual_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))
        
        # Initialize individual PDF path
        self.individual_pdf_path = ""
        
        # Multi-PDF variables
        self.multi_pdf_paths = []
        self.multi_pdf_listbox = None
        
        # Create Multi-PDF section
        self.create_multi_pdf_ui()
    
    def browse_individual_pdf(self):
        """Browse for individual payslip PDF"""
        file_path = filedialog.askopenfilename(
            title="Select Payslip PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.individual_pdf_path = file_path
            self.individual_pdf_label.config(text=os.path.basename(file_path))
            self.add_individual_pdf_to_list(file_path)
            self.add_individual_log(f"PDF selected: {os.path.basename(file_path)}", "info")
    
    def add_multiple_pdfs(self):
        """Add multiple PDF files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_paths:
            for file_path in file_paths:
                self.add_individual_pdf_to_list(file_path)
            self.add_individual_log(f"Added {len(file_paths)} PDF files", "success")
    
    def add_individual_pdf_to_list(self, file_path):
        """Add PDF file to the list display"""
        if file_path not in self.individual_pdf_files:
            self.individual_pdf_files.append(file_path)
            self.individual_pdf_listbox.insert(tk.END, os.path.basename(file_path))
            # Update label to show count
            if len(self.individual_pdf_files) == 1:
                self.individual_pdf_label.config(text=os.path.basename(file_path))
            else:
                self.individual_pdf_label.config(text=f"{len(self.individual_pdf_files)} files selected")
    
    def clear_individual_pdfs(self):
        """Clear all selected PDF files"""
        self.individual_pdf_files.clear()
        self.individual_pdf_listbox.delete(0, tk.END)
        self.individual_pdf_path = ""
        self.individual_pdf_label.config(text="No file selected")
        self.add_individual_log("All PDF files cleared", "info")
    
    def validate_individual_employee(self):
        """Validate individual employee information"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Individual retrieval modules not available")
            return
            
        matricule = self.individual_matricule.get().strip()
        email = self.individual_email.get().strip()
        
        if not matricule or not email:
            messagebox.showerror("Validation Error", "Please enter both matricule and email")
            return
        
        if not self.excel_path.get():
            messagebox.showerror("Error", "Please select employee Excel file in Bulk Distribution tab first")
            return
        
        # Validate employee
        found, employee_data = get_employee_by_matricule(matricule, self.excel_path.get())
        
        if found:
            self.add_individual_log(f"Employee found: {employee_data['name']} ({employee_data['matricule']})", "success")
            self.add_individual_log(f"Emails on record: {employee_data['email1']} | {employee_data['email2']}", "info")
            
            # Check if provided email matches
            if email.lower() in [emp_email.lower() for emp_email in [employee_data['email1'], employee_data['email2']] if emp_email]:
                self.add_individual_log("Email validation: PASSED", "success")
                self.individual_status.config(text="Employee validated", fg=self.success_color)
            else:
                self.add_individual_log(f"Email validation: FAILED - '{email}' not found in records", "error")
                self.individual_status.config(text="Email mismatch", fg=self.danger_color)
        else:
            self.add_individual_log(f"Employee not found: {matricule}", "error")
            self.individual_status.config(text="Employee not found", fg=self.danger_color)
    
    def retrieve_individual_payslip(self):
        """Retrieve and send individual payslip"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Individual retrieval modules not available")
            return
            
        matricule = self.individual_matricule.get().strip()
        email = self.individual_email.get().strip()
        
        if not matricule or not email:
            messagebox.showerror("Error", "Please enter both matricule and email")
            return
        
        if not self.individual_pdf_files:
            messagebox.showerror("Error", "Please select at least one payslip PDF file")
            return
        
        if not self.excel_path.get():
            messagebox.showerror("Error", "Please select employee Excel file in Bulk Distribution tab first")
            return
        
        try:
            self.individual_status.config(text="Processing...", fg=self.warning_color)
            self.add_individual_log("Starting individual payslip retrieval...", "info")
            
            # Use the individual retrieval function with multiple PDFs
            success, message, output_file = retrieve_individual_payslip(
                matricule, email, self.individual_pdf_files, self.excel_path.get(), self.simulation_mode.get()
            )
            
            if success:
                self.add_individual_log(f"SUCCESS: {message}", "success")
                self.add_individual_log(f"Output file: {output_file}", "info")
                self.individual_status.config(text="Success", fg=self.success_color)
                messagebox.showinfo("Success", message)
            else:
                self.add_individual_log(f"FAILED: {message}", "error")
                self.individual_status.config(text="Failed", fg=self.danger_color)
                messagebox.showerror("Failed", message)
                
        except Exception as e:
            error_msg = f"Error during retrieval: {str(e)}"
            self.add_individual_log(error_msg, "error")
            self.individual_status.config(text="Error", fg=self.danger_color)
            messagebox.showerror("Error", error_msg)
    
    def open_employee_editor(self):
        """Open employee data editor"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Individual retrieval modules not available")
            return
            
        if not self.excel_path.get():
            messagebox.showerror("Error", "Please select employee Excel file in Bulk Distribution tab first")
            return
        
        open_excel_editor(self.root, self.excel_path.get())
    
    def add_individual_log(self, message, log_type="info"):
        """Add message to individual log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": self.info_color,
            "success": self.success_color, 
            "error": self.danger_color,
            "warning": self.warning_color
        }
        
        icons = {
            "info": "",
            "success": "✓ ",
            "error": "✗ ",
            "warning": "! "
        }
        
        color = colors.get(log_type, "#374151")
        icon = icons.get(log_type, "")
        
        log_entry = f"[{timestamp}] {icon}{message}\n"
        
        self.individual_log_text.insert(tk.END, log_entry)
        self.individual_log_text.tag_add(log_type, f"end-2c linestart", f"end-1c")
        self.individual_log_text.tag_config(log_type, foreground=color)
        self.individual_log_text.see(tk.END)
        
        lines = self.individual_log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 200:
            self.individual_log_text.delete("1.0", "20.0")
    
    def clear_individual_log(self):
        """Clear individual log"""
        self.individual_log_text.delete("1.0", tk.END)
        self.add_individual_log("Individual log cleared", "info")
    
    def create_multi_pdf_ui(self):
        """Create multi-PDF aggregation UI section"""
        # Modern multi-PDF section
        multi_pdf_frame = tk.Frame(self.individual_frame, bg=self.card_color, relief=tk.FLAT, bd=0)
        multi_pdf_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Add border
        border_frame = tk.Frame(multi_pdf_frame, bg=self.border_color, relief=tk.FLAT, bd=1)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Section title with icon
        title_frame = tk.Frame(border_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(8, 5))
        
        tk.Label(
            title_frame,
            text="📚 Historical Payslips",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.text_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Multi-PDF aggregation for historical data",
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # Modern file selection controls
        file_controls = tk.Frame(border_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        file_controls.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        file_content = tk.Frame(file_controls, bg=self.hover_color)
        file_content.pack(fill=tk.X, padx=15, pady=6)
        
        tk.Button(
            file_content,
            text="➕ Add PDF Files",
            command=self.add_multi_pdf_files,
            font=('Segoe UI', 10, 'bold'),
            bg=self.info_color,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            file_content,
            text="✖️ Remove Selected",
            command=self.remove_selected_pdf,
            font=('Segoe UI', 10, 'bold'),
            bg=self.danger_color,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            file_content,
            text="🗑️ Clear All",
            command=self.clear_all_pdfs,
            font=('Segoe UI', 10, 'bold'),
            bg=self.text_secondary,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.LEFT)
        
        # Modern PDF list display
        list_frame = tk.Frame(border_frame, bg=self.card_color)
        list_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        # Create modern listbox with scrollbar
        list_container = tk.Frame(list_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        self.multi_pdf_listbox = tk.Listbox(
            list_container,
            font=('Segoe UI', 8),
            bg=self.card_color,
            fg=self.text_primary,
            selectmode=tk.SINGLE,
            height=4,
            relief=tk.FLAT,
            bd=0,
            selectbackground=self.primary_color,
            yscrollcommand=scrollbar.set
        )
        self.multi_pdf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.multi_pdf_listbox.yview)
        
        # Modern historical retrieval buttons
        historical_frame = tk.Frame(border_frame, bg=self.card_color)
        historical_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        # Primary action buttons
        primary_buttons = tk.Frame(historical_frame, bg=self.card_color)
        primary_buttons.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            primary_buttons,
            text="✓ Validate",
            command=self.validate_multi_pdfs,
            font=('Segoe UI', 9, 'bold'),
            bg=self.warning_color,
            fg='white',
            padx=12,
            pady=6,
            relief=tk.FLAT,
            bd=0,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            primary_buttons,
            text="📤 Retrieve",
            command=self.retrieve_historical_payslips_ui,
            font=('Segoe UI', 9, 'bold'),
            bg=self.success_color,
            fg='white',
            padx=12,
            pady=6,
            relief=tk.FLAT,
            bd=0,
            width=12
        ).pack(side=tk.LEFT)
        
        # Modern Multi-PDF status
        status_frame = tk.Frame(historical_frame, bg=self.hover_color, relief=tk.FLAT, bd=1)
        status_frame.pack(fill=tk.X)
        
        self.multi_pdf_status = tk.Label(
            status_frame,
            text="● Add PDF files to begin historical payslip retrieval",
            font=('Segoe UI', 10, 'bold'),
            bg=self.hover_color,
            fg=self.text_secondary
        )
        self.multi_pdf_status.pack(anchor=tk.W, padx=15, pady=6)
    
    def add_multi_pdf_files(self):
        """Add multiple PDF files for historical payslip retrieval"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Multi-PDF aggregation modules not available")
            return
            
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Payslip PDFs",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_paths:
            added_count = 0
            for file_path in file_paths:
                if file_path not in self.multi_pdf_paths:
                    self.multi_pdf_paths.append(file_path)
                    filename = os.path.basename(file_path)
                    self.multi_pdf_listbox.insert(tk.END, filename)
                    added_count += 1
            
            if added_count > 0:
                self.add_individual_log(f"Added {added_count} PDF files for historical retrieval", "success")
                self.update_multi_pdf_status()
            else:
                self.add_individual_log("All selected files already in list", "warning")
    
    def remove_selected_pdf(self):
        """Remove selected PDF from the list"""
        if not self.multi_pdf_listbox.curselection():
            messagebox.showwarning("Selection", "Please select a PDF file to remove")
            return
        
        selected_index = self.multi_pdf_listbox.curselection()[0]
        removed_file = self.multi_pdf_paths.pop(selected_index)
        self.multi_pdf_listbox.delete(selected_index)
        
        self.add_individual_log(f"Removed: {os.path.basename(removed_file)}", "info")
        self.update_multi_pdf_status()
    
    def clear_all_pdfs(self):
        """Clear all PDF files from the list"""
        if not self.multi_pdf_paths:
            return
            
        if messagebox.askyesno("Confirm", "Remove all PDF files from the list?"):
            count = len(self.multi_pdf_paths)
            self.multi_pdf_paths.clear()
            self.multi_pdf_listbox.delete(0, tk.END)
            
            self.add_individual_log(f"Cleared {count} PDF files", "info")
            self.update_multi_pdf_status()
    
    def validate_multi_pdfs(self):
        """Validate all PDF files in the list"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Multi-PDF aggregation modules not available")
            return
            
        if not self.multi_pdf_paths:
            messagebox.showwarning("No Files", "Please add PDF files first")
            return
        
        self.add_individual_log("Validating PDF files...", "info")
        
        valid_files, invalid_files = validate_pdf_files(self.multi_pdf_paths)
        
        if valid_files:
            self.add_individual_log(f"✓ {len(valid_files)} valid PDF files", "success")
            for file_path in valid_files:
                self.add_individual_log(f"  - {os.path.basename(file_path)}", "info")
        
        if invalid_files:
            self.add_individual_log(f"✗ {len(invalid_files)} invalid files", "error")
            for invalid in invalid_files:
                self.add_individual_log(f"  - {invalid}", "error")
        
        if not invalid_files:
            self.multi_pdf_status.config(text=f"All {len(valid_files)} PDF files are valid", fg=self.success_color)
            messagebox.showinfo("Validation Complete", f"All {len(valid_files)} PDF files are valid!")
        else:
            self.multi_pdf_status.config(text=f"{len(valid_files)} valid, {len(invalid_files)} invalid", fg=self.danger_color)
            messagebox.showwarning("Validation Issues", f"{len(valid_files)} valid, {len(invalid_files)} invalid files")
    
    def retrieve_historical_payslips_ui(self):
        """Handle historical payslip retrieval from UI"""
        if not INDIVIDUAL_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Multi-PDF aggregation modules not available")
            return
            
        matricule = self.individual_matricule.get().strip()
        email = self.individual_email.get().strip()
        
        if not matricule or not email:
            messagebox.showerror("Error", "Please enter both matricule and email")
            return
        
        if not self.multi_pdf_paths:
            messagebox.showerror("Error", "Please add PDF files for historical retrieval")
            return
        
        if not self.excel_path.get():
            messagebox.showerror("Error", "Please select employee Excel file in Bulk Distribution tab first")
            return
        
        # Validate PDFs first
        valid_files, invalid_files = validate_pdf_files(self.multi_pdf_paths)
        if invalid_files:
            messagebox.showerror("Invalid Files", f"Please fix {len(invalid_files)} invalid PDF files first")
            return
        
        try:
            self.multi_pdf_status.config(text="Processing historical payslips...", fg=self.warning_color)
            self.add_individual_log("Starting historical payslip retrieval...", "info")
            
            # Use the multi-PDF aggregation function
            success, message, output_file = retrieve_historical_payslips(
                matricule, email, valid_files, self.excel_path.get()
            )
            
            if success:
                self.add_individual_log(f"SUCCESS: {message}", "success")
                if output_file:
                    self.add_individual_log(f"Output file: {os.path.basename(output_file)}", "info")
                self.multi_pdf_status.config(text="Historical payslips retrieved successfully", fg=self.success_color)
                messagebox.showinfo("Success", message)
            else:
                self.add_individual_log(f"FAILED: {message}", "error")
                self.multi_pdf_status.config(text="Historical retrieval failed", fg=self.danger_color)
                messagebox.showerror("Failed", message)
                
        except Exception as e:
            error_msg = f"Error during historical retrieval: {str(e)}"
            self.add_individual_log(error_msg, "error")
            self.multi_pdf_status.config(text="Error occurred", fg=self.danger_color)
            messagebox.showerror("Error", error_msg)
    
    def update_multi_pdf_status(self):
        """Update the multi-PDF status display"""
        count = len(self.multi_pdf_paths)
        if count == 0:
            self.multi_pdf_status.config(text="Add PDF files to begin historical payslip retrieval", fg='#6b7280')
        elif count == 1:
            self.multi_pdf_status.config(text=f"1 PDF file ready for historical retrieval", fg=self.info_color)
        else:
            self.multi_pdf_status.config(text=f"{count} PDF files ready for historical retrieval", fg=self.info_color)
        
    def run(self):
        self.root.mainloop()

def main():
    app = FixedCompactUI()
    app.run()

if __name__ == "__main__":
    main()
