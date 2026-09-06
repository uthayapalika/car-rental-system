# views/registration_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import os

class RegistrationView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.window = parent.winfo_toplevel()  # Get the main window

        # Registration needs more vertical space for all fields.
        self.window.title("Car Rental System - Registration")
        self.window.geometry("1250x800")
        self.window.minsize(1100, 700)
        self.window.resizable(True, True)
        self.window.configure(bg="#f0f0f0")
        self.frame = parent  # This is the frame passed from controller
        self.controller = controller
        
        # Configure frame
        self.frame.configure(bg='#f0f0f0')
        
        # Create main UI in the frame
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the registration interface"""

        main_frame = tk.Frame(self.frame, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Top bar
        top_bar = tk.Frame(main_frame, bg='#f0f0f0')
        top_bar.pack(fill=tk.X, pady=(0, 8))

        back_btn = tk.Button(
            top_bar,
            text="← Back to Login",
            command=self.go_to_login,
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        back_btn.pack(side=tk.LEFT)

        title_label = tk.Label(
            top_bar,
            text="📝 Create Your Account",
            font=('Segoe UI', 24, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        )
        title_label.pack(side=tk.LEFT, padx=25)

        subtitle_label = tk.Label(
            top_bar,
            text="Join us and start renting cars today",
            font=('Segoe UI', 11),
            fg='#7f8c8d',
            bg='#f0f0f0'
        )
        subtitle_label.pack(side=tk.LEFT)

        ttk.Separator(main_frame, orient='horizontal').pack(
            fill=tk.X, pady=(0, 10)
        )

        # Main content
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Give the form more room than the information panel.
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        left_frame = tk.Frame(
            content_frame,
            bg='white',
            relief=tk.RAISED,
            bd=1
        )
        left_frame.grid(
            row=0, column=0,
            sticky='nsew',
            padx=(0, 8)
        )

        right_frame = tk.Frame(
            content_frame,
            bg='#2c3e50',
            relief=tk.RAISED,
            bd=1
        )
        right_frame.grid(
            row=0, column=1,
            sticky='nsew',
            padx=(8, 0)
        )

        self.setup_form(left_frame)
        self.setup_info_panel(right_frame)

    def setup_form(self, parent):
        """Setup the registration form"""

        # Header
        form_header = tk.Frame(parent, bg='white')
        form_header.pack(fill=tk.X, padx=25, pady=(15, 8))

        tk.Label(
            form_header,
            text="Personal & Account Information",
            font=('Segoe UI', 16, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor=tk.W)

        # Scrollable area
        canvas_frame = tk.Frame(parent, bg='white')
        canvas_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=(0, 10)
        )

        canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient='vertical',
            command=canvas.yview
        )

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg='white')
        canvas_window = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor='nw'
        )

        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))

        def resize_inner_frame(event):
            canvas.itemconfigure(
                canvas_window,
                width=event.width
            )

        scrollable_frame.bind(
            '<Configure>',
            update_scroll_region
        )
        canvas.bind(
            '<Configure>',
            resize_inner_frame
        )

        # -------------------------
        # Personal information
        # -------------------------
        tk.Label(
            scrollable_frame,
            text="📋 Personal Information",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor=tk.W, padx=20, pady=(5, 8))

        self.create_form_field(
            scrollable_frame, "First Name *", "first_name"
        )
        self.create_form_field(
            scrollable_frame, "Last Name *", "last_name"
        )
        self.create_form_field(
            scrollable_frame, "Email Address *", "email"
        )
        self.create_form_field(
            scrollable_frame, "Phone Number *", "phone"
        )
        self.create_form_field(
            scrollable_frame, "Driver License *", "driver_license"
        )
        self.create_form_field(
            scrollable_frame, "Address", "address", height=3
        )

        # -------------------------
        # Account information
        # -------------------------
        tk.Label(
            scrollable_frame,
            text="🔐 Account Information",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor=tk.W, padx=20, pady=(15, 8))

        # These are deliberately stacked vertically.
        self.create_form_field(
            scrollable_frame,
            "👤 Username *",
            "username"
        )

        self.create_form_field(
            scrollable_frame,
            "🔑 Password *",
            "password",
            show="*"
        )

        self.create_form_field(
            scrollable_frame,
            "✓ Confirm Password *",
            "confirm_password",
            show="*"
        )

        tk.Label(
            scrollable_frame,
            text="🔒 Password must be at least 6 characters",
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='white'
        ).pack(anchor=tk.W, padx=20, pady=(2, 5))

        self.show_password_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            scrollable_frame,
            text="👁️ Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bg='white',
            fg='#2c3e50',
            font=('Segoe UI', 10),
            selectcolor='white'
        ).pack(anchor=tk.W, padx=20, pady=(0, 10))

        # Buttons
        button_frame = tk.Frame(scrollable_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=12)

        register_btn = tk.Button(
            button_frame,
            text="✅ Create Account",
            command=self.controller.register,
            font=('Segoe UI', 12, 'bold'),
            bg='#2ecc71',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        )
        register_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_fields,
            font=('Segoe UI', 11),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT)

        login_frame = tk.Frame(scrollable_frame, bg='white')
        login_frame.pack(pady=(5, 10))

        tk.Label(
            login_frame,
            text="Already have an account?",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT)

        login_link = tk.Label(
            login_frame,
            text=" Login Here",
            font=('Segoe UI', 10, 'bold'),
            fg='#3498db',
            bg='white',
            cursor='hand2'
        )
        login_link.pack(side=tk.LEFT)
        login_link.bind(
            '<Button-1>',
            lambda e: self.go_to_login()
        )

        self.status_label = tk.Label(
            scrollable_frame,
            text="",
            font=('Segoe UI', 10),
            bg='white'
        )
        self.status_label.pack(pady=(0, 10))

        self.bind_enter_keys()

        # Mouse wheel scrolling
        def mousewheel(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                'units'
            )

        canvas.bind_all('<MouseWheel>', mousewheel)

    def create_form_field(self, parent, label_text, field_name, show=None, height=None):
        """Create a form field with label and entry"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.X, pady=6)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=('Segoe UI', 10, 'bold'),
            fg='#34495e',
            bg='white'
        )
        label.pack(anchor=tk.W, pady=(0, 3))
        
        if height and height > 1:
            entry = tk.Text(
                frame,
                height=height,
                font=('Segoe UI', 10),
                relief=tk.SOLID,
                bd=1,
                bg='#f8f9fa',
                wrap=tk.WORD
            )
            entry.pack(fill=tk.X, ipady=5)
            setattr(self, f"{field_name}_entry", entry)
        else:
            entry = tk.Entry(
                frame,
                font=('Segoe UI', 10),
                relief=tk.SOLID,
                bd=1,
                bg='#f8f9fa'
            )
            if show:
                entry.config(show=show)
            entry.pack(fill=tk.X, ipady=6)
            setattr(self, f"{field_name}_entry", entry)

    def setup_info_panel(self, parent):
        """Setup the right info panel"""
        # Title
        title_label = tk.Label(
            parent,
            text="🚗 Car Rental",
            font=('Segoe UI', 32, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(60, 5))
        
        subtitle_label = tk.Label(
            parent,
            text="System",
            font=('Segoe UI', 24, 'bold'),
            fg='#3498db',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=(0, 30))
        
        separator = tk.Frame(parent, bg='#3498db', height=2, width=150)
        separator.pack(pady=10)
        
        # Benefits
        benefits = [
            "✓ Wide selection of vehicles",
            "✓ Competitive prices",
            "✓ Easy booking process",
            "✓ 24/7 customer support",
            "✓ Flexible rental options",
            "✓ Free cancellation"
        ]
        
        for benefit in benefits:
            benefit_label = tk.Label(
                parent,
                text=benefit,
                font=('Segoe UI', 12),
                fg='#ecf0f1',
                bg='#2c3e50'
            )
            benefit_label.pack(anchor=tk.W, padx=40, pady=8)
        
        # Footer
        footer_frame = tk.Frame(parent, bg='#2c3e50')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=30)
        
        footer_label = tk.Label(
            footer_frame,
            text="Join thousands of satisfied customers",
            font=('Segoe UI', 11),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        footer_label.pack()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
            self.confirm_password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            self.confirm_password_entry.config(show="*")

    def bind_enter_keys(self):
        """Bind Enter key to move to next field or submit"""
        fields = ['first_name', 'last_name', 'email', 'phone', 
                 'driver_license', 'address', 'username', 'password', 'confirm_password']
        
        for i, field in enumerate(fields):
            entry = getattr(self, f"{field}_entry", None)
            if entry:
                if i < len(fields) - 1:
                    next_field = getattr(self, f"{fields[i+1]}_entry", None)
                    if next_field:
                        entry.bind('<Return>', lambda e, nf=next_field: nf.focus())
                else:
                    entry.bind('<Return>', lambda e: self.controller.register())

    def get_registration_data(self):
        """Get all registration data from form"""
        return {
            'first_name': self.first_name_entry.get().strip(),
            'last_name': self.last_name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'driver_license_num': self.driver_license_entry.get().strip(),
            'address': self.address_entry.get("1.0", tk.END).strip(),
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get().strip(),
            'confirm_password': self.confirm_password_entry.get().strip()
        }

    def show_error(self, message):
        """Show error message"""
        self.status_label.config(text=f"❌ {message}", fg='#e74c3c')
        
    def show_success(self, message):
        """Show success message"""
        self.status_label.config(text=f"✅ {message}", fg='#27ae60')

    def set_loading(self):
        """Set loading state"""
        self.status_label.config(text="⏳ Processing...", fg='#3498db')

    def reset_loading(self):
        """Reset loading state"""
        self.status_label.config(text="")

    def clear_fields(self):
        """Clear all form fields"""
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.driver_license_entry.delete(0, tk.END)
        self.address_entry.delete("1.0", tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.status_label.config(text="")
        self.first_name_entry.focus()

    def go_to_login(self):
        """Go back to login"""
        # Call the controller's go_to_login which will destroy the registration frame
        if hasattr(self.controller, 'go_to_login'):
            self.controller.go_to_login()
        elif hasattr(self.controller, 'login_controller'):
            # If we have a reference to the login controller, use it
            self.controller.login_controller.close_registration()