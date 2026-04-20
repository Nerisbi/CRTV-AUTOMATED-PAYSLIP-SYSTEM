#!/usr/bin/env python3
"""
Test multiple email functionality
"""

import pandas as pd
import os

print("=== MULTIPLE EMAIL TEST ===")
print("This shows how the system handles multiple email addresses")
print()

# Create sample data to demonstrate
sample_data = {
    'Name': ['John Doe', 'Jane Smith', 'Mike Johnson'],
    'Email': ['john@work.com', 'jane@company.com', 'mike@office.com'],
    'Email2': ['john@personal.com', '', 'mike@home.com'],
    'Matricule': ['3060', '6032', '1234']
}

print("SAMPLE EXCEL STRUCTURE:")
print("=" * 60)
df_sample = pd.DataFrame(sample_data)
print(df_sample.to_string(index=False))
print()

print("HOW THE SYSTEM WILL PROCESS:")
print("=" * 60)

for idx, row in df_sample.iterrows():
    name = row['Name']
    email1 = row['Email']
    email2 = row['Email2']
    
    print(f"\nEmployee: {name}")
    print(f"  Email 1: {email1}")
    print(f"  Email 2: {email2}")
    
    if email1 and email2:
        print(f"  -> Will send payslip to BOTH emails")
    elif email1:
        print(f"  -> Will send payslip to Email 1 only")
    elif email2:
        print(f"  -> Will send payslip to Email 2 only")
    else:
        print(f"  -> ERROR: No emails provided!")

print()
print("=== EXCEL FILE SETUP INSTRUCTIONS ===")
print("1. Open your employees.xlsx file")
print("2. Add a new column called 'Email2'")
print("3. Fill in second email addresses (leave blank if not needed)")
print("4. Save the file")
print()
print("EXAMPLE:")
print("Name        | Email                | Email2               | Matricule")
print("------------|---------------------|----------------------|----------")
print("John Doe    | john@work.com       | john@personal.com    | 3060")
print("Jane Smith  | jane@company.com    |                      | 6032")
print("Mike Johnson| mike@office.com     | mike@home.com        | 1234")
print()
print("The system will automatically detect and use both email addresses!")
