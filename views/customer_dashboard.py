# views/customer_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Add parent directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views.customer_vehicles_page import CustomerVehiclesPage
from views.customer_bookings_page import CustomerBookingsPage


class CustomerDashboard:
    def __init__(self, parent, user, controller):
        self.parent = parent
        self.user = user
        self.controller = controller
        self.db = getattr(controller, 'db', None) or getattr(controller, 'model', None)
        self.time_label = None
        self.running = True
        
        # Get customer ID for this user
        self.customer_id = self.get_customer_id()
        
        # Store references
        self.current_page = None
        self.current_frame = None
        
        self.setup_ui()
        self.show_vehicles_page()

    def get_customer_id(self):
        """Get customer ID from user ID"""
        try:
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT customer_id FROM customers WHERE user_id = ?",
                    (self.user['id'],)
                )
                result = cursor.fetchone()
                cursor.close()
                if result:
                    return result['customer_id']
        except Exception as e:
            print(f"Error getting customer ID: {e}")
        return None

    def setup_ui(self):
        """Setup the customer dashboard interface"""
        self.parent.configure(bg='#f0f0f0')
        
        # Top header
        self.create_header()
        
        # Main content area - this will hold the current page
        self.content_frame = tk.Frame(self.parent, bg='#f0f0f0')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create header with user info"""
        header_frame = tk.Frame(self.parent, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🚗 Car Rental - Customer Portal",
            font=('Segoe UI', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Navigation buttons
        nav_frame = tk.Frame(header_frame, bg='#2c3e50')
        nav_frame.pack(side=tk.LEFT, padx=10)
        
        nav_buttons = [
            ("🚗 Available Vehicles", self.show_vehicles_page),
            ("📝 My Bookings", self.show_bookings_page),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=command,
                font=('Segoe UI', 10),
                bg='#34495e',
                fg='white',
                cursor='hand2',
                relief=tk.FLAT,
                padx=15,
                pady=8
            )
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#3d566e'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#34495e'))
        
        # User info - RIGHT side with logout
        user_frame = tk.Frame(header_frame, bg='#2c3e50')
        user_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Username
        user_label = tk.Label(
            user_frame,
            text=f"👤 {self.user['username']}",
            font=('Segoe UI', 12),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        user_label.pack(side=tk.LEFT, padx=10)
        
        # Logout button
        logout_btn = tk.Button(
            user_frame,
            text="🚪 Logout",
            command=self.controller.logout,
            font=('Segoe UI', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        logout_btn.pack(side=tk.LEFT, padx=10)
        logout_btn.bind('<Enter>', lambda e: logout_btn.config(bg='#c0392b'))
        logout_btn.bind('<Leave>', lambda e: logout_btn.config(bg='#e74c3c'))

    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.parent, bg='#ecf0f1', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.time_label = tk.Label(
            status_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c5d'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c5d'
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        self.update_time()

    def update_time(self):
        """Update time in status bar"""
        if not self.running:
            return
        
        try:
            if self.time_label and self.time_label.winfo_exists():
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.time_label.config(text=current_time)
                self.parent.after(1000, self.update_time)
        except (tk.TclError, AttributeError):
            self.running = False

    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_vehicles_page(self):
        """Show available vehicles page"""
        self.clear_content()
        self.current_page = "vehicles"
        self.current_frame = CustomerVehiclesPage(
            self.content_frame, 
            self.db, 
            self.customer_id,
            self.show_booking_page,
            self.update_status
        )

    def show_bookings_page(self):
        """Show my bookings page"""
        self.clear_content()
        self.current_page = "bookings"
        self.current_frame = CustomerBookingsPage(
            self.content_frame, 
            self.db, 
            self.customer_id,
            self.update_status,
            self.show_payment_page  # Pass the payment callback
        )

    def show_payment_page(self, booking_id, booking_ref, amount):
        """Show payment page for a booking"""
        self.clear_content()
        self.current_page = "payment"
        from views.customer_payment_page import CustomerPaymentPage
        self.current_frame = CustomerPaymentPage(
            self.content_frame,
            self.db,
            self.customer_id,
            booking_id,
            booking_ref,
            amount,
            self.show_bookings_page,
            self.update_status
        )

    def show_booking_page(self, vehicle_id):
        """Show booking page for selected vehicle"""
        self.clear_content()
        self.current_page = "booking"
        from views.customer_booking_page import CustomerBookingPage
        self.current_frame = CustomerBookingPage(
            self.content_frame, 
            self.db, 
            self.customer_id,
            vehicle_id,
            self.show_vehicles_page,
            self.update_status
        )

    def update_status(self, message):
        """Update status bar message"""
        try:
            if hasattr(self, 'status_label') and self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=message)
        except:
            pass

    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.parent.destroy()