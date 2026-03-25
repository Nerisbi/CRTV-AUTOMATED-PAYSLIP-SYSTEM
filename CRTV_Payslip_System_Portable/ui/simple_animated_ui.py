import tkinter as tk
from tkinter import Canvas
import time
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleSplashScreen:
    def __init__(self):
        # Create splash window
        self.splash = tk.Toplevel()
        self.splash.title("")
        
        # Remove decorations and center
        self.splash.overrideredirect(True)
        width, height = 500, 350
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Background
        self.splash.configure(bg='#1e3a8a')
        
        # Canvas for drawing
        self.canvas = Canvas(
            self.splash,
            width=width,
            height=height,
            bg='#1e3a8a',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Animation variables
        self.frame = 0
        self.dots = []
        self.progress = 0
        
        # Start animation
        self.animate()
        
    def draw_static_elements(self):
        """Draw elements that don't change"""
        # Title
        self.canvas.create_text(
            250, 100,
            text="CRTV",
            font=('Segoe UI', 42, 'bold'),
            fill='white'
        )
        
        # Subtitle
        self.canvas.create_text(
            250, 140,
            text="Automated Payslip Distribution System",
            font=('Segoe UI', 11),
            fill='#93c5fd'
        )
        
        # Progress bar background
        self.canvas.create_rectangle(
            100, 250, 400, 270,
            fill='#1e40af',
            outline='#3b82f6',
            width=2
        )
        
    def draw_animated_dots(self):
        """Draw animated loading dots"""
        # Clear previous dots
        for dot in self.dots:
            self.canvas.delete(dot)
        self.dots.clear()
        
        # Create wave effect with dots
        colors = ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af']
        positions = [150, 200, 250, 300, 350]
        
        for i, (x, color) in enumerate(zip(positions, colors)):
            # Wave motion
            wave = math.sin(self.frame * 0.1 + i) * 3
            size = 6 + wave
            
            dot = self.canvas.create_oval(
                x - size, 200 - size,
                x + size, 200 + size,
                fill=color,
                outline=''
            )
            self.dots.append(dot)
            
    def draw_progress_bar(self):
        """Draw animated progress bar"""
        # Update progress
        if self.progress < 300:
            self.progress += 2
        else:
            self.progress = 0
            
        # Clear previous progress
        self.canvas.delete("progress")
        
        # Draw progress fill
        self.canvas.create_rectangle(
            100, 250, 100 + self.progress, 270,
            fill='#60a5fa',
            outline='',
            tags="progress"
        )
        
        # Progress text
        percentage = int((self.progress / 300) * 100)
        self.canvas.create_text(
            250, 290,
            text=f"Loading... {percentage}%",
            font=('Segoe UI', 10),
            fill='white',
            tags="progress"
        )
        
    def animate(self):
        """Main animation loop"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw all elements
        self.draw_static_elements()
        self.draw_animated_dots()
        self.draw_progress_bar()
        
        # Update frame counter
        self.frame += 1
        
        # Schedule next frame
        self.splash.after(50, self.animate)
        
    def close(self):
        """Close splash screen"""
        self.splash.destroy()

class AnimatedAppLauncher:
    def __init__(self):
        # Show splash screen
        self.splash = SimpleSplashScreen()
        
        # Schedule main app launch using the splash window
        self.splash.splash.after(3500, self.launch_main_app)
        
    def launch_main_app(self):
        """Launch the main application"""
        try:
            # Close splash
            self.splash.close()
            
            # Small delay
            time.sleep(0.3)
            
            # Import and start main app
            from ui.fixed_compact_ui import FixedCompactUI
            main_app = FixedCompactUI()
            main_app.run()
            
        except Exception as e:
            print(f"Error launching main app: {e}")
            self.splash.close()

def main():
    """Main entry point"""
    launcher = AnimatedAppLauncher()
    
    # Start the splash screen
    launcher.splash.splash.mainloop()

if __name__ == "__main__":
    main()
