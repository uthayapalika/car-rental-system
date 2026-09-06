# views/payment_view.py

import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime

from controllers.payment_controller import PaymentController


class PaymentView:

    def __init__(
        self,
        parent,
        db,
        user,
        dashboard_controller=None
    ):

        self.parent = parent
        self.db = db
        self.user = user
        self.dashboard_controller = dashboard_controller

        self.controller = PaymentController(db)

        self.editing_id = None

        # Check user role for permissions
        self.user_role = user.get('role', 'staff')
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'

        # Staff are view-only
        self.is_view_only = self.is_staff
        
        self.can_edit = self.is_admin or self.is_manager

        # ------------------------------------------------------
        # Variables
        # ------------------------------------------------------

        self.booking_var = tk.StringVar()

        self.payment_type_var = tk.StringVar(
            value="deposit"
        )

        self.amount_var = tk.StringVar()

        self.method_var = tk.StringVar(
            value="cash"
        )

        self.status_var = tk.StringVar(
            value="paid"
        )

        self.transaction_var = tk.StringVar()

        self.payment_date_var = tk.StringVar(
            value=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        self.notes_var = tk.StringVar()

        self.bookings = []

        self.setup_ui()

        self.load_bookings()

        self.load_payments()

    # ==========================================================
    # MAIN UI
    # ==========================================================

    def setup_ui(self):

        self.parent.configure(
            bg="#f0f0f0"
        )

        self.main_container = tk.Frame(
            self.parent,
            bg="#f0f0f0"
        )

        self.main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=20
        )

        # ------------------------------------------------------
        # Header
        # ------------------------------------------------------

        title_frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )

        title_frame.pack(
            fill=tk.X,
            pady=(0, 15)
        )

        # Title with view-only indicator for staff
        title_text = "💰 Payment Management"
        if self.is_view_only:
            title_text = "💰 Payment Management (View Only)"
            
        tk.Label(
            title_frame,
            text=title_text,
            font=("Segoe UI", 24, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0"
        ).pack(
            side=tk.LEFT
        )

        tk.Button(
            title_frame,
            text="◀ Back to Dashboard",
            command=self.go_back,
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(
            side=tk.RIGHT
        )

        # Stats
        stats_frame = tk.Frame(
            title_frame,
            bg="#f0f0f0"
        )
        stats_frame.pack(
            side=tk.RIGHT,
            padx=20
        )

        self.total_label = tk.Label(
            stats_frame,
            text="Total: 0",
            font=("Segoe UI", 12),
            fg="#7f8c8d",
            bg="#f0f0f0"
        )
        self.total_label.pack(
            side=tk.LEFT,
            padx=10
        )

        self.paid_label = tk.Label(
            stats_frame,
            text="Paid: 0",
            font=("Segoe UI", 12),
            fg="#27ae60",
            bg="#f0f0f0"
        )
        self.paid_label.pack(
            side=tk.LEFT,
            padx=10
        )

        self.pending_label = tk.Label(
            stats_frame,
            text="Pending: 0",
            font=("Segoe UI", 12),
            fg="#f39c12",
            bg="#f0f0f0"
        )
        self.pending_label.pack(
            side=tk.LEFT,
            padx=10
        )

        # View-only indicator for staff
        if self.is_view_only:
            view_only_label = tk.Label(
                stats_frame,
                text="🔒 View Only",
                font=("Segoe UI", 10, "bold"),
                fg="#e67e22",
                bg="#f0f0f0"
            )
            view_only_label.pack(
                side=tk.LEFT,
                padx=10
            )

        # ------------------------------------------------------
        # Search
        # ------------------------------------------------------

        search_frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )

        search_frame.pack(
            fill=tk.X,
            pady=(0, 10)
        )

        tk.Label(
            search_frame,
            text="Search:",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(
            side=tk.LEFT,
            padx=(0, 10)
        )

        self.search_var = tk.StringVar()

        self.search_var.trace_add(
            "write",
            self.on_search
        )

        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35,
            font=("Segoe UI", 11)
        ).pack(
            side=tk.LEFT
        )

        # ------------------------------------------------------
        # Buttons
        # ------------------------------------------------------

        button_frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )

        button_frame.pack(
            fill=tk.X,
            pady=(0, 10)
        )

        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.load_payments,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="📊 Export CSV",
            command=self.export_csv,
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="📊 Export Excel",
            command=self.export_excel,
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="📄 Export PDF",
            command=self.export_pdf,
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Add New Payment button - Only for admin and manager
        if self.can_edit:
            tk.Button(
                button_frame,
                text="➕ Add New Payment",
                command=self.clear_form,
                font=("Segoe UI", 10, "bold"),
                bg="#9b59b6",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=7
            ).pack(
                side=tk.LEFT,
                padx=5
            )

        # ------------------------------------------------------
        # Form - Only for admin and manager
        # ------------------------------------------------------

        if self.can_edit:
            self.create_form()
        else:
            # Show info message for view-only users
            info_frame = tk.Frame(
                self.main_container,
                bg="#f0f0f0"
            )
            info_frame.pack(
                fill=tk.X,
                pady=(0, 15)
            )
            
            info_label = tk.Label(
                info_frame,
                text="ℹ️ You are in View-Only mode. You can view and export payment data but cannot modify it.",
                font=("Segoe UI", 11),
                fg="#7f8c8d",
                bg="#f0f0f0"
            )
            info_label.pack()

        # ------------------------------------------------------
        # Table
        # ------------------------------------------------------

        self.create_table()

    # ==========================================================
    # FORM
    # ==========================================================

    def create_form(self):

        self.form_frame = tk.LabelFrame(
            self.main_container,
            text=" Add / Edit Payment ",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=10
        )

        self.form_frame.pack(
            fill=tk.X,
            pady=(0, 15)
        )

        # ------------------------------------------------------
        # Row 1
        # ------------------------------------------------------

        row1 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row1.pack(
            fill=tk.X,
            pady=5
        )

        tk.Label(
            row1,
            text="Booking *",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        self.booking_combo = ttk.Combobox(
            row1,
            textvariable=self.booking_var,
            width=45,
            state="readonly"
        )

        self.booking_combo.pack(
            side=tk.LEFT,
            padx=(5, 20)
        )

        tk.Label(
            row1,
            text="Payment Type *",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        ttk.Combobox(
            row1,
            textvariable=self.payment_type_var,
            values=[
                "deposit",
                "final",
                "refund"
            ],
            state="readonly",
            width=12
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Row 2
        # ------------------------------------------------------

        row2 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row2.pack(
            fill=tk.X,
            pady=5
        )

        tk.Label(
            row2,
            text="Amount ($) *",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        tk.Entry(
            row2,
            textvariable=self.amount_var,
            width=12
        ).pack(
            side=tk.LEFT,
            padx=(5, 20)
        )

        tk.Label(
            row2,
            text="Payment Method *",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        ttk.Combobox(
            row2,
            textvariable=self.method_var,
            values=[
                "cash",
                "card",
                "bank_transfer",
                "online"
            ],
            state="readonly",
            width=15
        ).pack(
            side=tk.LEFT,
            padx=(5, 20)
        )

        tk.Label(
            row2,
            text="Status",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        ttk.Combobox(
            row2,
            textvariable=self.status_var,
            values=[
                "pending",
                "paid",
                "failed",
                "refunded"
            ],
            state="readonly",
            width=12
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Row 3
        # ------------------------------------------------------

        row3 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row3.pack(
            fill=tk.X,
            pady=5
        )

        tk.Label(
            row3,
            text="Transaction Ref",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        tk.Entry(
            row3,
            textvariable=self.transaction_var,
            width=25
        ).pack(
            side=tk.LEFT,
            padx=(5, 20)
        )

        tk.Label(
            row3,
            text="Payment Date",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        tk.Entry(
            row3,
            textvariable=self.payment_date_var,
            width=20
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Row 4
        # ------------------------------------------------------

        row4 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row4.pack(
            fill=tk.X,
            pady=5
        )

        tk.Label(
            row4,
            text="Notes",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        tk.Entry(
            row4,
            textvariable=self.notes_var,
            width=60
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Buttons
        # ------------------------------------------------------

        row5 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row5.pack(
            fill=tk.X,
            pady=(8, 0)
        )

        self.save_button = tk.Button(
            row5,
            text="➕ Save Payment",
            command=self.save_payment,
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=7
        )

        self.save_button.pack(
            side=tk.RIGHT,
            padx=5
        )

        tk.Button(
            row5,
            text="Clear",
            command=self.clear_form,
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=7
        ).pack(
            side=tk.RIGHT,
            padx=5
        )

    # ==========================================================
    # TABLE
    # ==========================================================

    def create_table(self):

        frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        scroll_y = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL
        )

        scroll_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        scroll_x = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL
        )

        scroll_x.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        columns = (
            "ID",
            "Booking",
            "Customer",
            "Type",
            "Amount",
            "Method",
            "Status",
            "Transaction",
            "Date"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        for column in columns:

            self.tree.heading(
                column,
                text=column
            )

        widths = {
            "ID": 50,
            "Booking": 120,
            "Customer": 150,
            "Type": 100,
            "Amount": 100,
            "Method": 130,
            "Status": 100,
            "Transaction": 150,
            "Date": 160
        }

        for column, width in widths.items():

            self.tree.column(
                column,
                width=width
            )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True
        )

        scroll_y.config(
            command=self.tree.yview
        )

        scroll_x.config(
            command=self.tree.xview
        )

        # Bind events - different behavior based on role
        if self.can_edit:
            # Context menu - Only for admin and manager
            self.context_menu = tk.Menu(
                self.parent,
                tearoff=0
            )

            self.context_menu.add_command(
                label="✏️ Edit",
                command=self.edit_selected
            )

            self.context_menu.add_command(
                label="🗑️ Delete",
                command=self.delete_payment
            )

            self.tree.bind(
                "<Button-3>",
                self.show_context_menu
            )

            self.tree.bind(
                "<Double-1>",
                lambda event: self.edit_selected()
            )
        else:
            # View-only users can double-click to view details
            self.tree.bind(
                "<Double-1>",
                lambda event: self.view_payment_details()
            )

    # ==========================================================
    # VIEW DETAILS (for view-only users)
    # ==========================================================

    def view_payment_details(self):
        """Show payment details in a read-only dialog"""
        payment_id = self.get_selected_payment_id()
        if payment_id is None:
            return

        try:
            payment = self.controller.get_payment_by_id(payment_id)
            if not payment:
                messagebox.showerror("Error", "Payment not found.")
                return

            # Create details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Payment #{payment_id}")
            dialog.geometry("500x480")
            dialog.resizable(False, False)
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Set background
            dialog.configure(bg='#f0f0f0')

            # Header
            header_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="💰 Payment Details",
                font=("Segoe UI", 16, "bold"),
                fg="white",
                bg='#2c3e50'
            ).pack(pady=15)

            # Details
            details_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}".strip()
            
            status_colors = {
                'paid': '#27ae60',
                'pending': '#f39c12',
                'failed': '#e74c3c',
                'refunded': '#3498db'
            }
            status = payment.get('payment_status', 'pending')
            status_display = status.title()

            details = [
                ("Payment ID", str(payment.get('payment_id', ''))),
                ("Booking Reference", payment.get('booking_ref', 'N/A')),
                ("Customer", customer_name or 'N/A'),
                ("Payment Type", payment.get('payment_type', '').title()),
                ("Amount", f"${payment.get('amount', 0):.2f}"),
                ("Payment Method", payment.get('payment_method', '').replace('_', ' ').title()),
                ("Status", status_display),
                ("Transaction Ref", payment.get('transaction_reference', 'N/A') or 'N/A'),
                ("Payment Date", payment.get('payment_date', 'N/A') or 'N/A'),
                ("Notes", payment.get('notes', 'None') or 'None')
            ]

            for label, value in details:
                row_frame = tk.Frame(details_frame, bg='white')
                row_frame.pack(fill=tk.X, pady=3)
                
                tk.Label(
                    row_frame,
                    text=f"{label}:",
                    font=("Segoe UI", 11, "bold"),
                    bg='white',
                    fg='#2c3e50',
                    width=16,
                    anchor='w'
                ).pack(side=tk.LEFT)
                
                # Apply color to status
                if label == "Status":
                    status_color = status_colors.get(status, '#7f8c8d')
                    tk.Label(
                        row_frame,
                        text=value,
                        font=("Segoe UI", 11, "bold"),
                        bg='white',
                        fg=status_color
                    ).pack(side=tk.LEFT, padx=10)
                else:
                    tk.Label(
                        row_frame,
                        text=value,
                        font=("Segoe UI", 11),
                        bg='white',
                        fg='#34495e',
                        wraplength=350,
                        justify='left'
                    ).pack(side=tk.LEFT, padx=10)

            # Close button
            tk.Button(
                dialog,
                text="Close",
                command=dialog.destroy,
                font=("Segoe UI", 10, "bold"),
                bg="#3498db",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=30,
                pady=8
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load payment details:\n\n{str(e)}")

    # ==========================================================
    # LOAD BOOKINGS
    # ==========================================================

    def load_bookings(self):

        try:

            self.bookings = (
                self.controller.get_bookings()
            )

            values = []

            for booking in self.bookings:

                customer = (
                    f"{booking['first_name']} "
                    f"{booking['last_name']}"
                )

                values.append(
                    f"{booking['booking_id']}: "
                    f"{booking['booking_ref']} - "
                    f"{customer} - "
                    f"Balance ${booking['balance_amount']:.2f}"
                )

            # Only set if form exists
            if hasattr(self, 'booking_combo'):
                self.booking_combo[
                    'values'
                ] = values

                if values:
                    self.booking_combo.current(0)

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to load bookings:\n{e}"
            )

    # ==========================================================
    # LOAD PAYMENTS
    # ==========================================================

    def load_payments(self):

        try:

            for item in self.tree.get_children():

                self.tree.delete(item)

            payments = (
                self.controller.get_all_payments()
            )

            status_colors = {
                'paid': '#e8f5e9',
                'pending': '#fff3cd',
                'failed': '#ffebee',
                'refunded': '#e3f2fd'
            }

            for row in payments:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                status = (
                    row['payment_status']
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row['payment_id'],
                        row['booking_ref'],
                        customer,
                        row['payment_type'].title(),
                        f"${row['amount']:.2f}",
                        row['payment_method']
                        .replace(
                            "_",
                            " "
                        )
                        .title(),
                        status.title(),
                        row['transaction_reference']
                        or "",
                        row['payment_date']
                        or ""
                    ),
                    tags=(status,)
                )

            for status, color in status_colors.items():

                self.tree.tag_configure(
                    status,
                    background=color
                )

            # Update stats
            self.update_stats(payments)

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to load payments:\n{e}"
            )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def update_stats(self, payments=None):
        """Update statistics"""
        try:
            if payments is None:
                payments = self.controller.get_all_payments()

            total = len(payments) if payments else 0
            paid = 0
            pending = 0
            
            if payments:
                paid = sum(1 for p in payments if p.get('payment_status') == 'paid')
                pending = sum(1 for p in payments if p.get('payment_status') == 'pending')

            self.total_label.config(text=f"Total: {total}")
            self.paid_label.config(text=f"Paid: {paid}")
            self.pending_label.config(text=f"Pending: {pending}")

        except Exception:
            pass

    # ==========================================================
    # SEARCH
    # ==========================================================

    def on_search(self, *args):

        try:

            term = (
                self.search_var.get().strip()
            )

            if term:

                payments = (
                    self.controller.search_payments(
                        term
                    )
                )

            else:

                payments = (
                    self.controller.get_all_payments()
                )

            for item in self.tree.get_children():

                self.tree.delete(item)

            for row in payments:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row['payment_id'],
                        row['booking_ref'],
                        customer,
                        row['payment_type'].title(),
                        f"${row['amount']:.2f}",
                        row['payment_method']
                        .replace(
                            "_",
                            " "
                        )
                        .title(),
                        row['payment_status'].title(),
                        row['transaction_reference']
                        or "",
                        row['payment_date']
                        or ""
                    ),
                    tags=(
                        row['payment_status'],
                    )
                )

        except Exception as e:

            print(
                "Payment search error:",
                e
            )

    # ==========================================================
    # SAVE - Only for admin and manager
    # ==========================================================

    def save_payment(self):
        """Save payment - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify payments.")
            return

        booking_text = (
            self.booking_combo.get()
        )

        if not booking_text:

            messagebox.showwarning(
                "Validation",
                "Please select a booking."
            )

            return

        booking_id = int(
            booking_text.split(":")[0]
        )

        data = {
            'booking_id':
                booking_id,

            'payment_type':
                self.payment_type_var.get(),

            'amount':
                self.amount_var.get().strip(),

            'payment_method':
                self.method_var.get(),

            'payment_status':
                self.status_var.get(),

            'transaction_reference':
                self.transaction_var.get().strip(),

            'payment_date':
                self.payment_date_var.get().strip(),

            'notes':
                self.notes_var.get().strip()
        }

        try:

            if self.editing_id is not None:

                result = (
                    self.controller.update_payment(
                        self.editing_id,
                        data
                    )
                )

            else:

                result = (
                    self.controller.add_payment(
                        data
                    )
                )

            if result['success']:

                messagebox.showinfo(
                    "Success",
                    result['message']
                )

                self.clear_form()

                self.load_bookings()

                self.load_payments()

            else:

                messagebox.showerror(
                    "Error",
                    result['message']
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to save payment:\n\n{e}"
            )

    # ==========================================================
    # CLEAR - Only for admin and manager
    # ==========================================================

    def clear_form(self):
        """Clear form - only for admin and manager"""
        if not self.can_edit:
            return

        self.editing_id = None

        self.amount_var.set("")

        self.payment_type_var.set(
            "deposit"
        )

        self.method_var.set(
            "cash"
        )

        self.status_var.set(
            "paid"
        )

        self.transaction_var.set("")

        self.payment_date_var.set(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        self.notes_var.set("")

        if hasattr(self, 'booking_combo') and self.booking_combo['values']:
            self.booking_combo.current(0)

        if hasattr(self, 'save_button'):
            self.save_button.config(
                text="➕ Save Payment"
            )

    # ==========================================================
    # SELECTED ID
    # ==========================================================

    def get_selected_payment_id(self):

        selection = self.tree.selection()

        if not selection:

            messagebox.showwarning(
                "No Selection",
                "Please select a payment first."
            )

            return None

        item = self.tree.item(
            selection[0]
        )

        return item['values'][0]

    # ==========================================================
    # EDIT - Only for admin and manager
    # ==========================================================

    def edit_selected(self):
        """Edit selected payment - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to edit payments.")
            return

        payment_id = (
            self.get_selected_payment_id()
        )

        if payment_id is None:
            return

        payment = (
            self.controller.get_payment_by_id(
                payment_id
            )
        )

        if not payment:

            messagebox.showerror(
                "Error",
                "Payment not found."
            )

            return

        self.editing_id = payment_id

        # Booking
        for i, booking in enumerate(
            self.bookings
        ):

            if (
                booking['booking_id']
                == payment['booking_id']
            ):

                self.booking_combo.current(i)

                break

        self.payment_type_var.set(
            payment['payment_type']
        )

        self.amount_var.set(
            str(payment['amount'])
        )

        self.method_var.set(
            payment['payment_method']
        )

        self.status_var.set(
            payment['payment_status']
        )

        self.transaction_var.set(
            payment['transaction_reference']
            or ""
        )

        self.payment_date_var.set(
            payment['payment_date']
            or ""
        )

        self.notes_var.set(
            payment['notes']
            or ""
        )

        self.save_button.config(
            text="✏️ Update Payment"
        )

    # ==========================================================
    # CONTEXT MENU - Only for admin and manager
    # ==========================================================

    def show_context_menu(self, event):
        """Show context menu - only for admin and manager"""
        if not self.can_edit:
            return

        item = self.tree.identify_row(
            event.y
        )

        if item:

            self.tree.selection_set(
                item
            )

            self.context_menu.post(
                event.x_root,
                event.y_root
            )

    # ==========================================================
    # DELETE - Only for admin and manager
    # ==========================================================

    def delete_payment(self):
        """Delete payment - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to delete payments.")
            return

        payment_id = (
            self.get_selected_payment_id()
        )

        if payment_id is None:
            return

        payment = (
            self.controller.get_payment_by_id(
                payment_id
            )
        )

        if not payment:
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            (
                f"Delete payment "
                f"#{payment_id}?\n\n"
                "This will recalculate the booking balance."
            )
        ):

            return

        result = (
            self.controller.delete_payment(
                payment_id
            )
        )

        if result['success']:

            messagebox.showinfo(
                "Success",
                result['message']
            )

            self.clear_form()

            self.load_bookings()

            self.load_payments()

        else:

            messagebox.showerror(
                "Error",
                result['message']
            )

    # ==========================================================
    # BACK
    # ==========================================================

    def go_back(self):

        for widget in (
            self.parent.winfo_children()
        ):

            widget.destroy()

        if self.dashboard_controller:

            from views.main_dashboard import MainDashboard

            MainDashboard(
                self.parent,
                self.user,
                self.dashboard_controller
            )

    # ==========================================================
    # EXPORT - All users can export
    # ==========================================================

    def export_csv(self):

        payments = (
            self.controller.get_all_payments()
        )

        if not payments:

            messagebox.showwarning(
                "No Data",
                "No payments to export."
            )

            return

        self.controller.export_to_csv(
            payments
        )

    def export_excel(self):

        payments = (
            self.controller.get_all_payments()
        )

        if not payments:

            messagebox.showwarning(
                "No Data",
                "No payments to export."
            )

            return

        self.controller.export_to_excel(
            payments
        )

    def export_pdf(self):

        payments = (
            self.controller.get_all_payments()
        )

        if not payments:

            messagebox.showwarning(
                "No Data",
                "No payments to export."
            )

            return

        self.controller.export_to_pdf(
            payments
        )