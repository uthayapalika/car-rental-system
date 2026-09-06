# views/login_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from version import APP_VERSION
class LoginView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.window = parent
        self.controller = controller
        self.frame = None
        
        # Configure window
        self.window.title(f"Car Rental System - Version {APP_VERSION}") 
        self.window.geometry("1000x650")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        
        # Center the window
        self.center_window()
        
        # Create main frame
        self.setup_ui()
        
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = 1000
        height = 650
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Setup the login interface"""
        # Main frame for login
        self.frame = tk.Frame(self.window, bg='#f0f0f0')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame = self.frame
        
        # Left panel (login form)
        left_frame = tk.Frame(main_frame, bg='white', width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_frame.pack_propagate(False)
        
        # Right panel (branding)
        right_frame = tk.Frame(main_frame, bg='#2c3e50', width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        
        # Setup right panel
        self.setup_right_panel(right_frame)
        
        # Setup left panel
        self.setup_left_panel(left_frame)

    def setup_right_panel(self, frame):
        """Setup the right panel with branding"""
        # Welcome text
        welcome_label = tk.Label(
            frame,
            text="🚗",
            font=('Segoe UI', 48),
            fg='white',
            bg='#2c3e50'
        )
        welcome_label.pack(pady=(80, 10))
        
        title_label = tk.Label(
            frame,
            text="Car Rental",
            font=('Segoe UI', 32, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            frame,
            text="System",
            font=('Segoe UI', 24, 'bold'),
            fg='#3498db',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=(0, 20))
        
        separator = tk.Frame(frame, bg='#3498db', height=2, width=200)
        separator.pack(pady=10)
        
        desc_label = tk.Label(
            frame,
            text="Efficient Car Rental Management",
            font=('Segoe UI', 14),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        desc_label.pack(pady=(20, 5))
        
        desc2_label = tk.Label(
            frame,
            text="Secure • Fast • Reliable",
            font=('Segoe UI', 12),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        desc2_label.pack()
        
        # Features
        features_frame = tk.Frame(frame, bg='#2c3e50')
        features_frame.pack(pady=40)
        
        features = [
            "✓ Wide selection of vehicles",
            "✓ Competitive prices",
            "✓ Easy booking process",
            "✓ 24/7 customer support"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=('Segoe UI', 11),
                fg='#ecf0f1',
                bg='#2c3e50'
            )
            feature_label.pack(anchor=tk.W, pady=4)

    def setup_left_panel(self, frame):
        """Setup the left panel with login form"""
        # Logo or icon
        icon_label = tk.Label(
            frame,
            text="🔐",
            font=('Segoe UI', 40),
            bg='white'
        )
        icon_label.pack(pady=(40, 10))
        
        title_label = tk.Label(
            frame,
            text="Welcome Back!",
            font=('Segoe UI', 28, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        title_label.pack(pady=(5, 5))
        
        subtitle_label = tk.Label(
            frame,
            text="Please login to your account",
            font=('Segoe UI', 12),
            fg='#7f8c8d',
            bg='white'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = tk.Frame(frame, bg='white')
        form_frame.pack(pady=10, padx=50, fill=tk.X)
        
        # Username
        username_label = tk.Label(
            form_frame,
            text="Username",
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 12),
            bg='#f8f9fa',
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor='#3498db',
            highlightbackground='#ddd'
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Password
        password_label = tk.Label(
            form_frame,
            text="Password",
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 12),
            bg='#f8f9fa',
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor='#3498db',
            highlightbackground='#ddd',
            show="•"
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 10), ipady=10)
        
        # Show password
        self.show_password_var = tk.BooleanVar()
        show_check = tk.Checkbutton(
            form_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bg='white',
            fg='#2c3e50',
            font=('Segoe UI', 10),
            selectcolor='white'
        )
        show_check.pack(anchor=tk.W, pady=(0, 20))
        
        # ERROR MESSAGE LABEL (NO POPUP)
        self.error_label = tk.Label(
            form_frame,
            text="",
            font=('Segoe UI', 11, 'bold'),
            fg='#e74c3c',
            bg='white',
            wraplength=350,
            height=2
        )
        self.error_label.pack(fill=tk.X, pady=(0, 10))
        
        # Login button
        self.login_button = tk.Button(
            form_frame,
            text="Login",
            command=self.handle_login,
            font=('Segoe UI', 14, 'bold'),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=12
        )
        self.login_button.pack(fill=tk.X, pady=(0, 10))
        
        # Hover effects
        self.login_button.bind('<Enter>', lambda e: self.login_button.config(bg='#2980b9'))
        self.login_button.bind('<Leave>', lambda e: self.login_button.config(bg='#3498db'))
        
        # Register link
        register_frame = tk.Frame(form_frame, bg='white')
        register_frame.pack(pady=15)
        
        register_label = tk.Label(
            register_frame,
            text="Don't have an account?",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white'
        )
        register_label.pack(side=tk.LEFT)
        
        register_link = tk.Label(
            register_frame,
            text=" Register Here",
            font=('Segoe UI', 10, 'bold'),
            fg='#3498db',
            bg='white',
            cursor='hand2'
        )
        register_link.pack(side=tk.LEFT)
        register_link.bind('<Button-1>', lambda e: self.controller.open_registration())
        register_link.bind('<Enter>', lambda e: register_link.config(fg='#2980b9'))
        register_link.bind('<Leave>', lambda e: register_link.config(fg='#3498db'))
        
        # Status label for success messages
        self.status_label = tk.Label(
            frame,
            text="",
            font=('Segoe UI', 10),
            fg='#27ae60',
            bg='white'
        )
        self.status_label.pack(pady=(5, 0))
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def handle_login(self):
        """Handle login with validation"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Clear previous errors
        self.clear_errors()
        
        # Validate fields
        if not username:
            self.show_error("⚠️ Username is required")
            self.username_entry.focus()
            self.username_entry.config(highlightbackground='#e74c3c')
            return
        
        if not password:
            self.show_error("⚠️ Password is required")
            self.password_entry.focus()
            self.password_entry.config(highlightbackground='#e74c3c')
            return
        
        # Reset highlight
        self.username_entry.config(highlightbackground='#ddd')
        self.password_entry.config(highlightbackground='#ddd')
        
        # Call controller login
        self.controller.login()

    def show_error(self, message):
        """Show error message (NO POPUP)"""
        self.error_label.config(text=message, fg='#e74c3c')
        self.status_label.config(text="")
        
        # Flash the error label for attention
        self.flash_error_label()
        
    def flash_error_label(self):
        """Flash the error label for attention"""
        def flash():
            current_bg = self.error_label.cget('bg')
            if current_bg == 'white':
                self.error_label.config(bg='#ffe6e6')
            else:
                self.error_label.config(bg='white')
        
        # Flash twice
        self.error_label.after(100, flash)
        self.error_label.after(300, flash)
        self.error_label.after(500, flash)
        
    def show_success(self, message):
        """Show success message"""
        self.status_label.config(text=f"✅ {message}", fg='#27ae60')
        self.error_label.config(text="")

    def clear_errors(self):
        """Clear all error messages"""
        self.error_label.config(text="", bg='white')
        self.status_label.config(text="")
        self.username_entry.config(highlightbackground='#ddd')
        self.password_entry.config(highlightbackground='#ddd')

    def set_loading(self):
        """Set loading state"""
        self.login_button.config(state=tk.DISABLED, text="Logging in...")
        self.status_label.config(text="⏳ Processing...", fg='#3498db')
        self.error_label.config(text="", bg='white')

    def reset_loading(self):
        """Reset loading state"""
        self.login_button.config(state=tk.NORMAL, text="Login")
        self.status_label.config(text="")
        
    def get_credentials(self):
        """Get username and password"""
        return self.username_entry.get().strip(), self.password_entry.get().strip()

    def clear_fields(self):
        """Clear input fields"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()
        self.clear_errors()
    
    def hide(self):
        """Hide the login frame"""
        if self.frame:
            self.frame.pack_forget()
    
    def show(self):
        """Show the login frame"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)