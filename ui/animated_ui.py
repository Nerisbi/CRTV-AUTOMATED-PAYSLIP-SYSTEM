import tkinter as tk
from tkinter import Canvas, font
import time
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoadingAnimation:
    def __init__(self):
        self.splash = tk.Toplevel()
        self.splash.title("")
        
        # Remove window decorations
        self.splash.overrideredirect(True)
        
        # Center on screen
        self.splash.geometry("500x300+{}+{}".format(
            (self.splash.winfo_screenwidth() // 2) - 250,
            (self.splash.winfo_screenheight() // 2) - 150
        ))
        
        # Background
        self.splash.configure(bg='#1e3a8a')
        
        # Create canvas for animation
        self.canvas = Canvas(
            self.splash,
            width=500,
            height=300,
            bg='#1e3a8a',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Animation elements
        self.dots = []
        self.text_id = None
        self.subtitle_id = None
        self.progress_bar = None
        self.progress_width = 0
        
        # Start animation
        self.animate()
        
    def draw_logo(self):
        """Draw CRTV logo/text"""
        # Main title
        self.text_id = self.canvas.create_text(
            250, 100,
            text="CRTV",
            font=('Segoe UI', 48, 'bold'),
            fill='white'
        )
        
        # Subtitle
        self.subtitle_id = self.canvas.create_text(
            250, 140,
            text="Automated Payslip Distribution System",
            font=('Segoe UI', 12),
            fill='#93c5fd'
        )
        
    def draw_loading_dots(self):
        """Draw animated loading dots"""
        # Clear existing dots
        for dot in self.dots:
            self.canvas.delete(dot)
        self.dots.clear()
        
        # Create new dots with wave effect
        dot_colors = ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af']
        dot_positions = [150, 200, 250, 300, 350]
        
        for i, (x, color) in enumerate(zip(dot_positions, dot_colors)):
            size = 8 + (i * 2)  # Varying sizes for wave effect
            dot = self.canvas.create_oval(
                x - size, 180 - size,
                x + size, 180 + size,
                fill=color,
                outline=''
            )
            self.dots.append(dot)
            
    def draw_progress_bar(self):
        """Draw animated progress bar"""
        # Progress bar background
        self.canvas.create_rectangle(
            100, 220, 400, 240,
            fill='#1e40af',
            outline='#3b82f6',
            width=2
        )
        
        # Progress bar fill (animated)
        if self.progress_bar:
            self.canvas.delete(self.progress_bar)
            
        self.progress_bar = self.canvas.create_rectangle(
            100, 220, 100 + self.progress_width, 240,
            fill='#60a5fa',
            outline=''
        )
        
        # Progress text
        self.canvas.create_text(
            250, 260,
            text=f"Loading... {int(self.progress_width / 3)}%",
            font=('Segoe UI', 10),
            fill='white',
            tags="progress_text"
        )
        
    def animate(self):
        """Main animation loop"""
        # Draw static elements
        self.draw_logo()
        
        # Animate loading dots
        self.draw_loading_dots()
        
        # Animate progress bar
        if self.progress_width < 300:
            self.progress_width += 3
        else:
            self.progress_width = 0
            
        self.draw_progress_bar()
        
        # Continue animation
        self.splash.after(50, self.animate)
        
    def close(self):
        """Close splash screen"""
        self.splash.destroy()

class AnimatedCRTVApp:
    def __init__(self):
        # Show loading animation first
        self.loading = LoadingAnimation()
        
        # Start main app after delay
        self.root = None
        threading.Timer(3.0, self.start_main_app).start()
        
    def start_main_app(self):
        """Start the main application after loading"""
        try:
            # Import the fixed UI
            from ui.fixed_compact_ui import FixedCompactUI
            
            # Close loading animation
            self.loading.close()
            
            # Create and start main app
            self.root = FixedCompactUI().root
            
        except Exception as e:
            print(f"Error starting main app: {e}")
            self.loading.close()

def main():
    app = AnimatedCRTVApp()
    
    # Keep the loading screen running until main app starts
    try:
        # This will keep the splash screen alive
        app.loading.splash.mainloop()
    except:
        pass

if __name__ == "__main__":
    main()
