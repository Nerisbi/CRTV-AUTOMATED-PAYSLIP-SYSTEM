import tkinter as tk
from tkinter import Canvas
import time
import threading
import math
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProfessionalSplash:
    def __init__(self):
        self.splash = tk.Toplevel()
        self.splash.title("")
        
        # Remove window decorations for clean look
        self.splash.overrideredirect(True)
        
        # Set size and center
        width, height = 600, 400
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Professional background with gradient effect
        self.splash.configure(bg='#0f172a')
        
        # Create canvas
        self.canvas = Canvas(
            self.splash,
            width=width,
            height=height,
            bg='#0f172a',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Animation variables
        self.animation_frame = 0
        self.particles = []
        self.wave_offset = 0
        self.progress = 0
        self.text_opacity = 0
        
        # Initialize particles
        self.create_particles()
        
        # Start animation
        self.animate()
        
    def create_particles(self):
        """Create floating particles for background effect"""
        for _ in range(20):
            particle = {
                'x': random.random() * 600,
                'y': random.random() * 400,
                'size': random.random() * 3 + 1,
                'speed': random.random() * 0.5 + 0.2,
                'opacity': random.random() * 0.5 + 0.3
            }
            self.particles.append(particle)
            
    def draw_background_gradient(self):
        """Draw gradient background"""
        for i in range(10):
            color_value = 15 + i * 2
            color = f'#{color_value:02x}{color_value+5:02x}{color_value+15:02x}'
            self.canvas.create_rectangle(
                0, i * 40, 600, (i + 1) * 40,
                fill=color,
                outline=''
            )
            
    def draw_particles(self):
        """Draw and animate floating particles"""
        for particle in self.particles:
            # Update position
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                particle['y'] = 410
                particle['x'] = random.random() * 600
                
            # Draw particle
            size = particle['size']
            opacity = int(particle['opacity'] * 255)
            color = f'#{opacity:02x}{opacity+20:02x}{opacity+40:02x}'
            
            self.canvas.create_oval(
                particle['x'] - size, particle['y'] - size,
                particle['x'] + size, particle['y'] + size,
                fill=color,
                outline='',
                tags="particle"
            )
            
    def draw_logo(self):
        """Draw animated CRTV logo"""
        # Fade in effect
        if self.text_opacity < 255:
            self.text_opacity += 5
            
        # Main CRTV text with glow effect
        glow_size = 2 + math.sin(self.animation_frame * 0.05) * 1
        
        # Glow layers
        for i in range(3):
            glow_color = f'#{30+i*20:02x}{60+i*30:02x}{120+i*40:02x}'
            self.canvas.create_text(
                300 + i * glow_size, 130 + i * glow_size,
                text="CRTV",
                font=('Segoe UI', 52 - i * 4, 'bold'),
                fill=glow_color,
                tags="logo"
            )
            
        # Main text
        text_color = f'#{self.text_opacity:02x}{self.text_opacity:02x}{255:02x}'
        self.canvas.create_text(
            300, 130,
            text="CRTV",
            font=('Segoe UI', 48, 'bold'),
            fill=text_color,
            tags="logo"
        )
        
        # Subtitle with typewriter effect
        subtitle_text = "Automated Payslip Distribution System"
        display_length = min(len(subtitle_text), self.animation_frame // 3)
        display_text = subtitle_text[:display_length]
        
        self.canvas.create_text(
            300, 170,
            text=display_text,
            font=('Segoe UI', 11),
            fill='#94a3b8',
            tags="logo"
        )
        
    def draw_loading_animation(self):
        """Draw sophisticated loading animation"""
        center_x, center_y = 300, 250
        
        # Rotating rings
        for ring in range(3):
            angle = self.animation_frame * 0.02 + ring * 120
            radius = 30 + ring * 15
            
            for dot in range(8):
                dot_angle = angle + (dot * 45)
                dot_x = center_x + math.cos(math.radians(dot_angle)) * radius
                dot_y = center_y + math.sin(math.radians(dot_angle)) * radius
                
                # Pulsing effect
                pulse = math.sin(self.animation_frame * 0.1 + dot) * 2 + 4
                color = f'#{100+ring*50:02x}{150+ring*30:02x}{255:02x}'
                
                self.canvas.create_oval(
                    dot_x - pulse, dot_y - pulse,
                    dot_x + pulse, dot_y + pulse,
                    fill=color,
                    outline='',
                    tags="loading"
                )
                
        # Center loading text
        loading_text = "LOADING" + "." * ((self.animation_frame // 20) % 4)
        self.canvas.create_text(
            center_x, center_y + 60,
            text=loading_text,
            font=('Segoe UI', 10, 'bold'),
            fill='#cbd5e1',
            tags="loading"
        )
        
    def draw_progress_bar(self):
        """Draw modern progress bar"""
        bar_width = 400
        bar_height = 6
        bar_x = 100
        bar_y = 320
        
        # Background
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            fill='#1e293b',
            outline='#334155',
            width=1,
            tags="progress"
        )
        
        # Animated fill
        if self.progress < bar_width:
            self.progress += 2
        else:
            self.progress = 0
            
        # Gradient fill effect
        fill_width = self.progress
        for i in range(int(fill_width)):
            gradient = 1 - (i / bar_width) * 0.5
            color_value = int(96 + gradient * 159)
            color = f'#{color_value:02x}{165:02x}{250:02x}'
            
            self.canvas.create_line(
                bar_x + i, bar_y,
                bar_x + i, bar_y + bar_height,
                fill=color,
                tags="progress"
            )
            
        # Progress percentage
        percentage = int((self.progress / bar_width) * 100)
        self.canvas.create_text(
            300, bar_y + 20,
            text=f"Initializing System... {percentage}%",
            font=('Segoe UI', 9),
            fill='#64748b',
            tags="progress"
        )
        
    def animate(self):
        """Main animation loop"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw all elements
        self.draw_background_gradient()
        self.draw_particles()
        self.draw_logo()
        self.draw_loading_animation()
        self.draw_progress_bar()
        
        # Update animation frame
        self.animation_frame += 1
        
        # Continue animation
        self.splash.after(30, self.animate)
        
    def close(self):
        """Close splash screen"""
        self.splash.destroy()

class AnimatedApp:
    def __init__(self):
        # Show professional splash screen
        self.splash = ProfessionalSplash()
        
        # Start main app after animation
        self.main_app = None
        self.startup_timer = threading.Timer(4.0, self.launch_main_app)
        self.startup_timer.start()
        
    def launch_main_app(self):
        """Launch main application"""
        try:
            # Import and start main app
            from ui.fixed_compact_ui import FixedCompactUI
            
            # Close splash with fade effect
            self.splash.close()
            
            # Small delay before main app
            time.sleep(0.2)
            
            # Start main application
            self.main_app = FixedCompactUI()
            self.main_app.run()
            
        except Exception as e:
            print(f"Error launching main app: {e}")
            self.splash.close()

def main():
    """Main entry point"""
    app = AnimatedApp()
    
    # Run splash screen
    try:
        app.splash.splash.mainloop()
    except KeyboardInterrupt:
        app.splash.close()

if __name__ == "__main__":
    main()
