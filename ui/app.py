from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
from datetime import datetime
import threading
from services.payslip_service import PayslipService


class CRTVPayslipApp(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")

        self.title("CRTV Automated Payslip Distribution System")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.minsize(1000, 600)
        
        # Variables for file paths
        self.payslip_folder_path = tk.StringVar()
        self.employee_path = tk.StringVar()
        self.stamp_path = tk.StringVar()
        
        # Set default paths
        self.payslip_folder_path.set("input/payslips/")
        self.employee_path.set("input/employees - 1.xlsx")
        self.stamp_path.set("input/Stamp.png")
        
        # Initialize backend service
        self.service = PayslipService()
        self.service.set_progress_callback(self.on_service_progress)
        
        # Processing state
        self.is_processing = False

        # =====================
        # Load icons with error handling
        # =====================
        self.icons = {}
        icon_files = {
            "dashboard": "assets/dashboard.jpg",
            "upload": "assets/upload.jpg",
            "send": "assets/send.jpg",
            "logs": "assets/logs.jpg",
            "exit": "assets/exit.jpg"
        }
        
        for key, path in icon_files.items():
            try:
                if os.path.exists(path):
                    self.icons[key] = ImageTk.PhotoImage(
                        Image.open(path).resize((20, 20))
                    )
                else:
                    self.icons[key] = None
            except Exception as e:
                print(f"Warning: Could not load icon {key}: {e}")
                self.icons[key] = None

        # =====================
        # Layout
        # =====================
        self.sidebar = tb.Frame(self, width=230, bootstyle="dark")
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = tb.Frame(self, bootstyle="light")
        self.content.pack(side=RIGHT, expand=True, fill=BOTH)

        self.build_sidebar()
        self.show_dashboard()
        
        # Status bar
        self.status_bar = tb.Label(
            self,
            text="Ready",
            bootstyle="secondary",
            relief=tk.SUNKEN,
            anchor=W
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # =====================
    # Sidebar
    # =====================
    def build_sidebar(self):
        tb.Label(
            self.sidebar,
            text="CRTV",
            font=("Segoe UI", 22, "bold"),
            bootstyle="inverse-dark"
        ).pack(pady=30)

        buttons = [
            ("Dashboard", "dashboard", self.show_dashboard),
            ("Upload PDF", "upload", self.show_upload),
            ("Send Payslips", "send", self.show_send),
            ("Logs", "logs", self.show_logs),
            ("Exit", "exit", self.quit),
        ]

        for text, icon, command in buttons:
            btn_frame = tb.Frame(self.sidebar)
            btn_frame.pack(pady=6, padx=10, fill=X)
            
            btn_args = {
                "text": text,
                "bootstyle": "light-outline",
                "command": command,
                "width": 18
            }
            if self.icons.get(icon):
                btn_args["image"] = self.icons[icon]
                btn_args["compound"] = LEFT
            
            tb.Button(
                btn_frame,
                **btn_args
            ).pack(fill=X)

    # =====================
    # Content handlers
    # =====================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        
        # Main container
        main_frame = tb.Frame(self.content)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tb.Label(
            main_frame,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            bootstyle="dark"
        ).pack(pady=(0, 30))
        
        # Stats cards container
        cards_frame = tb.Frame(main_frame)
        cards_frame.pack(fill=BOTH, expand=True)
        
        # Create stats cards
        self.create_stats_cards(cards_frame)
        
        # Load initial stats
        self.refresh_stats()
        
        # Quick actions
        actions_frame = tb.LabelFrame(main_frame, text="Quick Actions")
        actions_frame.pack(fill=X, pady=(30, 20), padx=20)
        
        actions_row = tb.Frame(actions_frame)
        actions_row.pack(fill=X, padx=15, pady=15)
        
        tb.Button(
            actions_row,
            text="📤 Upload New Payslip",
            bootstyle="success",
            command=self.show_upload,
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            actions_row,
            text="📧 Send All Payslips",
            bootstyle="info",
            command=self.show_send,
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            actions_row,
            text="📋 View Logs",
            bootstyle="secondary",
            command=self.show_logs,
            width=20
        ).pack(side=LEFT)

    def show_upload(self):
        self.clear_content()
        
        # Main container
        main_frame = tb.Frame(self.content)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tb.Label(
            main_frame,
            text="Upload Payslip Documents",
            font=("Segoe UI", 22, "bold"),
            bootstyle="dark"
        ).pack(pady=(0, 30))
        
        # Upload section
        upload_frame = tb.LabelFrame(main_frame, text="Select Files")
        upload_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Payslip Folder
        self.create_folder_selector(upload_frame, "Payslips Folder:", self.payslip_folder_path, 0)
        
        # Employee Excel
        self.create_file_selector(upload_frame, "Employee List:", self.employee_path, "Excel files (*.xlsx)", 1)
        
        # Stamp Image
        self.create_file_selector(upload_frame, "Company Stamp:", self.stamp_path, "Image files (*.png *.jpg *.jpeg)", 2)
        
        # Action buttons
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=(20, 0))
        
        tb.Button(
            button_frame,
            text="Validate Files",
            bootstyle="info",
            command=self.validate_files,
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="Reset to Default",
            bootstyle="secondary",
            command=self.reset_paths,
            width=15
        ).pack(side=LEFT)

    def show_send(self):
        self.clear_content()
        
        # Main container
        main_frame = tb.Frame(self.content)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tb.Label(
            main_frame,
            text="Send Payslips",
            font=("Segoe UI", 22, "bold"),
            bootstyle="dark"
        ).pack(pady=(0, 30))
        
        # Configuration frame
        config_frame = tb.LabelFrame(main_frame, text="Email Configuration")
        config_frame.pack(fill=X, pady=(0, 20), padx=20)
        
        # Production mode notice
        tb.Label(
            config_frame,
            text="🟢 PRODUCTION MODE - Real emails will be sent to employees",
            bootstyle="success",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, padx=15, pady=15)
        
        # Test email button
        tb.Button(
            config_frame,
            text="📧 Test Email Connection",
            bootstyle="info-outline",
            command=self.test_email_connection,
            width=20
        ).pack(anchor=W, padx=15, pady=(0, 10))
        
        # Preview frame
        preview_frame = tb.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill=BOTH, expand=True, pady=(0, 20), padx=20)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.preview_text.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Action buttons
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X)
        
        tb.Button(
            button_frame,
            text="Preview Process",
            bootstyle="info",
            command=self.preview_process,
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="Start Sending",
            bootstyle="success",
            command=self.start_sending,
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="Stop Process",
            bootstyle="danger",
            command=self.stop_process,
            width=15
        ).pack(side=LEFT)

    def show_logs(self):
        self.clear_content()
        
        # Main container
        main_frame = tb.Frame(self.content)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title and controls
        title_frame = tb.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        tb.Label(
            title_frame,
            text="System Logs",
            font=("Segoe UI", 22, "bold"),
            bootstyle="dark"
        ).pack(side=LEFT)
        
        tb.Button(
            title_frame,
            text="Refresh",
            bootstyle="info",
            command=self.refresh_logs,
            width=10
        ).pack(side=RIGHT)
        
        tb.Button(
            title_frame,
            text="Clear Logs",
            bootstyle="danger",
            command=self.clear_logs,
            width=10
        ).pack(side=RIGHT, padx=(0, 10))
        
        # Log display
        log_frame = tb.LabelFrame(main_frame, text="Recent Activity")
        log_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Load initial logs
        self.refresh_logs()
    
    # =====================
    # Helper Methods
    # =====================
    def create_stats_cards(self, parent):
        """Create statistics cards for dashboard"""
        cards_row1 = tb.Frame(parent)
        cards_row1.pack(fill=X, pady=(0, 20))
        
        # Total Employees Card
        card1 = tb.Frame(cards_row1, bootstyle="info", relief=tk.RAISED, borderwidth=1)
        card1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        tb.Label(card1, text="👥", font=("Segoe UI", 24)).pack(pady=(10, 5))
        tb.Label(card1, text="Total Employees", font=("Segoe UI", 12)).pack()
        self.employees_count_label = tb.Label(card1, text="0", font=("Segoe UI", 20, "bold"), bootstyle="inverse-info")
        self.employees_count_label.pack(pady=(5, 10))
        
        # Payslips Generated Card
        card2 = tb.Frame(cards_row1, bootstyle="success", relief=tk.RAISED, borderwidth=1)
        card2.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        tb.Label(card2, text="📄", font=("Segoe UI", 24)).pack(pady=(10, 5))
        tb.Label(card2, text="PDF Files", font=("Segoe UI", 12)).pack()
        self.pages_count_label = tb.Label(card2, text="0", font=("Segoe UI", 20, "bold"), bootstyle="inverse-success")
        self.pages_count_label.pack(pady=(5, 10))
        
        # Emails Sent Card
        card3 = tb.Frame(cards_row1, bootstyle="warning", relief=tk.RAISED, borderwidth=1)
        card3.pack(side=LEFT, fill=BOTH, expand=True)
        
        tb.Label(card3, text="📧", font=("Segoe UI", 24)).pack(pady=(10, 5))
        tb.Label(card3, text="Ready Status", font=("Segoe UI", 12)).pack()
        self.status_label = tb.Label(card3, text="Ready", font=("Segoe UI", 20, "bold"), bootstyle="inverse-warning")
        self.status_label.pack(pady=(5, 10))
    
    def create_folder_selector(self, parent, label_text, variable, row):
        """Create a folder selector widget"""
        frame = tb.Frame(parent)
        frame.pack(fill=X, pady=10)
        
        tb.Label(frame, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        input_frame = tb.Frame(frame)
        input_frame.pack(fill=X, pady=(5, 0))
        
        tb.Entry(input_frame, textvariable=variable, font=("Segoe UI", 10)).pack(side=LEFT, fill=X, expand=True)
        
        tb.Button(
            input_frame,
            text="Browse",
            bootstyle="outline-primary",
            command=lambda: self.browse_folder(variable),
            width=10
        ).pack(side=RIGHT, padx=(5, 0))
    
    def create_file_selector(self, parent, label_text, variable, filetypes, row):
        """Create a file selector widget"""
        frame = tb.Frame(parent)
        frame.pack(fill=X, pady=10)
        
        tb.Label(frame, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        input_frame = tb.Frame(frame)
        input_frame.pack(fill=X, pady=(5, 0))
        
        tb.Entry(input_frame, textvariable=variable, font=("Segoe UI", 10)).pack(side=LEFT, fill=X, expand=True)
        
        tb.Button(
            input_frame,
            text="Browse",
            bootstyle="outline-primary",
            command=lambda: self.browse_file(variable, filetypes),
            width=10
        ).pack(side=RIGHT, padx=(5, 0))
    
    def browse_folder(self, variable):
        """Open folder dialog to select folder"""
        try:
            foldername = filedialog.askdirectory(
                parent=self,
                title="Select Payslips Folder",
                initialdir=os.path.expanduser("~")  # Start in user home directory
            )
            
            if foldername:
                variable.set(foldername)
                self.update_status(f"Selected folder: {os.path.basename(foldername)}")
                
        except Exception as e:
            print(f"Error browsing folder: {e}")
            messagebox.showerror("Error", f"Failed to browse folder: {str(e)}")
    
    def browse_file(self, variable, filetypes):
        """Open file dialog to select file"""
        try:
            # Create proper filetypes list for tkinter
            if filetypes == "PDF files (*.pdf)":
                filetypes_list = [("PDF files", "*.pdf"), ("All files", "*.*")]
            elif filetypes == "Excel files (*.xlsx)":
                filetypes_list = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            elif filetypes == "Image files (*.png *.jpg *.jpeg)":
                filetypes_list = [("Image files", "*.png *.jpg *.jpeg"), ("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")]
            else:
                filetypes_list = [("All files", "*.*")]
            
            # Use askopenfilename with proper parent
            filename = filedialog.askopenfilename(
                parent=self,
                title="Select File",
                filetypes=filetypes_list,
                initialdir=os.path.expanduser("~")  # Start in user home directory
            )
            
            if filename:
                variable.set(filename)
                self.update_status(f"Selected: {os.path.basename(filename)}")
                
        except Exception as e:
            print(f"Error browsing file: {e}")
            messagebox.showerror("Error", f"Failed to browse files: {str(e)}")
    
    def validate_files(self):
        """Validate all selected files"""
        # Update service with current paths
        self.service.payslip_folder = self.payslip_folder_path.get()
        self.service.input_excel = self.employee_path.get()
        self.service.stamp_image = self.stamp_path.get()
        
        # Use service validation
        all_valid, validation = self.service.validate_files()
        
        # Show results
        messages = []
        for file_type, is_valid in validation.items():
            status = "✅ Valid" if is_valid else "❌ Not found"
            display_name = file_type.replace('_', ' ').title()
            messages.append(f"{display_name}: {status}")
        
        result = "All files are valid!" if all_valid else "Some files need attention."
        messagebox.showinfo("File Validation", f"{result}\n\n" + "\n".join(messages))
        
        if all_valid:
            self.update_status("All files validated successfully")
            self.refresh_stats()
        else:
            self.update_status("File validation failed")
    
    def reset_paths(self):
        """Reset all file paths to defaults"""
        self.payslip_folder_path.set("input/payslips/")
        self.employee_path.set("input/employees - 1.xlsx")
        self.stamp_path.set("input/Stamp.png")
        self.update_status("Paths reset to defaults")
    
    def preview_process(self):
        """Preview the payslip sending process"""
        # Update service with current paths
        self.service.payslip_folder = self.payslip_folder_path.get()
        self.service.input_excel = self.employee_path.get()
        self.service.stamp_image = self.stamp_path.get()
        
        preview_data = self.service.preview_process()
        
        if preview_data is None:
            messagebox.showerror("Error", "Failed to generate preview. Check your files.")
            return
        
        preview = f"Process Preview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        preview += "=" * 60 + "\n\n"
        preview += f"Mode: {preview_data['mode']} (Real emails will be sent)\n"
        preview += f"Total Employees: {preview_data['total_employees']}\n"
        preview += f"PDF Files Found: {preview_data['pdf_files']}\n"
        preview += f"Payslip Folder: {preview_data['payslip_folder']}\n"
        preview += f"Output Directory: {preview_data['output_dir']}\n\n"
        preview += "PDF Files Analysis:\n"
        preview += "-" * 40 + "\n"
        
        for pdf_info in preview_data['pdfs_found']:
            preview += f"{pdf_info['match_status']} {pdf_info['pdf_file']}\n"
            preview += f"    Matricule: {pdf_info['matricule']}\n"
            preview += f"    Employee: {pdf_info['employee_name']}\n"
            preview += f"    Email: {pdf_info['email']}\n\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview)
        self.update_status("Process preview generated")
    
    def start_sending(self):
        """Start the payslip sending process"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing is already running!")
            return
        
        # Always show confirmation since we're in production mode
        result = messagebox.askyesno(
            "Confirm Sending", 
            "You are about to send REAL payslip emails to employees.\n\n"
            "This will process all PDF files in the selected folder and send them to matching employees.\n\n"
            "Continue?"
        )
        if not result:
            return
        
        # Update service with current paths and settings
        self.service.payslip_folder = self.payslip_folder_path.get()
        self.service.input_excel = self.employee_path.get()
        self.service.stamp_image = self.stamp_path.get()
        self.service.simulation_mode = False  # Always production now
        
        self.is_processing = True
        self.update_status("Starting payslip distribution...")
        try:
            self.status_label.config(text="Processing", bootstyle="inverse-danger")
        except:
            pass  # Handle UI error gracefully
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.run_payslip_process)
        thread.daemon = True
        thread.start()
    
    def stop_process(self):
        """Stop the current process"""
        if self.is_processing:
            self.service.cancel_processing()
            self.update_status("Cancelling process...")
            messagebox.showinfo("Stopping", "Process cancellation requested. Please wait...")
        else:
            self.update_status("No process running")
    
    def run_payslip_process(self):
        """Run the actual payslip process (in background thread)"""
        try:
            success, message = self.service.process_payslips()
            
            # Update UI in main thread
            self.after(0, self.processing_complete, success, message)
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.after(0, self.processing_complete, False, error_msg)
    
    def refresh_logs(self):
        """Refresh the log display"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            # Try to read log files
            log_files = ['logs/app.log', 'logs/error.log']
            log_content = f"System Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            log_content += "=" * 60 + "\n\n"
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():
                                log_content += f"--- {os.path.basename(log_file)} ---\n"
                                log_content += content + "\n\n"
                    except Exception as e:
                        log_content += f"Error reading {log_file}: {str(e)}\n\n"
            
            if log_content == f"System Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "=" * 60 + "\n\n":
                log_content += "No logs available yet."
            
            self.log_text.insert(1.0, log_content)
            self.log_text.config(state=tk.DISABLED)
            self.update_status("Logs refreshed")
    
    def clear_logs(self):
        """Clear all log files"""
        result = messagebox.askyesno("Confirm", "Clear all system logs?")
        if result:
            try:
                log_files = ['logs/app.log', 'logs/error.log']
                for log_file in log_files:
                    if os.path.exists(log_file):
                        open(log_file, 'w').close()
                
                self.refresh_logs()
                self.update_status("Logs cleared successfully")
                messagebox.showinfo("Success", "All logs have been cleared")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def update_status(self, message):
        """Update the status bar"""
        if hasattr(self, 'status_bar'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.status_bar.config(text=f"[{timestamp}] {message}")
        
        # Also log to file if logger is available
        try:
            from logger import log_info
            log_info(message)
        except:
            pass
    
    def refresh_stats(self):
        """Refresh dashboard statistics"""
        try:
            # Update service paths
            self.service.payslip_folder = self.payslip_folder_path.get()
            self.service.input_excel = self.employee_path.get()
            self.service.stamp_image = self.stamp_path.get()
            
            # Get counts
            employee_count = self.service.get_employee_count()
            page_count = self.service.get_pdf_page_count()
            
            # Update labels
            self.employees_count_label.config(text=str(employee_count))
            self.pages_count_label.config(text=str(page_count))
            
            # Update status based on file availability
            if employee_count > 0 and page_count > 0:
                self.status_label.config(text="Ready", bootstyle="inverse-success")
            else:
                self.status_label.config(text="Missing Files", bootstyle="inverse-warning")
                
        except Exception as e:
            print(f"Error refreshing stats: {e}")
            # Try to update just the counts without status
            try:
                employee_count = self.service.get_employee_count()
                page_count = self.service.get_pdf_page_count()
                self.employees_count_label.config(text=str(employee_count))
                self.pages_count_label.config(text=str(page_count))
            except:
                pass
    
    def on_service_progress(self, message, status="info"):
        """Callback for service progress updates"""
        # Update status bar
        self.update_status(message)
        
        # Also add to logs if we're on the logs page
        if hasattr(self, 'log_text'):
            try:
                self.log_text.config(state=tk.NORMAL)
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Add color coding based on status
                if status == "error":
                    prefix = "❌"
                elif status == "success":
                    prefix = "✅"
                elif status == "warning":
                    prefix = "⚠️"
                else:
                    prefix = "ℹ️"
                
                self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
                self.log_text.see(tk.END)  # Auto-scroll to bottom
                self.log_text.config(state=tk.DISABLED)
            except:
                pass
        
        # Update preview if we're on send page
        if hasattr(self, 'preview_text'):
            try:
                current_text = self.preview_text.get(1.0, tk.END)
                if "Process Preview" not in current_text:  # Only add if not in preview mode
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.preview_text.insert(tk.END, f"[{timestamp}] {message}\n")
                    self.preview_text.see(tk.END)
            except:
                pass
    
    def processing_complete(self, success, message):
        """Called when processing is complete"""
        self.is_processing = False
        
        # Reset cancellation flag
        self.service._cancelled = False
        
        try:
            if success:
                self.status_label.config(text="Complete", bootstyle="inverse-success")
                messagebox.showinfo("Success", message)
            else:
                if "cancelled" in message.lower():
                    self.status_label.config(text="Cancelled", bootstyle="inverse-warning")
                    messagebox.showinfo("Cancelled", message)
                else:
                    self.status_label.config(text="Error", bootstyle="inverse-danger")
                    messagebox.showerror("Error", message)
        except:
            pass  # Handle UI error gracefully
        
        # Refresh stats after processing
        try:
            self.refresh_stats()
        except:
            pass
    
    def on_simulation_mode_change(self):
        """Handle simulation mode checkbox change"""
        is_simulation = self.simulation_var.get()
        self.service.simulation_mode = is_simulation
        
        mode_text = "SIMULATION" if is_simulation else "PRODUCTION"
        status_type = "info" if is_simulation else "warning"
        self.update_status(f"Mode changed to: {mode_text}", status_type)
        
        if not is_simulation:
            messagebox.showinfo(
                "Production Mode", 
                "You are now in PRODUCTION mode. Real emails will be sent!"
            )
    
    def test_email_connection(self):
        """Test email connection and send test email"""
        # Update service with current simulation mode
        self.service.simulation_mode = self.simulation_var.get()
        
        # Run test in background thread
        thread = threading.Thread(target=self.run_email_test)
        thread.daemon = True
        thread.start()
    
    def run_email_test(self):
        """Run email test in background thread"""
        try:
            success = self.service.test_email_connection()
            
            # Update UI in main thread
            self.after(0, self.email_test_complete, success)
            
        except Exception as e:
            error_msg = f"Email test error: {str(e)}"
            self.after(0, self.email_test_complete, False, error_msg)
    
    def email_test_complete(self, success, message=""):
        """Called when email test is complete"""
        if success:
            messagebox.showinfo("Success", "Email test successful! Check your inbox.")
        else:
            messagebox.showerror("Error", f"Email test failed: {message}")


# =====================
# Run app
# =====================
if __name__ == "__main__":
    app = CRTVPayslipApp()
    app.mainloop()
