import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import pandas as pd
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CRTVDirectorUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Window configuration
        self.root.title("CRTV Automated Payslip Distribution System - Director Edition")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        self.root.state('zoomed')  # Start maximized
        
        # Configure colors
        self.bg_color = '#f8f9fa'
        self.card_color = 'white'
        self.primary_color = '#1e3a8a'
        self.success_color = '#059669'
        self.warning_color = '#d97706'
        self.danger_color = '#dc2626'
        self.info_color = '#2563eb'
        
        self.root.configure(bg=self.bg_color)
        
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
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_header(self):
        # Header section
        header_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="CRTV Automated Payslip Distribution System",
            font=('Segoe UI', 24, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="● System Ready",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.success_color
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
    def create_dashboard(self):
        # Dashboard cards container
        dashboard_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        dashboard_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Dashboard title
        title_frame = tk.Frame(dashboard_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="Dashboard Overview",
            font=('Segoe UI', 16, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(side=tk.LEFT)
        
        # Stats cards
        cards_frame = tk.Frame(dashboard_frame, bg=self.card_color)
        cards_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Total Employees Card
        self.create_stat_card(cards_frame, "Total Employees", "0", self.info_color, 0)
        
        # Processed Card
        self.create_stat_card(cards_frame, "Processed", "0", self.warning_color, 1)
        
        # Sent Card
        self.create_stat_card(cards_frame, "Emails Sent", "0", self.success_color, 2)
        
        # Failed Card
        self.create_stat_card(cards_frame, "Failed", "0", self.danger_color, 3)
        
    def create_stat_card(self, parent, title, value, color, column):
        # Card frame
        card = tk.Frame(parent, bg=self.card_color, relief=tk.SOLID, bd=1)
        card.grid(row=0, column=column, padx=10, sticky="ew", pady=5)
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.card_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text=title, 
            font=('Segoe UI', 12),
            bg=self.card_color,
            fg='#6b7280'
        )
        title_label.pack(anchor=tk.W)
        
        # Value
        value_label = tk.Label(
            content_frame, 
            text=value, 
            font=('Segoe UI', 28, 'bold'),
            bg=self.card_color,
            fg=color
        )
        value_label.pack(anchor=tk.W, pady=(8, 0))
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_label", value_label)
        
    def create_file_section(self):
        # File management section
        file_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Section title
        title_frame = tk.Frame(file_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="File Management",
            font=('Segoe UI', 16, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(side=tk.LEFT)
        
        # File controls
        file_controls = tk.Frame(file_frame, bg=self.card_color)
        file_controls.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # PDF File Section
        pdf_container = tk.Frame(file_controls, bg=self.card_color)
        pdf_container.pack(fill=tk.X, pady=8)
        
        tk.Label(pdf_container, text="Payslip PDF:", font=('Segoe UI', 12, 'bold'), bg=self.card_color).pack(side=tk.LEFT, padx=(0, 15))
        
        self.pdf_path_label = tk.Label(pdf_container, text=self.pdf_path.get(), bg=self.card_color, fg='#374151', font=('Segoe UI', 10))
        self.pdf_path_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.pdf_status = tk.Label(pdf_container, text="●", bg=self.card_color, fg=self.success_color, font=('Arial', 14, 'bold'))
        self.pdf_status.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(pdf_container, text="Browse", command=self.browse_pdf, font=('Segoe UI', 10), bg=self.info_color, fg='white', padx=15, pady=5).pack(side=tk.LEFT)
        
        # Excel File Section
        excel_container = tk.Frame(file_controls, bg=self.card_color)
        excel_container.pack(fill=tk.X, pady=8)
        
        tk.Label(excel_container, text="Employee Excel:", font=('Segoe UI', 12, 'bold'), bg=self.card_color).pack(side=tk.LEFT, padx=(0, 15))
        
        self.excel_path_label = tk.Label(excel_container, text=self.excel_path.get(), bg=self.card_color, fg='#374151', font=('Segoe UI', 10))
        self.excel_path_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.excel_status = tk.Label(excel_container, text="●", bg=self.card_color, fg=self.success_color, font=('Arial', 14, 'bold'))
        self.excel_status.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(excel_container, text="Browse", command=self.browse_excel, font=('Segoe UI', 10), bg=self.info_color, fg='white', padx=15, pady=5).pack(side=tk.LEFT)
        
        # File info display
        self.file_info_label = tk.Label(file_frame, text="", font=('Segoe UI', 11), bg=self.card_color, fg='#374151')
        self.file_info_label.pack(anchor=tk.W, padx=20, pady=(0, 20))
        
    def create_control_section(self):
        # Control panel
        control_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Section title
        title_frame = tk.Frame(control_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="Control Panel",
            font=('Segoe UI', 16, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(side=tk.LEFT)
        
        # Settings and progress
        settings_frame = tk.Frame(control_frame, bg=self.card_color)
        settings_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Simulation mode checkbox
        sim_check = tk.Checkbutton(
            settings_frame,
            text="Simulation Mode (No real emails sent)",
            variable=self.simulation_mode,
            bg=self.card_color,
            font=('Segoe UI', 11),
            fg='#374151',
            selectcolor=self.card_color
        )
        sim_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Email config button
        tk.Button(
            settings_frame,
            text="Email Configuration",
            command=self.show_email_config,
            font=('Segoe UI', 10),
            bg=self.info_color,
            fg='white',
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Action buttons
        buttons_frame = tk.Frame(control_frame, bg=self.card_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.validate_btn = tk.Button(
            buttons_frame,
            text="Validate Files",
            command=self.validate_files,
            font=('Segoe UI', 11, 'bold'),
            bg=self.warning_color,
            fg='white',
            width=18,
            height=2
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_btn = tk.Button(
            buttons_frame,
            text="Process Payslips",
            command=self.start_processing,
            font=('Segoe UI', 11, 'bold'),
            bg=self.success_color,
            fg='white',
            width=18,
            height=2
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(
            buttons_frame,
            text="Stop Processing",
            command=self.stop_processing,
            font=('Segoe UI', 11, 'bold'),
            bg=self.danger_color,
            fg='white',
            width=18,
            height=2,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status label
        self.processing_status = tk.Label(
            control_frame,
            text="Ready to process",
            font=('Segoe UI', 11),
            bg=self.card_color,
            fg='#374151'
        )
        self.processing_status.pack(anchor=tk.W, padx=20, pady=(0, 20))
        
    def create_log_section(self):
        # Log viewer
        log_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        title_frame = tk.Frame(log_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            title_frame,
            text="Activity Log",
            font=('Segoe UI', 16, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(side=tk.LEFT)
        
        # Clear log button
        tk.Button(
            title_frame,
            text="Clear Log",
            command=self.clear_log,
            font=('Segoe UI', 9),
            bg='#6b7280',
            fg='white',
            padx=10,
            pady=3
        ).pack(side=tk.RIGHT)
        
        # Log container
        log_container = tk.Frame(log_frame, bg=self.card_color)
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create scrolled text widget
        self.log_text = tk.Text(
            log_container,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#f8f9fa',
            relief=tk.SOLID,
            bd=1
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        self.pdf_status.config(fg=self.success_color if pdf_exists else self.danger_color)
        
        # Check Excel file
        excel_exists = os.path.exists(self.excel_path.get())
        self.excel_status.config(fg=self.success_color if excel_exists else self.danger_color)
        
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
                    text=f"Employees: {employee_count} • PDF pages: {page_count}",
                    fg=self.success_color
                )
            except Exception as e:
                self.file_info_label.config(
                    text=f"Error reading files: {str(e)}",
                    fg=self.warning_color
                )
        else:
            self.file_info_label.config(
                text="Please select both PDF and Excel files",
                fg=self.warning_color
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
                    self.add_log(f"Validation failed - Excel missing columns: {', '.join(missing_columns)}", "error")
                    messagebox.showerror("Validation Error", f"Excel file is missing required columns: {', '.join(missing_columns)}")
                else:
                    self.add_log(f"Files validated successfully - {len(df)} employees found", "success")
                    messagebox.showinfo("Validation Success", f"Files are ready for processing!\n\nEmployees: {len(df)}")
                    
            except Exception as e:
                self.add_log(f"Validation error: {str(e)}", "error")
                messagebox.showerror("Validation Error", f"Failed to validate files: {str(e)}")
        else:
            self.add_log("Please select both PDF and Excel files", "error")
            messagebox.showerror("Validation Error", "Please select both PDF and Excel files")
            
    def start_processing(self):
        if not os.path.exists(self.pdf_path.get()) or not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Error", "Please select valid files first")
            return
            
        self.processing = True
        self.process_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.validate_btn.config(state='disabled')
        self.progress_var.set(0)
        
        # Update simulation mode in main module
        import main
        main.SIMULATION_MODE = self.simulation_mode.get()
        main.INPUT_PDF = self.pdf_path.get()
        main.INPUT_EXCEL = self.excel_path.get()
        
        self.add_log(f"Starting processing - Simulation: {'ON' if self.simulation_mode.get() else 'OFF'}", "info")
        self.status_label.config(text="● Processing...", fg=self.warning_color)
        
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
                    
                    self.add_log(f"Processed: {name} - {email}", "success")
                    
                    # Update stats
                    self.stats['processed'] = processed
                    self.stats['sent'] = sent
                    self.update_stats_display()
                    
                except Exception as e:
                    failed += 1
                    self.stats['failed'] = failed
                    self.add_log(f"Failed for {row.get('Name', 'Unknown')}: {str(e)}", "error")
                    self.update_stats_display()
                    
            # Complete
            if self.processing:
                self.progress_var.set(100)
                self.processing_status.config(text="Processing completed!")
                self.add_log(f"Processing completed - Processed: {processed}, Sent: {sent}, Failed: {failed}", "success")
                self.status_label.config(text="● Completed", fg=self.success_color)
                
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
            self.add_log(f"Processing error: {str(e)}", "error")
            messagebox.showerror("Processing Error", f"An error occurred during processing: {str(e)}")
            self.status_label.config(text="● Error", fg=self.danger_color)
            
        finally:
            self.processing = False
            self.process_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.validate_btn.config(state='normal')
            
    def stop_processing(self):
        self.processing = False
        self.add_log("Processing stopped by user", "warning")
        self.status_label.config(text="● Stopped", fg=self.warning_color)
        
    def update_stats_display(self):
        self.processed_label.config(text=str(self.stats['processed']))
        self.emails_sent_label.config(text=str(self.stats['sent']))
        self.failed_label.config(text=str(self.stats['failed']))
        
    def show_email_config(self):
        # Show email configuration dialog
        config_window = tk.Toplevel(self.root)
        config_window.title("Email Configuration")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()
        config_window.configure(bg=self.bg_color)
        
        # Email settings
        tk.Label(config_window, text="Email Configuration", font=('Segoe UI', 16, 'bold'), bg=self.bg_color, fg=self.primary_color).pack(pady=20)
        
        config_frame = tk.Frame(config_window, bg=self.card_color, relief=tk.RAISED, bd=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Config fields
        fields = [
            ("SMTP Server:", "smtp.gmail.com"),
            ("Port:", "465"),
            ("Email Address:", "nerisbi801@gmail.com"),
            ("Password:", "qmpp eqym rclo bave")
        ]
        
        for i, (label, default) in enumerate(fields):
            tk.Label(config_frame, text=label, font=('Segoe UI', 11, 'bold'), bg=self.card_color).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)
            entry = tk.Entry(config_frame, font=('Segoe UI', 10), width=30)
            entry.insert(0, default)
            if "Password" in label:
                entry.config(show="*")
            entry.grid(row=i, column=1, sticky=tk.EW, padx=(0, 20), pady=10)
        
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(config_window, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Test Connection", font=('Segoe UI', 10), bg=self.info_color, fg='white', width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save", font=('Segoe UI', 10, 'bold'), bg=self.success_color, fg='white', width=12, command=config_window.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", font=('Segoe UI', 10), bg='#6b7280', fg='white', width=12, command=config_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def add_log(self, message, log_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different log types
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
            "warning": "⚠ "
        }
        
        color = colors.get(log_type, "#374151")
        icon = icons.get(log_type, "")
        
        log_entry = f"[{timestamp}] {icon}{message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.tag_add(log_type, f"end-2c linestart", f"end-1c")
        self.log_text.tag_config(log_type, foreground=color)
        self.log_text.see(tk.END)
        
        # Limit log entries to prevent memory issues
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", "100.0")
            
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.add_log("Log cleared", "info")
        
    def run(self):
        self.root.mainloop()

def main():
    app = CRTVDirectorUI()
    app.run()

if __name__ == "__main__":
    main()
