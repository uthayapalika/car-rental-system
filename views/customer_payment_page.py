# views/customer_payment_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import secrets
import string


class CustomerPaymentPage:
    def __init__(self, parent, db, customer_id, booking_id, booking_ref, amount, go_back_callback, update_status_callback):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.booking_id = booking_id
        self.booking_ref = booking_ref
        self.amount = amount
        self.go_back = go_back_callback
        self.update_status = update_status_callback
        
        # Payment type selection
        self.payment_type_var = tk.StringVar(value="deposit")
        
        # Card details
        self.card_number_var = tk.StringVar()
        self.card_holder_var = tk.StringVar()
        self.expiry_month_var = tk.StringVar()
        self.expiry_year_var = tk.StringVar()
        self.cvv_var = tk.StringVar()
        
        self.setup_ui()

    def generate_transaction_ref(self):
        """Generate a unique transaction reference"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"TXN-{date_part}-{random_part}"

    def setup_ui(self):
        """Setup the payment page UI"""
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
            text="◀ Back to Bookings",
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
            text="💳 Make Payment",
            font=('Segoe UI', 24, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 20))
        
        # Booking info
        info_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            info_frame,
            text="Booking Information",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        info_details = [
            f"Booking Reference: {self.booking_ref}",
            f"Total Amount: ${self.amount:.2f}",
            f"Booking ID: #{self.booking_id}"
        ]
        
        for detail in info_details:
            tk.Label(
                info_frame,
                text=detail,
                font=('Segoe UI', 11),
                fg='#34495e',
                bg='white'
            ).pack(anchor='w', pady=2)
        
        # Payment form
        form_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="Payment Details",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 15))
        
        # Payment Type
        type_frame = tk.Frame(form_frame, bg='white')
        type_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            type_frame,
            text="Payment Type:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Radio buttons for payment type
        payment_types = [
            ("Deposit", "deposit"),
            ("Full Payment", "final")
        ]
        
        for text, value in payment_types:
            tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.payment_type_var,
                value=value,
                font=('Segoe UI', 10),
                bg='white',
                command=self.update_amount
            ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Amount to pay
        amount_frame = tk.Frame(form_frame, bg='white')
        amount_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            amount_frame,
            text="Amount to Pay:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.payment_amount_var = tk.StringVar(value=f"${self.amount:.2f}")
        tk.Label(
            amount_frame,
            textvariable=self.payment_amount_var,
            font=('Segoe UI', 14, 'bold'),
            fg='#27ae60',
            bg='white'
        ).pack(side=tk.LEFT)
        
        # Separator
        separator = tk.Frame(form_frame, bg='#ecf0f1', height=2)
        separator.pack(fill=tk.X, pady=10)
        
        tk.Label(
            form_frame,
            text="Card Details",
            font=('Segoe UI', 12, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(5, 10))
        
        # Card Number
        card_frame = tk.Frame(form_frame, bg='white')
        card_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            card_frame,
            text="Card Number:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            card_frame,
            textvariable=self.card_number_var,
            font=('Segoe UI', 11),
            width=25,
            show="*"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            card_frame,
            text="(16 digits)",
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT)
        
        # Card Holder
        holder_frame = tk.Frame(form_frame, bg='white')
        holder_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            holder_frame,
            text="Card Holder:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            holder_frame,
            textvariable=self.card_holder_var,
            font=('Segoe UI', 11),
            width=30
        ).pack(side=tk.LEFT)
        
        # Expiry Date
        expiry_frame = tk.Frame(form_frame, bg='white')
        expiry_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            expiry_frame,
            text="Expiry Date:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Month dropdown
        months = [f"{i:02d}" for i in range(1, 13)]
        self.expiry_month_combo = ttk.Combobox(
            expiry_frame,
            textvariable=self.expiry_month_var,
            font=('Segoe UI', 10),
            width=5,
            values=months,
            state='readonly'
        )
        self.expiry_month_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Year dropdown
        current_year = datetime.now().year
        years = [str(i) for i in range(current_year, current_year + 11)]
        self.expiry_year_combo = ttk.Combobox(
            expiry_frame,
            textvariable=self.expiry_year_var,
            font=('Segoe UI', 10),
            width=7,
            values=years,
            state='readonly'
        )
        self.expiry_year_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            expiry_frame,
            text="(MM / YYYY)",
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT)
        
        # CVV
        cvv_frame = tk.Frame(form_frame, bg='white')
        cvv_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            cvv_frame,
            text="CVV:",
            font=('Segoe UI', 11),
            bg='white',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            cvv_frame,
            textvariable=self.cvv_var,
            font=('Segoe UI', 11),
            width=10,
            show="*"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            cvv_frame,
            text="(3-4 digits)",
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT)
        
        # Submit button
        btn_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="💳 Pay Now",
            command=self.process_payment,
            font=('Segoe UI', 12, 'bold'),
            bg='#2ecc71',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=40,
            pady=12
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
            pady=12
        ).pack(side=tk.LEFT, padx=5)

    def update_amount(self):
        """Update amount based on payment type"""
        if self.payment_type_var.get() == "deposit":
            # For deposit, pay 20% of total
            deposit = self.amount * 0.20
            self.payment_amount_var.set(f"${deposit:.2f}")
        else:
            self.payment_amount_var.set(f"${self.amount:.2f}")

    def process_payment(self):
        """Process the payment"""
        # Validate card details
        card_number = self.card_number_var.get().strip()
        card_holder = self.card_holder_var.get().strip()
        expiry_month = self.expiry_month_var.get()
        expiry_year = self.expiry_year_var.get()
        cvv = self.cvv_var.get().strip()
        
        if not card_number or len(card_number) < 16:
            messagebox.showwarning("Validation", "Please enter a valid 16-digit card number.")
            return
        
        if not card_holder:
            messagebox.showwarning("Validation", "Please enter the card holder name.")
            return
        
        if not expiry_month or not expiry_year:
            messagebox.showwarning("Validation", "Please select the expiry date.")
            return
        
        if not cvv or len(cvv) < 3:
            messagebox.showwarning("Validation", "Please enter a valid CVV.")
            return
        
        try:
            # Get amount to pay
            amount_str = self.payment_amount_var.get().replace('$', '').strip()
            amount = float(amount_str)
            
            # Generate transaction reference
            transaction_ref = self.generate_transaction_ref()
            
            # Get payment method and type
            payment_type = self.payment_type_var.get()
            payment_method = "card"  # Since we're using card
            
            # Insert payment
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn is None:
                messagebox.showerror("Error", "Database connection not available.")
                return
            
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO payments (
                    booking_id,
                    payment_type,
                    amount,
                    payment_method,
                    payment_status,
                    transaction_reference,
                    payment_date,
                    notes,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.booking_id,
                payment_type,
                amount,
                payment_method,
                'paid',
                transaction_ref,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"Card payment for booking {self.booking_ref}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            cursor.close()
            
            messagebox.showinfo(
                "Success",
                f"✅ Payment successful!\n\n"
                f"Transaction Reference: {transaction_ref}\n"
                f"Booking: {self.booking_ref}\n"
                f"Amount Paid: ${amount:.2f}\n"
                f"Payment Type: {payment_type.upper()}\n\n"
                "Thank you for your payment!"
            )
            
            self.go_back()
            
        except Exception as e:
            messagebox.showerror("Error", f"Payment failed: {str(e)}")