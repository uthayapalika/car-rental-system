# views/customer_booking_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers.customer_booking_controller import CustomerBookingController


class CustomerBookingPage:
    def __init__(self, parent, db, customer_id, vehicle_id, go_back_callback, update_status_callback):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.go_back = go_back_callback
        self.update_status = update_status_callback
        
        # Initialize customer booking controller
        self.controller = CustomerBookingController(db)
        
        # Vehicle data
        self.vehicle = None
        self.daily_rate = 0
        self.min_period = 1
        self.max_period = 30
        self.late_fee = 0
        
        # Form variables
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.end_date_var = tk.StringVar()
        self.days_var = tk.StringVar(value="0 days")
        self.subtotal_var = tk.StringVar(value="$0.00")
        self.discount_var = tk.StringVar(value="$0.00")
        self.grand_total_var = tk.StringVar(value="$0.00")
        
        self.setup_ui()
        self.load_vehicle_details()

    def setup_ui(self):
        """Setup the booking page UI with scrolling"""
        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        # Build UI in scrollable frame
        self.build_ui()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if hasattr(event, 'delta'):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def build_ui(self):
        """Build the UI in the scrollable frame"""
        # Back button
        back_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        back_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(
            back_frame,
            text="◀ Back to Vehicles",
            command=self.go_back,
            font=('Segoe UI', 10),
            bg='#95a5a6',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)
        
        # Title
        tk.Label(
            self.scrollable_frame,
            text="📝 Book Vehicle",
            font=('Segoe UI', 20, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 20))
        
        # Main content with two columns
        content_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Vehicle info
        left_frame = tk.Frame(content_frame, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.info_frame = tk.Frame(left_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=15)
        self.info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Vehicle info will be loaded here
        self.vehicle_info_label = tk.Label(
            self.info_frame,
            text="Loading vehicle details...",
            font=('Segoe UI', 12),
            fg='#7f8c8d',
            bg='white'
        )
        self.vehicle_info_label.pack(pady=20)
        
        # Right column - Booking form and calculation
        right_frame = tk.Frame(content_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Booking form
        form_frame = tk.Frame(right_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="Booking Details",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 15))
        
        # Start Date
        date_frame1 = tk.Frame(form_frame, bg='white')
        date_frame1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            date_frame1,
            text="Start Date:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.start_entry = tk.Entry(
            date_frame1,
            textvariable=self.start_date_var,
            font=('Segoe UI', 11),
            width=20
        )
        self.start_entry.pack(side=tk.LEFT)
        
        tk.Label(
            date_frame1,
            text="(YYYY-MM-DD)",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        # End Date
        date_frame2 = tk.Frame(form_frame, bg='white')
        date_frame2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            date_frame2,
            text="End Date:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.end_entry = tk.Entry(
            date_frame2,
            textvariable=self.end_date_var,
            font=('Segoe UI', 11),
            width=20
        )
        self.end_entry.pack(side=tk.LEFT)
        
        tk.Label(
            date_frame2,
            text="(YYYY-MM-DD)",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        # Special requests
        tk.Label(
            form_frame,
            text="Special Requests:",
            font=('Segoe UI', 11),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.notes_text = tk.Text(
            form_frame,
            font=('Segoe UI', 10),
            height=4,
            width=50
        )
        self.notes_text.pack(fill=tk.X, pady=(0, 10))
        
        # Cost breakdown
        cost_frame = tk.Frame(right_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=15)
        cost_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            cost_frame,
            text="Cost Breakdown",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        # Days
        days_row = tk.Frame(cost_frame, bg='white')
        days_row.pack(fill=tk.X, pady=2)
        tk.Label(days_row, text="Number of Days:", font=('Segoe UI', 11), bg='white', width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(days_row, textvariable=self.days_var, font=('Segoe UI', 11), bg='white').pack(side=tk.RIGHT)
        
        # Daily Rate
        rate_row = tk.Frame(cost_frame, bg='white')
        rate_row.pack(fill=tk.X, pady=2)
        tk.Label(rate_row, text="Daily Rate:", font=('Segoe UI', 11), bg='white', width=20, anchor='w').pack(side=tk.LEFT)
        self.rate_label = tk.Label(rate_row, text="$0.00", font=('Segoe UI', 11), bg='white')
        self.rate_label.pack(side=tk.RIGHT)
        
        # Subtotal
        subtotal_row = tk.Frame(cost_frame, bg='white')
        subtotal_row.pack(fill=tk.X, pady=2)
        tk.Label(subtotal_row, text="Subtotal:", font=('Segoe UI', 11), bg='white', width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(subtotal_row, textvariable=self.subtotal_var, font=('Segoe UI', 11), bg='white').pack(side=tk.RIGHT)
        
        # Discount
        discount_row = tk.Frame(cost_frame, bg='white')
        discount_row.pack(fill=tk.X, pady=2)
        tk.Label(discount_row, text="Discount (10% for 7+ days):", font=('Segoe UI', 11), bg='white', width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(discount_row, textvariable=self.discount_var, font=('Segoe UI', 11), fg='#27ae60', bg='white').pack(side=tk.RIGHT)
        
        # Separator
        separator = tk.Frame(cost_frame, bg='#ecf0f1', height=2)
        separator.pack(fill=tk.X, pady=5)
        
        # Grand Total
        total_row = tk.Frame(cost_frame, bg='white')
        total_row.pack(fill=tk.X, pady=5)
        tk.Label(total_row, text="Total Amount:", font=('Segoe UI', 13, 'bold'), bg='white', width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(total_row, textvariable=self.grand_total_var, font=('Segoe UI', 16, 'bold'), fg='#27ae60', bg='white').pack(side=tk.RIGHT)
        
        # Submit button frame (always at bottom)
        btn_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="📨 Submit Booking Request",
            command=self.submit_booking,
            font=('Segoe UI', 12, 'bold'),
            bg='#2ecc71',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.go_back,
            font=('Segoe UI', 11),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    def load_vehicle_details(self):
        """Load vehicle details from database"""
        self.vehicle = self.controller.get_vehicle_details(self.vehicle_id)
        
        if not self.vehicle:
            messagebox.showerror("Error", "Vehicle not found")
            self.go_back()
            return
        
        self.daily_rate = self.vehicle['daily_rate']
        self.min_period = self.vehicle['min_rent_period'] or 1
        self.max_period = self.vehicle['max_rent_period'] or 30
        self.late_fee = self.vehicle['late_fee_rate'] or 0
        
        # Update vehicle info display
        self.update_vehicle_info()
        
        # Update rate label
        self.rate_label.config(text=f"${self.daily_rate:.2f}")
        
        # Calculate total on date change
        self.start_date_var.trace_add("write", self.calculate_total)
        self.end_date_var.trace_add("write", self.calculate_total)

    def update_vehicle_info(self):
        """Update the vehicle information display"""
        # Clear existing info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Vehicle name
        tk.Label(
            self.info_frame,
            text=f"{self.vehicle['make']} {self.vehicle['model']}",
            font=('Segoe UI', 16, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w')
        
        # Details grid
        details = [
            (f"Year: {self.vehicle['year']}", f"License: {self.vehicle['license_plate']}"),
            (f"Fuel: {self.vehicle['fuel_type']}", f"Color: {self.vehicle['color'] or 'N/A'}"),
            (f"Daily Rate: ${self.vehicle['daily_rate']:.2f}", f"Category: {self.vehicle['category_name'] or 'N/A'}"),
            (f"Min Period: {self.min_period} days", f"Max Period: {self.max_period} days"),
            (f"Late Fee: ${self.late_fee:.2f}/day", f"Status: {self.vehicle['status'].capitalize()}")
        ]
        
        for row_data in details:
            row = tk.Frame(self.info_frame, bg='white')
            row.pack(fill=tk.X, pady=3)
            
            for i, text in enumerate(row_data):
                tk.Label(
                    row,
                    text=text,
                    font=('Segoe UI', 11),
                    fg='#2c3e50',
                    bg='white'
                ).pack(side=tk.LEFT, padx=(0, 40) if i == 0 else (0, 0))
        
        # Late fee warning
        if self.late_fee > 0:
            tk.Label(
                self.info_frame,
                text=f"⚠️ Late Return Fee: ${self.late_fee:.2f}/day",
                font=('Segoe UI', 10, 'bold'),
                fg='#e74c3c',
                bg='white'
            ).pack(anchor='w', pady=(5, 0))

    def calculate_total(self, *args):
        """Calculate total amount based on dates"""
        try:
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            
            if not start_str or not end_str:
                self.days_var.set("0 days")
                self.subtotal_var.set("$0.00")
                self.discount_var.set("$0.00")
                self.grand_total_var.set("$0.00")
                return
            
            start = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d")
            
            if end <= start:
                self.days_var.set("0 days")
                self.subtotal_var.set("$0.00")
                self.discount_var.set("$0.00")
                self.grand_total_var.set("$0.00")
                return
            
            days = (end - start).days
            
            # Validate min/max period
            if days < self.min_period:
                self.days_var.set(f"{days} days (⚠️ Min: {self.min_period})")
                self.subtotal_var.set("$0.00")
                self.discount_var.set("$0.00")
                self.grand_total_var.set("$0.00")
                return
            
            if days > self.max_period:
                self.days_var.set(f"{days} days (⚠️ Max: {self.max_period})")
                self.subtotal_var.set("$0.00")
                self.discount_var.set("$0.00")
                self.grand_total_var.set("$0.00")
                return
            
            # Calculate totals
            subtotal = days * self.daily_rate
            
            # Apply discount for long rentals (7+ days)
            discount = 0
            if days >= 7:
                discount = subtotal * 0.10  # 10% discount
                self.discount_var.set(f"-$ {discount:.2f}")
            else:
                self.discount_var.set("$0.00")
            
            grand_total = subtotal - discount
            
            self.days_var.set(f"{days} days")
            self.subtotal_var.set(f"$ {subtotal:.2f}")
            self.grand_total_var.set(f"$ {grand_total:.2f}")
            
        except ValueError:
            self.days_var.set("0 days")
            self.subtotal_var.set("$0.00")
            self.discount_var.set("$0.00")
            self.grand_total_var.set("$0.00")
        except Exception as e:
            print(f"Error calculating total: {e}")

    def submit_booking(self):
        """Submit booking request"""
        if not self.customer_id:
            messagebox.showerror("Error", "Customer profile not found. Please contact support.")
            return
        
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        
        if not start_date or not end_date:
            messagebox.showwarning("Validation", "Please select both start and end dates.")
            return
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if end <= start:
                messagebox.showwarning("Validation", "End date must be after start date.")
                return
            
            days = (end - start).days
            
            if days < self.min_period:
                messagebox.showwarning(
                    "Validation",
                    f"Minimum rental period is {self.min_period} day(s)."
                )
                return
            
            if days > self.max_period:
                messagebox.showwarning(
                    "Validation",
                    f"Maximum rental period is {self.max_period} day(s)."
                )
                return
            
            # Calculate final total with discount
            subtotal = days * self.daily_rate
            discount = subtotal * 0.10 if days >= 7 else 0
            total_amount = subtotal - discount
            
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Create booking using controller
            success, message, booking_ref = self.controller.create_booking(
                self.customer_id,
                self.vehicle_id,
                start_date,
                end_date,
                self.daily_rate,
                days,
                total_amount,
                notes
            )
            
            if success:
                messagebox.showinfo(
                    "Success",
                    f"✅ Booking request submitted successfully!\n\n"
                    f"Booking Reference: {booking_ref}\n"
                    f"Vehicle: {self.vehicle['make']} {self.vehicle['model']}\n"
                    f"Dates: {start_date} to {end_date}\n"
                    f"Days: {days}\n"
                    f"Daily Rate: ${self.daily_rate:.2f}\n"
                    f"Subtotal: ${subtotal:.2f}\n"
                    f"Discount: ${discount:.2f}\n"
                    f"Total: ${total_amount:.2f}\n\n"
                    "Your request has been sent to the admin for approval.\n"
                    "You will be notified once confirmed."
                )
                self.go_back()
            else:
                messagebox.showerror("Error", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not submit booking: {str(e)}")

    def update_status(self, message):
        """Update status bar"""
        if self.update_status:
            self.update_status(message)