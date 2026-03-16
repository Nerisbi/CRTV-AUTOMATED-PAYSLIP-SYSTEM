from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
from datetime import datetime
import threading
from services.payslip_service_clean import PayslipService


class CRTVPayslipApp(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")

        self.title("CRTV Automated Payslip Distribution System")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.minsize(1000, 600)
        
        # Variables for file paths
        self.payslip_path = tk.StringVar()
        self.employee_path = tk.StringVar()
        self.stamp_path = tk.StringVar()
        
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
        
        # Add keyboard shortcuts
        self.bind('<Control-r>', lambda e: self.reset_processing_state())
        self.bind('<F5>', lambda e: self.reset_processing_state())
    
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
            ("Upload Files", "upload", self.show_upload),
            ("Send Payslips", "send", self.show_send),
            ("Logs", "logs", self.show_logs),
            ("Reset State", "exit", self.reset_processing_state),
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
            text="📤 Upload Files",
            bootstyle="success",
            command=self.show_upload,
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            actions_row,
            text="📧 Send Payslips",
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
            text="Upload Required Files",
            font=("Segoe UI", 22, "bold"),
            bootstyle="dark"
        ).pack(pady=(0, 30))
        
        # Upload section
        upload_frame = tb.LabelFrame(main_frame, text="Select Files")
        upload_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Payslip PDF
        self.create_file_selector(upload_frame, "Payslip PDF:", self.payslip_path, "PDF files (*.pdf)", 0)
        
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
            text="Clear Selections",
            bootstyle="secondary",
            command=self.clear_paths,
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
        config_frame = tb.LabelFrame(main_frame, text="Process Information")
        config_frame.pack(fill=X, pady=(0, 20), padx=20)
        
        tb.Label(
            config_frame,
            text="This will generate individual payslip PDFs and email them to all employees.",
            font=("Segoe UI", 10),
            bootstyle="info"
        ).pack(anchor=W, padx=15, pady=15)
        
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
            text="Start Distribution",
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
        
        # PDF Pages Card
        card2 = tb.Frame(cards_row1, bootstyle="success", relief=tk.RAISED, borderwidth=1)
        card2.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        tb.Label(card2, text="📄", font=("Segoe UI", 24)).pack(pady=(10, 5))
        tb.Label(card2, text="PDF Pages", font=("Segoe UI", 12)).pack()
        self.pages_count_label = tb.Label(card2, text="0", font=("Segoe UI", 20, "bold"), bootstyle="inverse-success")
        self.pages_count_label.pack(pady=(5, 10))
        
        # Status Card
        card3 = tb.Frame(cards_row1, bootstyle="warning", relief=tk.RAISED, borderwidth=1)
        card3.pack(side=LEFT, fill=BOTH, expand=True)
        
        tb.Label(card3, text="📧", font=("Segoe UI", 24)).pack(pady=(10, 5))
        tb.Label(card3, text="System Status", font=("Segoe UI", 12)).pack()
        self.status_label = tb.Label(card3, text="Ready", font=("Segoe UI", 20, "bold"), bootstyle="inverse-warning")
        self.status_label.pack(pady=(5, 10))
    
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
        self.service.input_pdf = self.payslip_path.get()
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
    
    def clear_paths(self):
        """Clear all file paths"""
        self.payslip_path.set("")
        self.employee_path.set("")
        self.stamp_path.set("")
        self.update_status("File paths cleared")
    
    def preview_process(self):
        """Preview the payslip sending process"""
        # Update service with current paths
        self.service.input_pdf = self.payslip_path.get()
        self.service.input_excel = self.employee_path.get()
        self.service.stamp_image = self.stamp_path.get()
        
        preview_data = self.service.preview_process()
        
        if preview_data is None:
            messagebox.showerror("Error", "Failed to generate preview. Check your files.")
            return
        
        preview = f"Process Preview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        preview += "=" * 60 + "\n\n"
        preview += f"Total Employees: {preview_data['total_employees']}\n"
        preview += f"PDF Pages: {preview_data['pdf_pages']}\n"
        preview += f"Payslip File: {preview_data['payslip_file']}\n"
        preview += f"Output Directory: {preview_data['output_dir']}\n\n"
        preview += "Employees to process:\n"
        preview += "-" * 40 + "\n"
        
        for emp in preview_data['employees']:
            preview += f"• {emp['name']} -> {emp['email']} (Page {emp['page']})\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview)
        self.update_status("Process preview generated")
    
    def start_sending(self):
        """Start the payslip sending process"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing is already running!")
            return
        
        # Check if files are selected
        if not self.payslip_path.get() or not self.employee_path.get() or not self.stamp_path.get():
            messagebox.showwarning("Missing Files", "Please select all required files before starting distribution.")
            return
        
        # Confirm before starting
        result = messagebox.askyesno(
            "Confirm", 
            "This will generate and email payslips to all employees.\n\nContinue?"
        )
        if not result:
            return
        
        # Update service with current paths
        self.service.input_pdf = self.payslip_path.get()
        self.service.input_excel = self.employee_path.get()
        self.service.stamp_image = self.stamp_path.get()
        
        self.is_processing = True
        self.update_status("Starting payslip distribution...")
        
        # Safely update status label if it exists
        try:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="Processing", bootstyle="inverse-danger")
        except:
            pass  # Label doesn't exist or is on different page
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.run_payslip_process)
        thread.daemon = True
        thread.start()
    
    def stop_process(self):
        """Stop the current process"""
        if self.is_processing:
            self.is_processing = False
            self.update_status("Process stopped by user")
            
            # Safely update status label if it exists
            try:
                if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                    self.status_label.config(text="Stopped", bootstyle="inverse-warning")
            except:
                pass  # Label doesn't exist or is on different page
                
            messagebox.showinfo("Stopped", "Process has been stopped. You can start a new distribution.")
        else:
            self.update_status("No process running")
            messagebox.showinfo("Info", "No process is currently running.")
    
    def reset_processing_state(self):
        """Reset the processing state - call this if app gets stuck"""
        self.is_processing = False
        
        # Safely update status label if it exists
        try:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="Ready", bootstyle="inverse-warning")
        except:
            pass  # Label doesn't exist or is on different page
            
        self.update_status("Processing state reset")
    
    def run_payslip_process(self):
        """Run the actual payslip process (in background thread)"""
        try:
            success, message = self.service.process_payslips()
            
            # Update UI in main thread
            self.after(0, self.processing_complete, success, message)
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.after(0, self.processing_complete, False, error_msg)
        finally:
            # Always ensure processing state is reset
            self.is_processing = False
    
    def refresh_logs(self):
        """Refresh the log display using the logger module"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            try:
                # Use the logger module to get logs
                from logger import get_logs
                log_content = get_logs("payslip", 200)  # Get last 200 lines
                
                if log_content and "No payslip log file found" not in log_content:
                    display_content = f"System Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    display_content += "=" * 60 + "\n\n"
                    display_content += log_content
                else:
                    display_content = f"System Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    display_content += "=" * 60 + "\n\n"
                    display_content += "No logs available yet. Start processing payslips to see logs here."
                
                self.log_text.insert(1.0, display_content)
                self.log_text.config(state=tk.DISABLED)
                self.update_status("Logs refreshed")
                
            except Exception as e:
                error_content = f"Error loading logs: {str(e)}"
                self.log_text.insert(1.0, error_content)
                self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Clear all log files using the logger module"""
        result = messagebox.askyesno("Confirm", "Clear all system logs?")
        if result:
            try:
                from logger import clear_logs
                success = clear_logs("payslip")
                
                if success:
                    self.refresh_logs()
                    self.update_status("Logs cleared successfully")
                    messagebox.showinfo("Success", "All logs have been cleared")
                else:
                    messagebox.showerror("Error", "Failed to clear logs")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def refresh_stats(self):
        """Refresh dashboard statistics"""
        try:
            # Update service paths
            self.service.input_pdf = self.payslip_path.get()
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
        
        # Safely update status label if it exists
        try:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                if success:
                    self.status_label.config(text="Complete", bootstyle="inverse-success")
                else:
                    self.status_label.config(text="Error", bootstyle="inverse-danger")
        except:
            pass  # Label doesn't exist or is on different page
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
        
        # Refresh stats after processing
        self.refresh_stats()
    
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


# =====================
# Run app
# =====================
if __name__ == "__main__":
    app = CRTVPayslipApp()
    app.mainloop()
