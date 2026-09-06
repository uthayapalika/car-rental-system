# views/booking_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers.booking_controller import BookingController


class BookingView:
    def __init__(self, parent, db, user, dashboard_controller=None):
        self.parent = parent
        self.db = db
        self.user = user
        self.dashboard_controller = dashboard_controller

        # Controller
        self.controller = BookingController(db)

        # Editing state
        self.editing_id = None

        # Check user role for permissions
        self.user_role = user.get('role', 'staff')
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'

        # Staff are view-only
        self.is_view_only = self.is_staff
        
        self.can_edit = self.is_admin or self.is_manager
        
        # Admin can approve/reject bookings
        self.can_approve = self.is_admin

        # Form variables
        self.booking_ref_var = tk.StringVar()
        self.customer_id_var = tk.StringVar()
        self.vehicle_id_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.pickup_location_var = tk.StringVar()
        self.dropoff_location_var = tk.StringVar()
        self.daily_rate_var = tk.StringVar()
        self.total_days_var = tk.StringVar()
        self.total_amount_var = tk.StringVar()
        self.deposit_amount_var = tk.StringVar()
        self.status_var = tk.StringVar(value="pending")
        self.notes_var = tk.StringVar()

        # Search
        self.search_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="all")

        # Customer and vehicle data
        self.customers = []
        self.vehicles = []

        self.setup_ui()
        self.load_bookings()
        self.load_dropdowns()

    def setup_ui(self):
        """Setup the booking management UI"""
        self.parent.configure(bg="#f0f0f0")

        # Main container
        self.main_container = tk.Frame(self.parent, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # HEADER
        self.create_header()

        # SEARCH
        self.create_search()

        # ACTION BUTTONS
        self.create_action_buttons()

        # FORM - Only for admin and manager
        if self.can_edit:
            self.create_form()
        else:
            # Show info message for view-only users
            info_frame = tk.Frame(self.main_container, bg="#f0f0f0")
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            info_label = tk.Label(
                info_frame,
                text="ℹ️ You are in View-Only mode. You can view and export booking data but cannot modify it.",
                font=("Segoe UI", 11),
                fg="#7f8c8d",
                bg="#f0f0f0"
            )
            info_label.pack()

        # TABLE
        self.create_table()

        # Approval buttons - Only for admin
        if self.can_approve:
            self.create_approval_buttons()

    def create_header(self):
        """Create header"""
        title_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, pady=(0, 15))

        # Title with view-only indicator for staff
        title_text = "📋 Booking Management"
        if self.is_view_only:
            title_text = "📋 Booking Management (View Only)"
            
        tk.Label(
            title_frame,
            text=title_text,
            font=("Segoe UI", 24, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)

        tk.Button(
            title_frame,
            text="◀ Back to Dashboard",
            command=self.go_back,
            font=("Segoe UI", 10),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT)

        # Stats
        stats_frame = tk.Frame(title_frame, bg="#f0f0f0")
        stats_frame.pack(side=tk.RIGHT, padx=20)

        self.total_label = tk.Label(
            stats_frame,
            text="Total: 0",
            font=("Segoe UI", 12),
            fg="#7f8c8d",
            bg="#f0f0f0"
        )
        self.total_label.pack(side=tk.LEFT, padx=10)

        self.pending_label = tk.Label(
            stats_frame,
            text="Pending: 0",
            font=("Segoe UI", 12),
            fg="#f39c12",
            bg="#f0f0f0"
        )
        self.pending_label.pack(side=tk.LEFT, padx=10)

        # View-only indicator for staff
        if self.is_view_only:
            view_only_label = tk.Label(
                stats_frame,
                text="🔒 View Only",
                font=("Segoe UI", 10, "bold"),
                fg="#e67e22",
                bg="#f0f0f0"
            )
            view_only_label.pack(side=tk.LEFT, padx=10)

    def create_search(self):
        """Create search and filter"""
        search_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            search_frame,
            text="Search:",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var.trace_add("write", self.on_search)
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=30
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            search_frame,
            text="Status:",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_filter_var,
            font=("Segoe UI", 10),
            width=15,
            state="readonly",
            values=["all", "pending", "approved", "rejected", "active", "completed", "cancelled"]
        )
        self.status_combo.pack(side=tk.LEFT)
        self.status_combo.bind("<<ComboboxSelected>>", self.on_status_filter)

    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.load_bookings,
            font=("Segoe UI", 10),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📊 Export CSV",
            command=self.export_csv,
            font=("Segoe UI", 10),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📊 Export Excel",
            command=self.export_excel,
            font=("Segoe UI", 10),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📄 Export PDF",
            command=self.export_pdf,
            font=("Segoe UI", 10),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        # Add New Booking button - Only for admin and manager
        if self.can_edit:
            tk.Button(
                button_frame,
                text="➕ Add New Booking",
                command=self.clear_form,
                font=("Segoe UI", 10, "bold"),
                bg="#9b59b6",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=7
            ).pack(side=tk.LEFT, padx=5)

    def create_approval_buttons(self):
        """Create approval buttons for admin"""
        approval_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        approval_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            approval_frame,
            text="✅ Approve Booking",
            command=self.approve_booking,
            font=("Segoe UI", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            approval_frame,
            text="❌ Reject Booking",
            command=self.reject_booking,
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

    def create_form(self):
        """Create add/edit form"""
        self.form_frame = tk.LabelFrame(
            self.main_container,
            text=" Add / Edit Booking ",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=10
        )
        self.form_frame.pack(fill=tk.X, pady=(0, 15))

        # ROW 1
        row1 = tk.Frame(self.form_frame, bg="white")
        row1.pack(fill=tk.X, pady=5)

        # Booking Ref
        tk.Label(row1, text="Booking Ref *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row1, textvariable=self.booking_ref_var, font=("Segoe UI", 10), width=18).pack(side=tk.LEFT, padx=(0, 20))

        # Customer
        tk.Label(row1, text="Customer *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.customer_combo = ttk.Combobox(
            row1,
            textvariable=self.customer_id_var,
            font=("Segoe UI", 10),
            width=25,
            state="readonly"
        )
        self.customer_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Vehicle
        tk.Label(row1, text="Vehicle *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.vehicle_combo = ttk.Combobox(
            row1,
            textvariable=self.vehicle_id_var,
            font=("Segoe UI", 10),
            width=25,
            state="readonly"
        )
        self.vehicle_combo.pack(side=tk.LEFT)

        # ROW 2
        row2 = tk.Frame(self.form_frame, bg="white")
        row2.pack(fill=tk.X, pady=5)

        # Daily Rate
        tk.Label(row2, text="Daily Rate *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.daily_rate_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT, padx=(0, 20))

        # Start Date
        tk.Label(row2, text="Start Date *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.start_date_var, font=("Segoe UI", 10), width=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row2, text="(YYYY-MM-DD)", font=("Segoe UI", 9), fg="#7f8c8d", bg="white").pack(side=tk.LEFT, padx=(0, 20))

        # End Date
        tk.Label(row2, text="End Date *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.end_date_var, font=("Segoe UI", 10), width=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row2, text="(YYYY-MM-DD)", font=("Segoe UI", 9), fg="#7f8c8d", bg="white").pack(side=tk.LEFT)

        # ROW 3
        row3 = tk.Frame(self.form_frame, bg="white")
        row3.pack(fill=tk.X, pady=5)

        # Pickup Location
        tk.Label(row3, text="Pickup Location", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row3, textvariable=self.pickup_location_var, font=("Segoe UI", 10), width=18).pack(side=tk.LEFT, padx=(0, 20))

        # Drop-off Location
        tk.Label(row3, text="Drop-off Location", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row3, textvariable=self.dropoff_location_var, font=("Segoe UI", 10), width=18).pack(side=tk.LEFT, padx=(0, 20))

        # Status
        tk.Label(row3, text="Status", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.status_combo_form = ttk.Combobox(
            row3,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            width=15,
            state="readonly",
            values=["pending", "approved", "rejected", "active", "completed", "cancelled"]
        )
        self.status_combo_form.pack(side=tk.LEFT)

        # ROW 4
        row4 = tk.Frame(self.form_frame, bg="white")
        row4.pack(fill=tk.X, pady=5)

        # Total Days (auto-calculated, read-only)
        tk.Label(row4, text="Total Days", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row4, textvariable=self.total_days_var, font=("Segoe UI", 10, "bold"), fg="#2c3e50", bg="white", width=10, anchor="w").pack(side=tk.LEFT, padx=(0, 20))

        # Total Amount (auto-calculated, read-only)
        tk.Label(row4, text="Total Amount ($)", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row4, textvariable=self.total_amount_var, font=("Segoe UI", 10, "bold"), fg="#27ae60", bg="white", width=12, anchor="w").pack(side=tk.LEFT, padx=(0, 20))

        # Deposit
        tk.Label(row4, text="Deposit ($)", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row4, textvariable=self.deposit_amount_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT)

        # ROW 5 - Notes
        row5 = tk.Frame(self.form_frame, bg="white")
        row5.pack(fill=tk.X, pady=5)

        tk.Label(row5, text="Notes", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row5, textvariable=self.notes_var, font=("Segoe UI", 10), width=60).pack(side=tk.LEFT)

        # ROW 6 - Buttons
        row6 = tk.Frame(self.form_frame, bg="white")
        row6.pack(fill=tk.X, pady=(8, 0))

        self.save_button = tk.Button(
            row6,
            text="➕ Add Booking",
            command=self.save_booking,
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=25,
            pady=7
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)

        tk.Button(
            row6,
            text="Clear",
            command=self.clear_form,
            font=("Segoe UI", 10),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=25,
            pady=7
        ).pack(side=tk.RIGHT, padx=5)

        # Bind date changes to calculate total
        self.start_date_var.trace_add("write", self.calculate_total)
        self.end_date_var.trace_add("write", self.calculate_total)
        self.daily_rate_var.trace_add("write", self.calculate_total)

    def create_table(self):
        """Create table for bookings"""
        table_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        table_frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ("ID", "Reference", "Customer", "Vehicle", "Start", "End", "Days", "Total", "Paid", "Balance", "Status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        headings = {
            "ID": "ID",
            "Reference": "Reference",
            "Customer": "Customer",
            "Vehicle": "Vehicle",
            "Start": "Start",
            "End": "End",
            "Days": "Days",
            "Total": "Total ($)",
            "Paid": "Paid ($)",
            "Balance": "Balance ($)",
            "Status": "Status"
        }

        for column, heading in headings.items():
            self.tree.heading(column, text=heading)

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Reference", width=150, anchor="center")
        self.tree.column("Customer", width=150)
        self.tree.column("Vehicle", width=180)
        self.tree.column("Start", width=100, anchor="center")
        self.tree.column("End", width=100, anchor="center")
        self.tree.column("Days", width=60, anchor="center")
        self.tree.column("Total", width=100, anchor="center")
        self.tree.column("Paid", width=100, anchor="center")
        self.tree.column("Balance", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Bind events - different behavior based on role
        if self.can_edit:
            self.tree.bind("<Double-1>", lambda event: self.edit_selected())
            self.tree.bind("<Button-3>", self.show_context_menu)

            # Context menu - Only for admin and manager
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="✏️ Edit", command=self.edit_selected)
            self.context_menu.add_command(label="🗑️ Delete", command=self.delete_booking)
            
            # Approval options only for admin
            if self.can_approve:
                self.context_menu.add_separator()
                self.context_menu.add_command(label="✅ Approve", command=self.approve_booking)
                self.context_menu.add_command(label="❌ Reject", command=self.reject_booking)
        else:
            # View-only users can double-click to view details
            self.tree.bind("<Double-1>", lambda event: self.view_booking_details())

    # ==========================================================
    # VIEW DETAILS (for view-only users)
    # ==========================================================

    def view_booking_details(self):
        """Show booking details in a read-only dialog"""
        booking_id = self.get_selected_booking_id()
        if booking_id is None:
            return

        try:
            booking = self.controller.get_booking_by_id(booking_id)
            if not booking:
                messagebox.showerror("Error", "Booking not found.")
                return

            # Create details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Booking #{booking.get('booking_ref', '')}")
            dialog.geometry("550x550")
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
                text=f"📋 Booking {booking.get('booking_ref', '')}",
                font=("Segoe UI", 16, "bold"),
                fg="white",
                bg='#2c3e50'
            ).pack(pady=15)

            # Details
            details_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            status_colors = {
                'pending': '#f39c12',
                'approved': '#27ae60',
                'rejected': '#e74c3c',
                'active': '#3498db',
                'completed': '#2ecc71',
                'cancelled': '#95a5a6'
            }
            status = booking.get('booking_status', 'pending')
            status_display = status.title()

            customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}".strip()
            vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')} ({booking.get('license_plate', '')})"

            details = [
                ("Booking ID", str(booking.get('booking_id', ''))),
                ("Reference", booking.get('booking_ref', '')),
                ("Customer", customer_name or 'N/A'),
                ("Customer Email", booking.get('email', 'N/A')),
                ("Customer Phone", booking.get('phone', 'N/A')),
                ("Vehicle", vehicle_name or 'N/A'),
                ("Start Date", booking.get('start_date', '')),
                ("End Date", booking.get('end_date', '')),
                ("Total Days", str(booking.get('total_days', 0))),
                ("Daily Rate", f"${booking.get('daily_rate', 0):.2f}"),
                ("Total Amount", f"${booking.get('total_amount', 0):.2f}"),
                ("Paid Amount", f"${booking.get('paid_amount', 0):.2f}"),
                ("Balance", f"${booking.get('balance_amount', 0):.2f}"),
                ("Deposit", f"${booking.get('deposit_amount', 0):.2f}"),
                ("Pickup Location", booking.get('pickup_location', 'N/A')),
                ("Drop-off Location", booking.get('dropoff_location', 'N/A')),
                ("Status", status_display),
                ("Notes", booking.get('notes', 'None') or 'None')
            ]

            # Status with color indicator
            for i, (label, value) in enumerate(details):
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
            messagebox.showerror("Error", f"Could not load booking details:\n\n{str(e)}")

    def load_dropdowns(self):
        """Load customers and vehicles into dropdowns - only if form exists"""
        try:
            # Load customers
            customers = self.controller.get_customers()
            self.customers = customers or []
            customer_display = []
            for c in self.customers:
                customer_display.append(f"{c['customer_id']}: {c['first_name']} {c['last_name']} ({c['email']})")
            
            # Only set if form exists
            if hasattr(self, 'customer_combo'):
                self.customer_combo["values"] = customer_display

            # Load vehicles
            vehicles = self.controller.get_vehicles()
            self.vehicles = vehicles or []
            vehicle_display = []
            for v in self.vehicles:
                vehicle_display.append(f"{v['id']}: {v['make']} {v['model']} ({v['license_plate']})")
            
            if hasattr(self, 'vehicle_combo'):
                self.vehicle_combo["values"] = vehicle_display

            # Set default values - only if form exists
            if hasattr(self, 'customer_combo'):
                self.customer_combo.set("")
                self.vehicle_combo.set("")
                self.booking_ref_var.set(self.controller.get_next_booking_ref())

        except Exception as e:
            print(f"Error loading dropdowns: {e}")

    def load_bookings(self, search_term="", status_filter="all"):
        """Load bookings into the tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if search_term:
                bookings = self.controller.search_bookings(search_term)
            elif status_filter != "all":
                bookings = self.controller.get_by_status(status_filter)
            else:
                bookings = self.controller.get_all_bookings()

            if bookings:
                for row in bookings:
                    # Status colors for tag
                    status = row.get('booking_status', 'pending')
                    
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            row.get("booking_id", ""),
                            row.get("booking_ref", ""),
                            f"{row.get('first_name', '')} {row.get('last_name', '')}",
                            f"{row.get('make', '')} {row.get('model', '')} ({row.get('license_plate', '')})",
                            row.get("start_date", ""),
                            row.get("end_date", ""),
                            row.get("total_days", ""),
                            f"${row.get('total_amount', 0):.2f}",
                            f"${row.get('paid_amount', 0):.2f}",
                            f"${row.get('balance_amount', 0):.2f}",
                            status.capitalize()
                        ),
                        tags=(status,)
                    )

            # Configure status colors
            status_colors = {
                'pending': '#fff3e0',
                'approved': '#e8f5e9',
                'rejected': '#ffebee',
                'active': '#e3f2fd',
                'completed': '#e8f5e9',
                'cancelled': '#f5f5f5'
            }
            for status, color in status_colors.items():
                self.tree.tag_configure(status, background=color)

            # Update stats
            self.update_stats(bookings)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load bookings: {str(e)}")

    def update_stats(self, bookings):
        """Update statistics"""
        total = len(bookings) if bookings else 0
        pending = 0
        if bookings:
            pending = sum(1 for b in bookings if b.get('booking_status') == 'pending')

        self.total_label.config(text=f"Total: {total}")
        self.pending_label.config(text=f"Pending: {pending}")

    def calculate_total(self, *args):
        """Calculate total days and amount"""
        try:
            start_str = self.start_date_var.get().strip()
            end_str = self.end_date_var.get().strip()
            daily_rate = self.daily_rate_var.get().strip()

            if start_str and end_str and daily_rate:
                start = datetime.strptime(start_str, "%Y-%m-%d")
                end = datetime.strptime(end_str, "%Y-%m-%d")
                if end > start:
                    days = (end - start).days
                    self.total_days_var.set(str(days))
                    total = days * float(daily_rate)
                    self.total_amount_var.set(f"{total:.2f}")
                else:
                    self.total_days_var.set("0")
                    self.total_amount_var.set("0.00")
        except:
            pass

    def save_booking(self):
        """Save or update booking - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify bookings.")
            return

        data = {
            'booking_ref': self.booking_ref_var.get().strip(),
            'customer_id': self.get_selected_id(self.customer_combo.get()),
            'vehicle_id': self.get_selected_id(self.vehicle_combo.get()),
            'start_date': self.start_date_var.get().strip(),
            'end_date': self.end_date_var.get().strip(),
            'pickup_location': self.pickup_location_var.get().strip(),
            'dropoff_location': self.dropoff_location_var.get().strip(),
            'daily_rate': self.daily_rate_var.get().strip(),
            'deposit_amount': self.deposit_amount_var.get().strip() or '0',
            'booking_status': self.status_var.get(),
            'notes': self.notes_var.get().strip()
        }

        # Validation
        if not data['booking_ref']:
            messagebox.showwarning("Validation", "Booking reference is required.")
            return
        if not data['customer_id']:
            messagebox.showwarning("Validation", "Please select a customer.")
            return
        if not data['vehicle_id']:
            messagebox.showwarning("Validation", "Please select a vehicle.")
            return
        if not data['start_date']:
            messagebox.showwarning("Validation", "Start date is required.")
            return
        if not data['end_date']:
            messagebox.showwarning("Validation", "End date is required.")
            return

        try:
            if self.editing_id is None:
                result = self.controller.add_booking(data)
            else:
                result = self.controller.update_booking(self.editing_id, data)

            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.clear_form()
                self.load_bookings()
            else:
                messagebox.showerror("Error", result['message'])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save booking: {str(e)}")

    def approve_booking(self):
        """Approve a booking - only for admin"""
        if not self.can_approve:
            messagebox.showwarning("Access Denied", "Only administrators can approve bookings.")
            return

        booking_id = self.get_selected_booking_id()
        if booking_id is None:
            return

        if not messagebox.askyesno("Confirm Approve", "Are you sure you want to approve this booking?"):
            return

        try:
            result = self.controller.approve_booking(booking_id, self.user.get('id'))
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.load_bookings()
                self.clear_form()
            else:
                messagebox.showerror("Error", result['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve booking: {str(e)}")

    def reject_booking(self):
        """Reject a booking with reason - only for admin"""
        if not self.can_approve:
            messagebox.showwarning("Access Denied", "Only administrators can reject bookings.")
            return

        booking_id = self.get_selected_booking_id()
        if booking_id is None:
            return

        # Create dialog for rejection reason
        self.rejection_dialog(booking_id)

    def rejection_dialog(self, booking_id):
        """Create rejection dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Reject Booking")
        dialog.geometry("400x200")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(
            dialog,
            text="Rejection Reason",
            font=("Segoe UI", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack(pady=(20, 10))

        reason_text = tk.Text(dialog, font=("Segoe UI", 10), height=3, width=40)
        reason_text.pack(padx=20, pady=10)

        def submit_rejection():
            reason = reason_text.get("1.0", tk.END).strip()
            if not reason:
                messagebox.showwarning("Validation", "Please enter a rejection reason.")
                return

            try:
                result = self.controller.reject_booking(booking_id, reason)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    dialog.destroy()
                    self.load_bookings()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reject booking: {str(e)}")

        btn_frame = tk.Frame(dialog, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="Submit",
            command=submit_rejection,
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            font=("Segoe UI", 10),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)

    def edit_selected(self):
        """Edit selected booking - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to edit bookings.")
            return

        booking_id = self.get_selected_booking_id()
        if booking_id is None:
            return

        try:
            booking = self.controller.get_booking_by_id(booking_id)
            if not booking:
                messagebox.showerror("Error", "Booking not found.")
                return

            self.editing_id = booking_id

            # Set form values
            self.booking_ref_var.set(booking.get('booking_ref', ''))
            self.start_date_var.set(booking.get('start_date', ''))
            self.end_date_var.set(booking.get('end_date', ''))
            self.pickup_location_var.set(booking.get('pickup_location', ''))
            self.dropoff_location_var.set(booking.get('dropoff_location', ''))
            self.daily_rate_var.set(str(booking.get('daily_rate', 0)))
            self.deposit_amount_var.set(str(booking.get('deposit_amount', 0)))
            self.status_var.set(booking.get('booking_status', 'pending'))
            self.notes_var.set(booking.get('notes', ''))

            # Set customer
            customer_id = booking.get('customer_id')
            for i, c in enumerate(self.customers):
                if c.get('customer_id') == customer_id:
                    self.customer_combo.current(i)
                    break

            # Set vehicle
            vehicle_id = booking.get('vehicle_id')
            for i, v in enumerate(self.vehicles):
                if v.get('id') == vehicle_id:
                    self.vehicle_combo.current(i)
                    break

            self.save_button.config(text="✏️ Update Booking")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load booking: {str(e)}")

    def delete_booking(self):
        """Delete selected booking - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to delete bookings.")
            return

        booking_id = self.get_selected_booking_id()
        if booking_id is None:
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this booking?"):
            return

        try:
            result = self.controller.delete_booking(booking_id)
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.load_bookings()
                self.clear_form()
            else:
                messagebox.showerror("Error", result['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete booking: {str(e)}")

    def get_selected_booking_id(self):
        """Get selected booking ID from tree"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a booking first.")
            return None

        item = self.tree.item(selection[0])
        return item['values'][0]

    def get_selected_id(self, display_text):
        """Extract ID from display text (e.g., '1: John Doe (john@mail.com)' -> 1)"""
        if not display_text:
            return None
        try:
            return int(display_text.split(':')[0])
        except:
            return None

    def clear_form(self):
        """Clear form fields - only for admin and manager"""
        if not self.can_edit:
            return

        self.editing_id = None
        self.booking_ref_var.set(self.controller.get_next_booking_ref())
        self.customer_id_var.set("")
        self.vehicle_id_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.pickup_location_var.set("")
        self.dropoff_location_var.set("")
        self.daily_rate_var.set("")
        self.total_days_var.set("")
        self.total_amount_var.set("")
        self.deposit_amount_var.set("0")
        self.status_var.set("pending")
        self.notes_var.set("")
        
        if hasattr(self, 'customer_combo'):
            self.customer_combo.set("")
            self.vehicle_combo.set("")
        
        if hasattr(self, 'save_button'):
            self.save_button.config(text="➕ Add Booking")

    def on_search(self, *args):
        """Handle search"""
        search_term = self.search_var.get().strip()
        status = self.status_filter_var.get()
        self.load_bookings(search_term, status)

    def on_status_filter(self, event):
        """Handle status filter"""
        search_term = self.search_var.get().strip()
        status = self.status_filter_var.get()
        self.load_bookings(search_term, status)

    def show_context_menu(self, event):
        """Show context menu - only for admin and manager"""
        if not self.can_edit:
            return
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def go_back(self):
        """Go back to dashboard"""
        for widget in self.parent.winfo_children():
            widget.destroy()

        if self.dashboard_controller:
            from views.main_dashboard import MainDashboard
            MainDashboard(self.parent, self.user, self.dashboard_controller)

    def export_csv(self):
        """Export to CSV - all users can export"""
        bookings = self.controller.get_all_bookings()
        if bookings:
            self.controller.export_to_csv(bookings)
        else:
            messagebox.showwarning("No Data", "No bookings to export.")

    def export_excel(self):
        """Export to Excel - all users can export"""
        bookings = self.controller.get_all_bookings()
        if bookings:
            self.controller.export_to_excel(bookings)
        else:
            messagebox.showwarning("No Data", "No bookings to export.")

    def export_pdf(self):
        """Export to PDF - all users can export"""
        bookings = self.controller.get_all_bookings()
        if bookings:
            self.controller.export_to_pdf(bookings)
        else:
            messagebox.showwarning("No Data", "No bookings to export.")