# views/customer_registration_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CustomerRegistrationView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.window = parent
        self.controller = controller
        
        # Configure window
        self.window.title("Customer Registration")
        self.window.geometry("1100x750")
        self.window.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
        
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = 1100
        height = 750
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Setup the customer registration interface"""
        # Main container
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="👤 Customer Registration",
            font=('Arial', 24, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create two columns: form and table
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Registration Form
        left_panel = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel - Customer List
        right_panel = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Setup form in left panel
        self.setup_form(left_panel)
        
        # Setup table in right panel
        self.setup_table(right_panel)
        
        # Load existing customers
        self.controller.load_customers()

    def setup_form(self, parent):
        """Setup the registration form"""
        # Form title
        form_title = tk.Label(
            parent,
            text="Register New Customer",
            font=('Arial', 18, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        form_title.pack(pady=(20, 15))
        
        # Form frame
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Create two columns for form fields
        left_col = tk.Frame(form_frame, bg='white')
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_col = tk.Frame(form_frame, bg='white')
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Left column - Personal Information
        tk.Label(left_col, text="Personal Information", font=('Arial', 14, 'bold'), 
                bg='white', fg='#2c3e50').pack(anchor=tk.W, pady=(0, 10))
        
        self.create_form_field(left_col, "First Name *:", "first_name")
        self.create_form_field(left_col, "Last Name *:", "last_name")
        self.create_form_field(left_col, "Email *:", "email")
        self.create_form_field(left_col, "Phone *:", "phone")
        self.create_form_field(left_col, "Driver License *:", "driver_license")
        self.create_form_field(left_col, "Address:", "address", height=3)
        
        # Right column - Account Information
        tk.Label(right_col, text="Account Information", font=('Arial', 14, 'bold'), 
                bg='white', fg='#2c3e50').pack(anchor=tk.W, pady=(0, 10))
        
        self.create_form_field(right_col, "Username *:", "username")
        self.create_form_field(right_col, "Password *:", "password", show="•")
        self.create_form_field(right_col, "Confirm Password *:", "confirm_password", show="•")
        
        # Password requirements
        requirements = tk.Label(
            right_col,
            text="Password must be at least 6 characters",
            font=('Arial', 9),
            fg='#7f8c8d',
            bg='white'
        )
        requirements.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        
        register_btn = tk.Button(
            button_frame,
            text="Register Customer",
            command=self.controller.register_customer,
            font=('Arial', 12, 'bold'),
            bg='#2ecc71',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_fields,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(
            parent,
            text="",
            font=('Arial', 11),
            bg='white'
        )
        self.status_label.pack(pady=(0, 20))

    def create_form_field(self, parent, label_text, field_name, show=None, height=None):
        """Create a form field with label and entry"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=('Arial', 11),
            fg='#2c3e50',
            bg='white'
        )
        label.pack(anchor=tk.W, pady=(0, 2))
        
        if height and height > 1:
            # Text widget for multi-line (address)
            entry = tk.Text(
                frame,
                height=height,
                font=('Arial', 11),
                relief=tk.SOLID,
                bd=1,
                wrap=tk.WORD
            )
            entry.pack(fill=tk.X)
            setattr(self, f"{field_name}_entry", entry)
        else:
            # Entry widget
            entry = tk.Entry(
                frame,
                font=('Arial', 11),
                relief=tk.SOLID,
                bd=1
            )
            if show:
                entry.config(show=show)
            entry.pack(fill=tk.X, ipady=5)
            setattr(self, f"{field_name}_entry", entry)

    def setup_table(self, parent):
        """Setup the customer table"""
        # Table title
        table_title = tk.Label(
            parent,
            text="Registered Customers",
            font=('Arial', 18, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        table_title.pack(pady=(20, 10))
        
        # Search bar
        search_frame = tk.Frame(parent, bg='white')
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", bg='white', font=('Arial', 11)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.search_customers)
        
        refresh_btn = tk.Button(
            search_frame,
            text="🔄 Refresh",
            command=self.controller.load_customers,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Create Treeview for customers
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create table
        columns = ('ID', 'First Name', 'Last Name', 'Email', 'Phone', 
                  'License', 'Address', 'Created', 'Username')
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Configure column headings and widths
        column_widths = {
            'ID': 50,
            'First Name': 120,
            'Last Name': 120,
            'Email': 150,
            'Phone': 110,
            'License': 110,
            'Address': 150,
            'Created': 130,
            'Username': 110
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='w' if col != 'ID' else 'center')
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to view details
        self.tree.bind('<Double-Button-1>', self.on_customer_double_click)
        
        # Delete button
        delete_btn = tk.Button(
            parent,
            text="🗑️ Delete Selected",
            command=self.delete_selected_customer,
            font=('Arial', 11),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        delete_btn.pack(pady=(0, 20))

    def get_customer_data(self):
        """Get customer data from form fields"""
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

    def display_customers(self, customers):
        """Display customers in the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert customers
        for customer in customers:
            self.tree.insert('', 'end', values=(
                customer['customer_id'],
                customer['first_name'],
                customer['last_name'],
                customer['email'],
                customer['phone'],
                customer['driver_license_num'],
                customer['address'][:30] + '...' if len(customer.get('address', '')) > 30 else customer.get('address', ''),
                customer['created_at'],
                customer['username']
            ))

    def search_customers(self, event):
        """Search customers based on input"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.controller.load_customers()
            return
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if any(search_term in str(v).lower() for v in values[1:5]):
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)

    def on_customer_double_click(self, event):
        """Handle double-click on customer row"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item)['values']
            
            messagebox.showinfo(
                "Customer Details",
                f"ID: {values[0]}\n"
                f"Name: {values[1]} {values[2]}\n"
                f"Email: {values[3]}\n"
                f"Phone: {values[4]}\n"
                f"License: {values[5]}\n"
                f"Address: {values[6]}\n"
                f"Created: {values[7]}\n"
                f"Username: {values[8]}"
            )

    def delete_selected_customer(self):
        """Delete selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a customer to delete.")
            return
        
        item = selected[0]
        values = self.tree.item(item)['values']
        customer_id = values[0]
        
        self.controller.delete_customer(customer_id)

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