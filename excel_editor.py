import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from individual_retrieval import update_employee_email, get_employee_by_matricule
from logger import log_info, log_error

class ExcelEditor:
    def __init__(self, parent, excel_path):
        self.parent = parent
        self.excel_path = excel_path
        self.employees_df = None
        self.current_row = None
        
        self.create_editor_window()
        self.load_employee_data()
    
    def create_editor_window(self):
        """Create the Excel editor window"""
        self.editor_window = tk.Toplevel(self.parent)
        self.editor_window.title("Employee Data Editor")
        self.editor_window.geometry("900x600")
        self.editor_window.transient(self.parent)
        self.editor_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.editor_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.editor_window.columnconfigure(0, weight=1)
        self.editor_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search Employee", padding="5")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Matricule:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_employee).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=3, padx=5)
        ttk.Button(search_frame, text="Refresh Data", command=self.load_employee_data).grid(row=0, column=4, padx=5)
        
        # Treeview frame
        tree_frame = ttk.LabelFrame(main_frame, text="Employee Records", padding="5")
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
        tree_scroll.config(command=self.tree.yview)
        
        # Define columns
        columns = ("Matricule", "Name", "Email", "Email 2")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        # Define headings
        self.tree.heading("Matricule", text="Matricule")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Primary Email")
        self.tree.heading("Email 2", text="Secondary Email")
        
        # Configure column widths
        self.tree.column("Matricule", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Email", width=250)
        self.tree.column("Email 2", width=250)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        
        # Edit frame
        edit_frame = ttk.LabelFrame(main_frame, text="Edit Selected Employee", padding="5")
        edit_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Edit fields
        ttk.Label(edit_frame, text="Matricule:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.edit_matricule = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.edit_matricule, state="readonly", width=20).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="Name:").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.edit_name = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.edit_name, state="readonly", width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="Primary Email:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.edit_email1 = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.edit_email1, width=30).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="Secondary Email:").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        self.edit_email2 = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.edit_email2, width=30).grid(row=1, column=3, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_fields).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Row", command=self.delete_employee).grid(row=0, column=2, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Keyboard shortcuts
        self.editor_window.bind('<Control-s>', lambda e: self.save_changes())
        self.editor_window.bind('<Control-f>', lambda e: self.search_var.set(''))
        search_entry.focus()
    
    def load_employee_data(self):
        """Load employee data from Excel file"""
        try:
            if not os.path.exists(self.excel_path):
                messagebox.showerror("Error", f"Excel file not found:\n{self.excel_path}")
                return
            
            self.employees_df = pd.read_excel(self.excel_path, engine="openpyxl")
            
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Populate tree
            for idx, row in self.employees_df.iterrows():
                matricule = str(row.get('Matricule', '')).strip()
                name = str(row.get('Name', '')).strip()
                email1 = str(row.get('Email', '')).strip()
                email2 = str(row.get('Email 2', '')).strip()
                
                self.tree.insert("", "end", values=(matricule, name, email1, email2), tags=(str(idx),))
            
            self.status_var.set(f"Loaded {len(self.employees_df)} employee records")
            log_info(f"Excel editor loaded {len(self.employees_df)} records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file:\n{str(e)}")
            log_error(f"Error loading Excel file: {e}")
    
    def search_employee(self):
        """Search employee by matricule"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
        
        # Clear current selection
        for item in self.tree.get_children():
            self.tree.selection_remove(item)
        
        # Search in tree
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] and values[0].upper() == search_term.upper():
                self.tree.selection_add(item)
                self.tree.see(item)
                self.status_var.set(f"Found employee: {values[1]} ({values[0]})")
                return
        
        self.status_var.set(f"No employee found with matricule: {search_term}")
        messagebox.showinfo("Not Found", f"No employee found with matricule: {search_term}")
    
    def clear_search(self):
        """Clear search and selection"""
        self.search_var.set("")
        for item in self.tree.get_children():
            self.tree.selection_remove(item)
        self.reset_fields()
        self.status_var.set("Search cleared")
    
    def on_employee_select(self, event):
        """Handle employee selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        tags = self.tree.item(item, "tags")
        
        if tags:
            self.current_row = int(tags[0])
            
            # Update edit fields
            self.edit_matricule.set(values[0])
            self.edit_name.set(values[1])
            self.edit_email1.set(values[2])
            self.edit_email2.set(values[3])
            
            self.status_var.set(f"Selected: {values[1]} ({values[0]})")
    
    def save_changes(self):
        """Save changes to selected employee"""
        if self.current_row is None:
            messagebox.showwarning("No Selection", "Please select an employee to edit")
            return
        
        try:
            # Get current values
            matricule = self.edit_matricule.get().strip()
            name = self.edit_name.get().strip()
            email1 = self.edit_email1.get().strip()
            email2 = self.edit_email2.get().strip()
            
            # Validate required fields
            if not matricule or not name:
                messagebox.showerror("Validation Error", "Matricule and Name are required")
                return
            
            # Validate email format if provided
            if email1 and not self.validate_email(email1):
                messagebox.showerror("Validation Error", "Invalid primary email format")
                return
            
            if email2 and not self.validate_email(email2):
                messagebox.showerror("Validation Error", "Invalid secondary email format")
                return
            
            # Update DataFrame
            self.employees_df.at[self.current_row, 'Matricule'] = matricule
            self.employees_df.at[self.current_row, 'Name'] = name
            self.employees_df.at[self.current_row, 'Email'] = email1
            self.employees_df.at[self.current_row, 'Email 2'] = email2
            
            # Save to Excel file
            self.employees_df.to_excel(self.excel_path, index=False, engine='openpyxl')
            
            # Update tree
            for item in self.tree.get_children():
                tags = self.tree.item(item, "tags")
                if tags and int(tags[0]) == self.current_row:
                    self.tree.item(item, values=(matricule, name, email1, email2))
                    break
            
            self.status_var.set(f"Changes saved for {name} ({matricule})")
            log_info(f"Employee data updated: {name} ({matricule})")
            messagebox.showinfo("Success", f"Employee data saved successfully:\n{name} ({matricule})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes:\n{str(e)}")
            log_error(f"Error saving employee changes: {e}")
    
    def reset_fields(self):
        """Reset edit fields to current selection"""
        if self.current_row is not None:
            selection = self.tree.selection()
            if selection:
                item = selection[0]
                values = self.tree.item(item, "values")
                self.edit_matricule.set(values[0])
                self.edit_name.set(values[1])
                self.edit_email1.set(values[2])
                self.edit_email2.set(values[3])
    
    def delete_employee(self):
        """Delete selected employee"""
        if self.current_row is None:
            messagebox.showwarning("No Selection", "Please select an employee to delete")
            return
        
        name = self.edit_name.get()
        matricule = self.edit_matricule.get()
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employee:\n{name} ({matricule})?"):
            try:
                # Remove from DataFrame
                self.employees_df = self.employees_df.drop(self.current_row).reset_index(drop=True)
                
                # Save to Excel
                self.employees_df.to_excel(self.excel_path, index=False, engine='openpyxl')
                
                # Reload data
                self.load_employee_data()
                self.reset_fields()
                self.current_row = None
                
                self.status_var.set(f"Deleted employee: {name} ({matricule})")
                log_info(f"Employee deleted: {name} ({matricule})")
                messagebox.showinfo("Success", f"Employee deleted successfully:\n{name} ({matricule})")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete employee:\n{str(e)}")
                log_error(f"Error deleting employee: {e}")
    
    def validate_email(self, email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

def open_excel_editor(parent, excel_path):
    """Open Excel editor window"""
    return ExcelEditor(parent, excel_path)
