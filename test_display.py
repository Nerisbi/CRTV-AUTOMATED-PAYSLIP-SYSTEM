#!/usr/bin/env python3
"""
Test if tkinter can display windows properly
"""

import tkinter as tk

print("=== DISPLAY TEST ===")
print("Testing basic tkinter window display...")

try:
    # Create a simple test window
    root = tk.Tk()
    root.title("Display Test")
    root.geometry("300x200")
    
    label = tk.Label(root, text="If you see this, display works!")
    label.pack(pady=20)
    
    button = tk.Button(root, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("Window created successfully")
    print("If the window doesn't appear, there's a display issue")
    print("Try running: python -m tkinter")
    
    # This will show the window briefly
    root.after(3000, root.quit)  # Auto-close after 3 seconds
    root.mainloop()
    
    print("Window test completed")
    
except Exception as e:
    print(f"Display test failed: {e}")
    import traceback
    traceback.print_exc()
    
    print("\nPOSSIBLE SOLUTIONS:")
    print("1. Update graphics drivers")
    print("2. Run Windows Display troubleshooter")
    print("3. Try running as administrator")
    print("4. Check if tkinter is properly installed")
    print("5. Try: python -m tkinter (this should show a demo window)")
