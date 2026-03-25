import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import pandas as pd
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FixedCompactUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Window configuration
        self.root.title("CRTV Payslip Distribution System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Center window
        self.center_window()
        
        # Colors
        self.bg_color = '#f0f4f8'
        self.card_color = 'white'
        self.primary_color = '#2563eb'
        self.success_color = '#16a34a'
        self.warning_color = '#ca8a04'
        self.danger_color = '#dc2626'
        self.info_color = '#0891b2'
        
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
        
        # Create UI
        self.create_main_layout()
        self.create_header()
        self.create_dashboard()
        self.create_file_section()
        self.create_control_section()
        self.create_log_section()
        
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
        
    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg=self.primary_color, height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="CRTV Automated Payslip Distribution System",
            font=('Segoe UI', 18, 'bold'),
            bg=self.primary_color,
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=15)
        
        self.status_label = tk.Label(
            header_frame,
            text="● Ready",
            font=('Segoe UI', 11, 'bold'),
            bg=self.primary_color,
            fg='#86efac'
        )
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=15)
        
    def create_dashboard(self):
        dashboard_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        dashboard_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            dashboard_frame,
            text="📊 Dashboard",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        cards_frame = tk.Frame(dashboard_frame, bg=self.card_color)
        cards_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.create_stat_card(cards_frame, "Employees", "0", self.info_color, 0)
        self.create_stat_card(cards_frame, "Processed", "0", self.warning_color, 1)
        self.create_stat_card(cards_frame, "Sent", "0", self.success_color, 2)
        self.create_stat_card(cards_frame, "Failed", "0", self.danger_color, 3)
        
    def create_stat_card(self, parent, title, value, color, column):
        card = tk.Frame(parent, bg=self.card_color, relief=tk.SOLID, bd=1, width=200)
        card.grid(row=0, column=column, padx=5, sticky="ew", pady=5)
        parent.grid_columnconfigure(column, weight=1)
        
        content_frame = tk.Frame(card, bg=self.card_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        title_label = tk.Label(
            content_frame, 
            text=title, 
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg='#6b7280'
        )
        title_label.pack(side=tk.LEFT)
        
        value_label = tk.Label(
            content_frame, 
            text=value, 
            font=('Segoe UI', 16, 'bold'),
            bg=self.card_color,
            fg=color
        )
        value_label.pack(side=tk.RIGHT)
        
        setattr(self, f"{title.lower()}_label", value_label)
        
    def create_file_section(self):
        file_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            file_frame,
            text="📁 File Management",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        file_controls = tk.Frame(file_frame, bg=self.card_color)
        file_controls.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # PDF Row
        pdf_row = tk.Frame(file_controls, bg=self.card_color)
        pdf_row.pack(fill=tk.X, pady=3)
        
        tk.Label(pdf_row, text="PDF:", font=('Segoe UI', 10, 'bold'), bg=self.card_color, width=8, anchor='w').pack(side=tk.LEFT)
        self.pdf_path_label = tk.Label(pdf_row, text=self.pdf_path.get(), bg=self.card_color, fg='#374151', font=('Segoe UI', 9))
        self.pdf_path_label.pack(side=tk.LEFT, padx=(5, 10))
        self.pdf_status = tk.Label(pdf_row, text="●", bg=self.card_color, fg=self.success_color, font=('Arial', 10))
        self.pdf_status.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(pdf_row, text="Browse", command=self.browse_pdf, font=('Segoe UI', 8), bg=self.info_color, fg='white', padx=8, pady=2).pack(side=tk.LEFT)
        
        # Excel Row
        excel_row = tk.Frame(file_controls, bg=self.card_color)
        excel_row.pack(fill=tk.X, pady=3)
        
        tk.Label(excel_row, text="Excel:", font=('Segoe UI', 10, 'bold'), bg=self.card_color, width=8, anchor='w').pack(side=tk.LEFT)
        self.excel_path_label = tk.Label(excel_row, text=self.excel_path.get(), bg=self.card_color, fg='#374151', font=('Segoe UI', 9))
        self.excel_path_label.pack(side=tk.LEFT, padx=(5, 10))
        self.excel_status = tk.Label(excel_row, text="●", bg=self.card_color, fg=self.success_color, font=('Arial', 10))
        self.excel_status.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(excel_row, text="Browse", command=self.browse_excel, font=('Segoe UI', 8), bg=self.info_color, fg='white', padx=8, pady=2).pack(side=tk.LEFT)
        
        self.file_info_label = tk.Label(file_frame, text="", font=('Segoe UI', 9), bg=self.card_color, fg='#374151')
        self.file_info_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
    def create_control_section(self):
        control_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            control_frame,
            text="⚙️ Control Panel",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Settings
        settings_frame = tk.Frame(control_frame, bg=self.card_color)
        settings_frame.pack(fill=tk.X, padx=15, pady=(0, 8))
        
        tk.Checkbutton(
            settings_frame,
            text="Simulation Mode",
            variable=self.simulation_mode,
            bg=self.card_color,
            font=('Segoe UI', 9),
            fg='#374151',
            selectcolor=self.card_color
        ).pack(side=tk.LEFT)
        
        tk.Button(
            settings_frame,
            text="Email Settings",
            command=self.show_email_config,
            font=('Segoe UI', 8),
            bg=self.info_color,
            fg='white',
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 8))
        
        # Buttons
        buttons_frame = tk.Frame(control_frame, bg=self.card_color)
        buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 8))
        
        self.validate_btn = tk.Button(
            buttons_frame,
            text="Validate",
            command=self.validate_files,
            font=('Segoe UI', 9, 'bold'),
            bg=self.warning_color,
            fg='white',
            width=12,
            height=1
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.process_btn = tk.Button(
            buttons_frame,
            text="Process",
            command=self.start_processing,
            font=('Segoe UI', 9, 'bold'),
            bg=self.success_color,
            fg='white',
            width=12,
            height=1
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.send_btn = tk.Button(
            buttons_frame,
            text="Send Payslips",
            command=self.send_payslips,
            font=('Segoe UI', 9, 'bold'),
            bg=self.primary_color,
            fg='white',
            width=12,
            height=1
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = tk.Button(
            buttons_frame,
            text="Stop",
            command=self.stop_processing,
            font=('Segoe UI', 9, 'bold'),
            bg=self.danger_color,
            fg='white',
            width=12,
            height=1,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status
        self.processing_status = tk.Label(
            control_frame,
            text="Ready",
            font=('Segoe UI', 9),
            bg=self.card_color,
            fg='#374151'
        )
        self.processing_status.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
    def create_log_section(self):
        log_frame = tk.Frame(self.main_frame, bg=self.card_color, relief=tk.RAISED, bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(log_frame, bg=self.card_color)
        title_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(
            title_frame,
            text="📋 Activity Log",
            font=('Segoe UI', 12, 'bold'),
            bg=self.card_color,
            fg=self.primary_color
        ).pack(side=tk.LEFT)
        
        tk.Button(
            title_frame,
            text="Clear",
            command=self.clear_log,
            font=('Segoe UI', 8),
            bg='#6b7280',
            fg='white',
            padx=6,
            pady=2
        ).pack(side=tk.RIGHT)
        
        log_container = tk.Frame(log_frame, bg=self.card_color)
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        self.log_text = tk.Text(
            log_container,
            height=8,
            wrap=tk.WORD,
            font=('Consolas', 8),
            bg='#f8f9fa',
            relief=tk.SOLID,
            bd=1
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
                    text=f"✓ {employee_count} employees, {page_count} PDF pages",
                    fg=self.success_color
                )
            except Exception as e:
                self.file_info_label.config(
                    text=f"✗ Error: {str(e)[:30]}...",
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
                    self.add_log(f"✓ Valid: {len(df)} employees", "success")
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
        self.status_label.config(text="● Processing", fg='#fbbf24')
        
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
        
    def send_payslips(self):
        """Dedicated function to send payslips - calls main script directly"""
        if not os.path.exists(self.pdf_path.get()) or not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Error", "Select valid files first")
            return
            
        # Confirm sending
        if not self.simulation_mode.get():
            result = messagebox.askyesno(
                "Confirm Sending",
                "This will send REAL emails to all employees.\n\nAre you sure you want to continue?"
            )
            if not result:
                return
        
        self.processing = True
        self.process_btn.config(state='disabled')
        self.send_btn.config(state='disabled')
        self.validate_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_var.set(0)
        
        # Update main module settings
        import main
        main.SIMULATION_MODE = self.simulation_mode.get()
        main.INPUT_PDF = self.pdf_path.get()
        main.INPUT_EXCEL = self.excel_path.get()
        
        mode_text = "REAL EMAILS" if not self.simulation_mode.get() else "SIMULATION"
        self.add_log(f"📧 SENDING PAYSLLIPS - {mode_text}", "info")
        self.status_label.config(text="● Sending", fg=self.primary_color)
        
        # Run main script in thread
        thread = threading.Thread(target=self.run_main_script)
        thread.daemon = True
        thread.start()
        
    def run_main_script(self):
        """Run the actual main payslip script"""
        try:
            self.processing_status.config(text="Running main script...")
            self.progress_var.set(20)
            
            # Import and run main function
            import main
            main.main()
            
            self.progress_var.set(100)
            self.processing_status.config(text="Completed!")
            
            if self.simulation_mode.get():
                self.add_log("✓ Simulation completed - no real emails sent", "success")
            else:
                self.add_log("✓ Payslips sent successfully!", "success")
                
            self.status_label.config(text="● Complete", fg=self.success_color)
            
            messagebox.showinfo(
                "Complete",
                f"Payslip processing completed!\n\nMode: {'Simulation' if self.simulation_mode.get() else 'Real Emails'}\nCheck output folder for generated payslips."
            )
            
        except Exception as e:
            self.add_log(f"Script error: {e}", "error")
            messagebox.showerror("Error", f"Script failed: {e}")
            self.status_label.config(text="● Error", fg=self.danger_color)
            
        finally:
            self.processing = False
            self.process_btn.config(state='normal')
            self.send_btn.config(state='normal')
            self.validate_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
        
    def process_thread(self):
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
                    
                    self.add_log(f"✓ {name}", "success")
                    self.stats['processed'] = processed
                    self.stats['sent'] = sent
                    self.update_stats_display()
                    
                except Exception as e:
                    failed += 1
                    self.stats['failed'] = failed
                    self.add_log(f"✗ {row.get('Name', '?')}: {e}", "error")
                    self.update_stats_display()
                    
            if self.processing:
                self.progress_var.set(100)
                self.processing_status.config(text="Done!")
                self.add_log(f"Complete: {processed} processed, {sent} sent, {failed} failed", "success")
                self.status_label.config(text="● Complete", fg=self.success_color)
                
                messagebox.showinfo(
                    "Complete",
                    f"Processing done!\n\nTotal: {total}\nProcessed: {processed}\nSent: {sent}\nFailed: {failed}"
                )
            
        except Exception as e:
            self.add_log(f"Error: {e}", "error")
            messagebox.showerror("Error", f"Processing failed: {e}")
            self.status_label.config(text="● Error", fg=self.danger_color)
            
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
        
    def run(self):
        self.root.mainloop()

def main():
    app = FixedCompactUI()
    app.run()

if __name__ == "__main__":
    main()
