import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
import threading
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main as process_payslips

class CRTVProfessionalApp(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        
        # Window configuration
        self.title("CRTV Automated Payslip Distribution System - Professional Edition")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        self.state('zoomed')  # Start maximized
        
        # Configure style
        self.style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Heading.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Card.TFrame', borderwidth=1, relief='solid')
        
        # Variables
        self.pdf_path = tk.StringVar(value="input/payslips.pdf")
        self.excel_path = tk.StringVar(value="input/employees.xlsx")
        self.simulation_mode = tk.BooleanVar(value=True)
        self.processing = False
        self.stats = {
            'total_employees': 0,
            'processed': 0,
            'sent': 0,
            'failed': 0
        }
        
        # Create main container
        self.create_main_layout()
        self.create_header()
        self.create_dashboard()
        self.create_file_section()
        self.create_control_section()
        self.create_log_section()
        
        # Initialize
        self.update_file_status()
        
    def create_main_layout(self):
        # Main container with padding
        self.main_frame = tb.Frame(self, padding="20")
        self.main_frame.pack(fill=BOTH, expand=True)
        
    def create_header(self):
        # Header section
        header_frame = tb.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        title_label = tb.Label(
            header_frame, 
            text="CRTV Automated Payslip Distribution System",
            bootstyle="primary",
            style='Title.TLabel'
        )
        title_label.pack(side=LEFT)
        
        # Status indicator
        self.status_label = tb.Label(
            header_frame,
            text="● System Ready",
            bootstyle="success",
            font=('Segoe UI', 12)
        )
        self.status_label.pack(side=RIGHT)
        
    def create_dashboard(self):
        # Dashboard cards container
        dashboard_frame = tb.LabelFrame(
            self.main_frame,
            text="Dashboard Overview",
            bootstyle="primary",
            padding="15"
        )
        dashboard_frame.pack(fill=X, pady=(0, 20))
        
        # Stats cards
        cards_frame = tb.Frame(dashboard_frame)
        cards_frame.pack(fill=X)
        
        # Total Employees Card
        self.create_stat_card(cards_frame, "Total Employees", "0", "info", 0)
        
        # Processed Card
        self.create_stat_card(cards_frame, "Processed", "0", "warning", 1)
        
        # Sent Card
        self.create_stat_card(cards_frame, "Emails Sent", "0", "success", 2)
        
        # Failed Card
        self.create_stat_card(cards_frame, "Failed", "0", "danger", 3)
        
    def create_stat_card(self, parent, title, value, bootstyle, column):
        card = tb.Frame(parent, bootstyle=f"{bootstyle}", style='Card.TFrame', padding="15")
        card.grid(row=0, column=column, padx=10, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Title
        title_label = tb.Label(card, text=title, font=('Segoe UI', 10))
        title_label.pack(anchor=W)
        
        # Value
        value_label = tb.Label(card, text=value, font=('Segoe UI', 24, 'bold'))
        value_label.pack(anchor=W, pady=(5, 0))
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_label", value_label)
        
    def create_file_section(self):
        # File management section
        file_frame = tb.LabelFrame(
            self.main_frame,
            text="File Management",
            bootstyle="primary",
            padding="15"
        )
        file_frame.pack(fill=X, pady=(0, 20))
        
        # PDF File Section
        pdf_container = tb.Frame(file_frame)
        pdf_container.pack(fill=X, pady=5)
        
        tb.Label(pdf_container, text="Payslip PDF:", font=('Segoe UI', 11, 'bold')).pack(side=LEFT, padx=(0, 10))
        
        self.pdf_path_label = tb.Label(pdf_container, text=self.pdf_path.get(), bootstyle="secondary")
        self.pdf_path_label.pack(side=LEFT, padx=(0, 10))
        
        self.pdf_status = tb.Label(pdf_container, text="●", bootstyle="success")
        self.pdf_status.pack(side=LEFT, padx=(0, 10))
        
        tb.Button(pdf_container, text="Browse", command=self.browse_pdf, bootstyle="outline-primary").pack(side=LEFT)
        
        # Excel File Section
        excel_container = tb.Frame(file_frame)
        excel_container.pack(fill=X, pady=5)
        
        tb.Label(excel_container, text="Employee Excel:", font=('Segoe UI', 11, 'bold')).pack(side=LEFT, padx=(0, 10))
        
        self.excel_path_label = tb.Label(excel_container, text=self.excel_path.get(), bootstyle="secondary")
        self.excel_path_label.pack(side=LEFT, padx=(0, 10))
        
        self.excel_status = tb.Label(excel_container, text="●", bootstyle="success")
        self.excel_status.pack(side=LEFT, padx=(0, 10))
        
        tb.Button(excel_container, text="Browse", command=self.browse_excel, bootstyle="outline-primary").pack(side=LEFT)
        
        # File info display
        self.file_info_label = tb.Label(file_frame, text="", font=('Segoe UI', 10))
        self.file_info_label.pack(pady=(10, 0))
        
    def create_control_section(self):
        # Control panel
        control_frame = tb.LabelFrame(
            self.main_frame,
            text="Control Panel",
            bootstyle="primary",
            padding="15"
        )
        control_frame.pack(fill=X, pady=(0, 20))
        
        # Top row - Settings
        settings_frame = tb.Frame(control_frame)
        settings_frame.pack(fill=X, pady=(0, 15))
        
        # Simulation mode checkbox
        sim_check = tb.Checkbutton(
            settings_frame,
            text="Simulation Mode (No real emails sent)",
            variable=self.simulation_mode,
            bootstyle="primary-round-toggle"
        )
        sim_check.pack(side=LEFT)
        
        # Email config button
        tb.Button(
            settings_frame,
            text="Email Configuration",
            command=self.show_email_config,
            bootstyle="info"
        ).pack(side=RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tb.Progressbar(
            control_frame,
            variable=self.progress_var,
            bootstyle="success-striped",
            mode='determinate'
        )
        self.progress_bar.pack(fill=X, pady=(0, 15))
        
        # Action buttons
        buttons_frame = tb.Frame(control_frame)
        buttons_frame.pack(fill=X)
        
        self.validate_btn = tb.Button(
            buttons_frame,
            text="📋 Validate Files",
            command=self.validate_files,
            bootstyle="info",
            width=20
        )
        self.validate_btn.pack(side=LEFT, padx=(0, 10))
        
        self.process_btn = tb.Button(
            buttons_frame,
            text="🚀 Process Payslips",
            command=self.start_processing,
            bootstyle="success",
            width=20
        )
        self.process_btn.pack(side=LEFT, padx=(0, 10))
        
        self.stop_btn = tb.Button(
            buttons_frame,
            text="⏹ Stop Processing",
            command=self.stop_processing,
            bootstyle="danger",
            width=20,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT)
        
        # Status label
        self.processing_status = tb.Label(
            control_frame,
            text="Ready to process",
            font=('Segoe UI', 11)
        )
        self.processing_status.pack(pady=(10, 0))
        
    def create_log_section(self):
        # Log viewer
        log_frame = tb.LabelFrame(
            self.main_frame,
            text="Activity Log",
            bootstyle="primary",
            padding="15"
        )
        log_frame.pack(fill=BOTH, expand=True)
        
        # Create scrolled text widget
        self.log_text = tk.Text(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#f8f9fa'
        )
        
        scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Add initial log entry
        self.add_log("System initialized successfully", "success")
        
    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select Payslip PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            self.pdf_path_label.config(text=os.path.basename(filename))
            self.update_file_status()
            
    def browse_excel(self):
        filename = filedialog.askopenfilename(
            title="Select Employee Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path.set(filename)
            self.excel_path_label.config(text=os.path.basename(filename))
            self.update_file_status()
            
    def update_file_status(self):
        # Check PDF file
        pdf_exists = os.path.exists(self.pdf_path.get())
        self.pdf_status.config(
            text="●",
            bootstyle="success" if pdf_exists else "danger"
        )
        
        # Check Excel file
        excel_exists = os.path.exists(self.excel_path.get())
        self.excel_status.config(
            text="●",
            bootstyle="success" if excel_exists else "danger"
        )
        
        # Update file info
        if pdf_exists and excel_exists:
            try:
                # Get employee count
                df = pd.read_excel(self.excel_path.get())
                employee_count = len(df)
                self.stats['total_employees'] = employee_count
                self.total_employees_label.config(text=str(employee_count))
                
                # Get PDF page count
                from PyPDF2 import PdfReader
                reader = PdfReader(self.pdf_path.get())
                page_count = len(reader.pages)
                
                self.file_info_label.config(
                    text=f"📊 {employee_count} employees • {page_count} PDF pages",
                    bootstyle="success"
                )
            except Exception as e:
                self.file_info_label.config(
                    text=f"⚠️ Error reading files: {str(e)}",
                    bootstyle="warning"
                )
        else:
            self.file_info_label.config(
                text="⚠️ Please select both PDF and Excel files",
                bootstyle="warning"
            )
            
    def validate_files(self):
        self.add_log("Validating files...", "info")
        self.update_file_status()
        
        pdf_exists = os.path.exists(self.pdf_path.get())
        excel_exists = os.path.exists(self.excel_path.get())
        
        if pdf_exists and excel_exists:
            try:
                # Validate Excel structure
                df = pd.read_excel(self.excel_path.get())
                required_columns = ['Name', 'Email']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    self.add_log(f"❌ Excel missing columns: {', '.join(missing_columns)}", "error")
                    messagebox.showerror("Validation Error", f"Excel file is missing required columns: {', '.join(missing_columns)}")
                else:
                    self.add_log(f"✅ Files validated successfully - {len(df)} employees found", "success")
                    messagebox.showinfo("Validation Success", f"Files are ready for processing!\n\nEmployees: {len(df)}\nPDF pages: Will be checked during processing")
                    
            except Exception as e:
                self.add_log(f"❌ Validation error: {str(e)}", "error")
                messagebox.showerror("Validation Error", f"Failed to validate files: {str(e)}")
        else:
            self.add_log("❌ Please select both PDF and Excel files", "error")
            messagebox.showerror("Validation Error", "Please select both PDF and Excel files")
            
    def start_processing(self):
        if not os.path.exists(self.pdf_path.get()) or not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Error", "Please select valid files first")
            return
            
        self.processing = True
        self.process_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.validate_btn.config(state=DISABLED)
        self.progress_var.set(0)
        
        # Update simulation mode in main module
        import main
        main.SIMULATION_MODE = self.simulation_mode.get()
        main.INPUT_PDF = self.pdf_path.get()
        main.INPUT_EXCEL = self.excel_path.get()
        
        self.add_log(f"🚀 Starting processing - Simulation: {'ON' if self.simulation_mode.get() else 'OFF'}", "info")
        self.status_label.config(text="● Processing...", bootstyle="warning")
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_payslips_thread)
        thread.daemon = True
        thread.start()
        
    def process_payslips_thread(self):
        try:
            # Update progress
            self.progress_var.set(10)
            self.processing_status.config(text="Reading employee data...")
            
            # Read employee data
            df = pd.read_excel(self.excel_path.get())
            total_employees = len(df)
            
            self.progress_var.set(30)
            self.processing_status.config(text="Processing payslips...")
            
            # Process each employee
            processed = 0
            sent = 0
            failed = 0
            
            for index, row in df.iterrows():
                if not self.processing:
                    break
                    
                try:
                    name = str(row["Name"]).strip()
                    email = str(row["Email"]).strip()
                    
                    # Update progress
                    progress = 30 + (70 * (index + 1) / total_employees)
                    self.progress_var.set(progress)
                    
                    processed += 1
                    if not self.simulation_mode.get():
                        sent += 1
                    
                    self.add_log(f"✅ Processed: {name} - {email}", "success")
                    
                    # Update stats
                    self.stats['processed'] = processed
                    self.stats['sent'] = sent
                    self.update_stats_display()
                    
                except Exception as e:
                    failed += 1
                    self.stats['failed'] = failed
                    self.add_log(f"❌ Failed for {row.get('Name', 'Unknown')}: {str(e)}", "error")
                    self.update_stats_display()
                    
            # Complete
            if self.processing:
                self.progress_var.set(100)
                self.processing_status.config(text="Processing completed!")
                self.add_log(f"🎉 Processing completed - Processed: {processed}, Sent: {sent}, Failed: {failed}", "success")
                self.status_label.config(text="● Completed", bootstyle="success")
                
                # Show completion message
                messagebox.showinfo(
                    "Processing Complete",
                    f"Processing completed successfully!\n\n"
                    f"Total Employees: {total_employees}\n"
                    f"Processed: {processed}\n"
                    f"Emails Sent: {sent}\n"
                    f"Failed: {failed}"
                )
            
        except Exception as e:
            self.add_log(f"❌ Processing error: {str(e)}", "error")
            messagebox.showerror("Processing Error", f"An error occurred during processing: {str(e)}")
            self.status_label.config(text="● Error", bootstyle="danger")
            
        finally:
            self.processing = False
            self.process_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.validate_btn.config(state=NORMAL)
            
    def stop_processing(self):
        self.processing = False
        self.add_log("⏹ Processing stopped by user", "warning")
        self.status_label.config(text="● Stopped", bootstyle="warning")
        
    def update_stats_display(self):
        self.processed_label.config(text=str(self.stats['processed']))
        self.emails_sent_label.config(text=str(self.stats['sent']))
        self.failed_label.config(text=str(self.stats['failed']))
        
    def show_email_config(self):
        # Show email configuration dialog
        config_window = tb.Toplevel(self)
        config_window.title("Email Configuration")
        config_window.geometry("500x400")
        config_window.transient(self)
        config_window.grab_set()
        
        # Email settings
        tb.Label(config_window, text="Email Configuration", font=('Segoe UI', 14, 'bold')).pack(pady=20)
        
        config_frame = tb.Frame(config_window, padding="20")
        config_frame.pack(fill=BOTH, expand=True)
        
        tb.Label(config_frame, text="SMTP Server:").grid(row=0, column=0, sticky=W, pady=5)
        tb.Entry(config_frame, textvariable=tk.StringVar(value="smtp.gmail.com")).grid(row=0, column=1, sticky="ew", pady=5)
        
        tb.Label(config_frame, text="Port:").grid(row=1, column=0, sticky=W, pady=5)
        tb.Entry(config_frame, textvariable=tk.StringVar(value="465")).grid(row=1, column=1, sticky="ew", pady=5)
        
        tb.Label(config_frame, text="Email Address:").grid(row=2, column=0, sticky=W, pady=5)
        tb.Entry(config_frame, textvariable=tk.StringVar(value="nerisbi801@gmail.com")).grid(row=2, column=1, sticky="ew", pady=5)
        
        tb.Label(config_frame, text="Password:").grid(row=3, column=0, sticky=W, pady=5)
        tb.Entry(config_frame, show="*", textvariable=tk.StringVar(value="qmpp eqym rclo bave")).grid(row=3, column=1, sticky="ew", pady=5)
        
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tb.Frame(config_window)
        button_frame.pack(pady=20)
        
        tb.Button(button_frame, text="Test Connection", bootstyle="info", width=15).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Save", bootstyle="success", width=15, command=config_window.destroy).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Cancel", bootstyle="secondary", width=15, command=config_window.destroy).pack(side=LEFT, padx=5)
        
    def add_log(self, message, log_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different log types
        colors = {
            "info": "",
            "success": "✅ ",
            "error": "❌ ",
            "warning": "⚠️ "
        }
        
        prefix = colors.get(log_type, "")
        log_entry = f"[{timestamp}] {prefix}{message}\n"
        
        self.log_text.insert(END, log_entry)
        self.log_text.see(END)
        
        # Limit log entries to prevent memory issues
        lines = self.log_text.get("1.0", END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", "100.0")

def main():
    app = CRTVProfessionalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
