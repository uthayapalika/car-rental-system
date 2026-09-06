# views/vehicle_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.vehicle_controller import VehicleController


class VehicleView:
    def __init__(self, parent, db, user, dashboard_controller=None):
        self.parent = parent
        self.db = db
        self.user = user
        self.dashboard_controller = dashboard_controller

        # Database/controller
        self.controller = VehicleController(db)

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
        
        # Form variables
        self.make_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.license_plate_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.mileage_var = tk.StringVar()
        self.daily_rate_var = tk.StringVar()
        self.status_var = tk.StringVar(value="available")
        self.fuel_type_var = tk.StringVar(value="Petrol")
        self.min_period_var = tk.StringVar(value="1")
        self.max_period_var = tk.StringVar(value="30")

        # Category selection
        self.category_id_var = tk.StringVar()
        self.categories = []

        self.setup_ui()
        self.load_categories()
        self.load_vehicles()

    # ==========================================================
    # MAIN UI
    # ==========================================================

    def setup_ui(self):
        self.parent.configure(bg="#f0f0f0")

        # Main container
        self.main_container = tk.Frame(self.parent, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ------------------------------------------------------
        # HEADER
        # ------------------------------------------------------

        title_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, pady=(0, 15))

        # Title with view-only indicator for staff
        title_text = "🚗 Vehicle Management"
        if self.is_view_only:
            title_text = "🚗 Vehicle Management (View Only)"
            
        tk.Label(
            title_frame,
            text=title_text,
            font=("Segoe UI", 24, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)

        # Back button
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

        # Statistics
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

        self.available_label = tk.Label(
            stats_frame,
            text="Available: 0",
            font=("Segoe UI", 12),
            fg="#27ae60",
            bg="#f0f0f0"
        )
        self.available_label.pack(side=tk.LEFT, padx=10)

        self.rented_label = tk.Label(
            stats_frame,
            text="Rented: 0",
            font=("Segoe UI", 12),
            fg="#e74c3c",
            bg="#f0f0f0"
        )
        self.rented_label.pack(side=tk.LEFT, padx=10)

        # ------------------------------------------------------
        # SEARCH
        # ------------------------------------------------------

        search_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            search_frame,
            text="Search:",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=35
        )
        self.search_entry.pack(side=tk.LEFT)

        # Status filter
        tk.Label(
            search_frame,
            text="Status:",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(20, 10))

        self.status_filter_var = tk.StringVar(value="all")
        status_filter = ttk.Combobox(
            search_frame,
            textvariable=self.status_filter_var,
            values=["all", "available", "rented", "maintenance", "reserved"],
            width=12,
            state="readonly"
        )
        status_filter.pack(side=tk.LEFT)
        status_filter.bind("<<ComboboxSelected>>", lambda e: self.load_vehicles())

        # ------------------------------------------------------
        # ACTION BUTTONS
        # ------------------------------------------------------

        button_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Refresh button - always visible
        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.load_vehicles,
            font=("Segoe UI", 10),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=7
        ).pack(side=tk.LEFT, padx=5)

        # Export buttons - always visible for all users
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

        # Add New Vehicle button - Only for admin and manager
        if self.can_edit:
            tk.Button(
                button_frame,
                text="➕ Add New Vehicle",
                command=self.clear_form,
                font=("Segoe UI", 10, "bold"),
                bg="#9b59b6",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=7
            ).pack(side=tk.LEFT, padx=5)

        # View-only indicator for staff
        if self.is_view_only:
            view_only_label = tk.Label(
                button_frame,
                text="🔒 View Only Mode",
                font=("Segoe UI", 10, "bold"),
                fg="#e67e22",
                bg="#f0f0f0"
            )
            view_only_label.pack(side=tk.RIGHT, padx=10)

        # ------------------------------------------------------
        # ADD / EDIT FORM - Only for admin and manager
        # ------------------------------------------------------

        if self.can_edit:
            self.create_form()
        else:
            # Show info message for view-only users
            info_frame = tk.Frame(self.main_container, bg="#f0f0f0")
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            info_label = tk.Label(
                info_frame,
                text="ℹ️ You are in View-Only mode. You can view and export vehicle data but cannot modify it.",
                font=("Segoe UI", 11),
                fg="#7f8c8d",
                bg="#f0f0f0"
            )
            info_label.pack()

        # ------------------------------------------------------
        # TABLE
        # ------------------------------------------------------

        self.create_table()

    # ==========================================================
    # ADD / EDIT FORM
    # ==========================================================

    def create_form(self):
        self.form_frame = tk.LabelFrame(
            self.main_container,
            text=" Add / Edit Vehicle ",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=10
        )
        self.form_frame.pack(fill=tk.X, pady=(0, 15))

        # Row 1: Category, Make, Model
        row1 = tk.Frame(self.form_frame, bg="white")
        row1.pack(fill=tk.X, pady=5)

        # Category
        tk.Label(row1, text="Category *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.category_combo = ttk.Combobox(
            row1,
            textvariable=self.category_id_var,
            width=15,
            state="readonly"
        )
        self.category_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Make
        tk.Label(row1, text="Make *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row1, textvariable=self.make_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT, padx=(0, 20))

        # Model
        tk.Label(row1, text="Model *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row1, textvariable=self.model_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT)

        # Row 2: Year, License Plate, Color
        row2 = tk.Frame(self.form_frame, bg="white")
        row2.pack(fill=tk.X, pady=5)

        # Year
        tk.Label(row2, text="Year *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.year_var, font=("Segoe UI", 10), width=8).pack(side=tk.LEFT, padx=(0, 20))

        # License Plate
        tk.Label(row2, text="License Plate *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.license_plate_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT, padx=(0, 20))

        # Color
        tk.Label(row2, text="Color", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.color_var, font=("Segoe UI", 10), width=10).pack(side=tk.LEFT)

        # Row 3: Mileage, Daily Rate, Fuel Type
        row3 = tk.Frame(self.form_frame, bg="white")
        row3.pack(fill=tk.X, pady=5)

        # Mileage
        tk.Label(row3, text="Mileage", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row3, textvariable=self.mileage_var, font=("Segoe UI", 10), width=10).pack(side=tk.LEFT, padx=(0, 20))

        # Daily Rate
        tk.Label(row3, text="Daily Rate ($) *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row3, textvariable=self.daily_rate_var, font=("Segoe UI", 10), width=10).pack(side=tk.LEFT, padx=(0, 20))

        # Fuel Type
        tk.Label(row3, text="Fuel Type", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(
            row3,
            textvariable=self.fuel_type_var,
            values=["Petrol", "Diesel", "Electric", "Hybrid"],
            width=10,
            state="readonly"
        ).pack(side=tk.LEFT)

        # Row 4: Status, Min Period, Max Period
        row4 = tk.Frame(self.form_frame, bg="white")
        row4.pack(fill=tk.X, pady=5)

        # Status
        tk.Label(row4, text="Status", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(
            row4,
            textvariable=self.status_var,
            values=["available", "rented", "maintenance", "reserved"],
            width=12,
            state="readonly"
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Min Period
        tk.Label(row4, text="Min Period (days)", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row4, textvariable=self.min_period_var, font=("Segoe UI", 10), width=6).pack(side=tk.LEFT, padx=(0, 20))

        # Max Period
        tk.Label(row4, text="Max Period (days)", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row4, textvariable=self.max_period_var, font=("Segoe UI", 10), width=6).pack(side=tk.LEFT)

        # Row 5: Buttons
        row5 = tk.Frame(self.form_frame, bg="white")
        row5.pack(fill=tk.X, pady=(8, 0))

        self.save_button = tk.Button(
            row5,
            text="➕ Save Vehicle",
            command=self.save_vehicle,
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
            row5,
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

    # ==========================================================
    # TABLE
    # ==========================================================

    def create_table(self):
        table_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        table_frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = (
            "ID", "Category", "Make", "Model", "Year", "License Plate",
            "Color", "Mileage", "Daily Rate", "Status", "Fuel Type"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        headings = {
            "ID": "ID",
            "Category": "Category",
            "Make": "Make",
            "Model": "Model",
            "Year": "Year",
            "License Plate": "License Plate",
            "Color": "Color",
            "Mileage": "Mileage",
            "Daily Rate": "Daily Rate ($)",
            "Status": "Status",
            "Fuel Type": "Fuel Type"
        }

        for column, heading in headings.items():
            self.tree.heading(column, text=heading)

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Category", width=120)
        self.tree.column("Make", width=100)
        self.tree.column("Model", width=100)
        self.tree.column("Year", width=60, anchor="center")
        self.tree.column("License Plate", width=110, anchor="center")
        self.tree.column("Color", width=80, anchor="center")
        self.tree.column("Mileage", width=80, anchor="center")
        self.tree.column("Daily Rate", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Fuel Type", width=80, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Right-click menu - Only for admin and manager
        if self.can_edit:
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="✏️ Edit", command=self.edit_selected)
            self.context_menu.add_command(label="🔄 Change Status", command=self.change_status)
            self.context_menu.add_command(label="🗑️ Delete", command=self.delete_vehicle)
            self.tree.bind("<Button-3>", self.show_context_menu)
            self.tree.bind("<Double-1>", lambda event: self.edit_selected())
        else:
            # View-only users can double-click to view details
            self.tree.bind("<Double-1>", lambda event: self.view_vehicle_details())

    # ==========================================================
    # VIEW DETAILS (for view-only users)
    # ==========================================================

    def view_vehicle_details(self):
        """Show vehicle details in a read-only dialog"""
        vehicle_id = self.get_selected_vehicle_id()
        if vehicle_id is None:
            return

        try:
            vehicle = self.controller.get_vehicle_by_id(vehicle_id)
            if not vehicle:
                messagebox.showerror("Error", "Vehicle not found.")
                return

            # Create details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Vehicle Details - {vehicle['make']} {vehicle['model']}")
            dialog.geometry("450x500")
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
                text=f"🚗 {vehicle['make']} {vehicle['model']}",
                font=("Segoe UI", 16, "bold"),
                fg="white",
                bg='#2c3e50'
            ).pack(pady=15)

            # Details
            details_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            details = [
                ("ID", str(vehicle['id'])),
                ("Category", vehicle['category_name'] if 'category_name' in vehicle else 'N/A'),
                ("Make", vehicle['make']),
                ("Model", vehicle['model']),
                ("Year", str(vehicle['year'])),
                ("License Plate", vehicle['license_plate']),
                ("Color", vehicle['color'] or 'N/A'),
                ("Mileage", f"{vehicle['mileage']:,}" if vehicle['mileage'] else '0'),
                ("Daily Rate", f"${vehicle['daily_rate']:.2f}"),
                ("Status", vehicle['status'].title()),
                ("Fuel Type", vehicle['fuel_type'] or 'N/A'),
                ("Min Period", f"{vehicle.get('min_rent_period', 1)} days"),
                ("Max Period", f"{vehicle.get('max_rent_period', 30)} days"),
            ]

            for i, (label, value) in enumerate(details):
                row_frame = tk.Frame(details_frame, bg='white')
                row_frame.pack(fill=tk.X, pady=3)
                
                tk.Label(
                    row_frame,
                    text=f"{label}:",
                    font=("Segoe UI", 11, "bold"),
                    bg='white',
                    fg='#2c3e50',
                    width=15,
                    anchor='w'
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    row_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    bg='white',
                    fg='#34495e'
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
            messagebox.showerror("Error", f"Could not load vehicle details:\n\n{str(e)}")

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_categories(self):
        """Load categories into combobox"""
        try:
            from models.vehicle_category_model import VehicleCategoryModel
            model = VehicleCategoryModel(self.db)
            self.categories = model.get_all()

            # Clear and populate combobox - only if form exists
            if hasattr(self, 'category_combo'):
                values = [f"{cat['id']}: {cat['name']}" for cat in self.categories]
                self.category_combo['values'] = values

                if values:
                    self.category_combo.current(0)
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_vehicles(self):
        """Load vehicles into treeview"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Apply status filter
            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "all":
                vehicles = self.controller.get_by_status(status_filter)
            else:
                vehicles = self.controller.get_all_vehicles()

            # Define status colors outside the conditional block
            status_colors = {
                'available': '#e8f5e9',  # Green
                'rented': '#ffebee',      # Red
                'maintenance': '#fff3e0', # Orange
                'reserved': '#e3f2fd'     # Blue
            }

            if vehicles:
                for row in vehicles:
                    status = row['status'].title()
                    tags = (row['status'],)

                    # Get values using dictionary-style indexing
                    category_name = row['category_name'] if 'category_name' in row.keys() and row['category_name'] else ''
                    color = row['color'] if row['color'] else ''
                    mileage = row['mileage'] if row['mileage'] else 0
                    fuel_type = row['fuel_type'] if row['fuel_type'] else ''

                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            row['id'],
                            category_name,
                            row['make'],
                            row['model'],
                            row['year'],
                            row['license_plate'],
                            color,
                            f"{mileage:,}",
                            f"${row['daily_rate']:.2f}",
                            status,
                            fuel_type
                        ),
                        tags=tags
                    )

            # Configure tags for color coding
            for status, color in status_colors.items():
                self.tree.tag_configure(status, background=color)

            self.update_stats(vehicles)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load vehicles:\n\n{str(e)}")

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def update_stats(self, vehicles=None):
        try:
            if vehicles is None:
                vehicles = self.controller.get_all_vehicles()
            
            if vehicles is None:
                vehicles = []

            total = len(vehicles)
            
            # Get counts from controller
            counts = self.controller.get_status_counts()

            self.total_label.config(text=f"Total: {total}")
            self.available_label.config(text=f"Available: {counts.get('available', 0)}")
            self.rented_label.config(text=f"Rented: {counts.get('rented', 0)}")
        except Exception as e:
            print(f"Error updating stats: {e}")

    # ==========================================================
    # SEARCH
    # ==========================================================

    def on_search(self, *args):
        try:
            search_term = self.search_var.get().strip()

            if search_term:
                vehicles = self.controller.search_vehicles(search_term)
            else:
                vehicles = self.controller.get_all_vehicles()

            # Apply status filter
            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "all":
                vehicles = [v for v in vehicles if v['status'] == status_filter]

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in vehicles:
                category_name = row['category_name'] if 'category_name' in row.keys() and row['category_name'] else ''
                color = row['color'] if row['color'] else ''
                mileage = row['mileage'] if row['mileage'] else 0
                fuel_type = row['fuel_type'] if row['fuel_type'] else ''

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row['id'],
                        category_name,
                        row['make'],
                        row['model'],
                        row['year'],
                        row['license_plate'],
                        color,
                        f"{mileage:,}",
                        f"${row['daily_rate']:.2f}",
                        row['status'].title(),
                        fuel_type
                    ),
                    tags=(row['status'],)
                )
        except Exception as e:
            print("Search error:", e)

    # ==========================================================
    # SAVE / UPDATE - Only for admin and manager
    # ==========================================================

    def save_vehicle(self):
        """Save vehicle - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify vehicles.")
            return
            
        # Get form data
        category_text = self.category_combo.get()
        if not category_text:
            messagebox.showwarning("Validation", "Please select a category.")
            return

        category_id = int(category_text.split(':')[0])

        data = {
            'category_id': category_id,
            'make': self.make_var.get().strip(),
            'model': self.model_var.get().strip(),
            'year': self.year_var.get().strip(),
            'license_plate': self.license_plate_var.get().strip(),
            'color': self.color_var.get().strip(),
            'mileage': self.mileage_var.get().strip() or 0,
            'daily_rate': self.daily_rate_var.get().strip(),
            'status': self.status_var.get(),
            'fuel_type': self.fuel_type_var.get(),
            'min_rent_period': self.min_period_var.get().strip() or 1,
            'max_rent_period': self.max_period_var.get().strip() or 30
        }

        try:
            # UPDATE
            if self.editing_id is not None:
                result = self.controller.update_vehicle(self.editing_id, data)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    self.clear_form()
                    self.load_vehicles()
                else:
                    messagebox.showerror("Error", result['message'])
            # ADD
            else:
                result = self.controller.add_vehicle(data)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    self.clear_form()
                    self.load_vehicles()
                else:
                    messagebox.showerror("Error", result['message'])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save vehicle:\n\n{str(e)}")

    # ==========================================================
    # CLEAR FORM - Only for admin and manager
    # ==========================================================

    def clear_form(self):
        """Clear form - only for admin and manager"""
        if not self.can_edit:
            return
            
        self.editing_id = None

        self.make_var.set("")
        self.model_var.set("")
        self.year_var.set("")
        self.license_plate_var.set("")
        self.color_var.set("")
        self.mileage_var.set("")
        self.daily_rate_var.set("")
        self.status_var.set("available")
        self.fuel_type_var.set("Petrol")
        self.min_period_var.set("1")
        self.max_period_var.set("30")

        if hasattr(self, 'category_combo') and self.categories:
            self.category_combo.current(0)

        if hasattr(self, 'save_button'):
            self.save_button.config(text="➕ Save Vehicle")

    # ==========================================================
    # EDIT - Only for admin and manager
    # ==========================================================

    def edit_selected(self):
        """Edit selected vehicle - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to edit vehicles.")
            return

        vehicle_id = self.get_selected_vehicle_id()
        if vehicle_id is None:
            return

        try:
            vehicle = self.controller.get_vehicle_by_id(vehicle_id)
            if not vehicle:
                messagebox.showerror("Error", "Vehicle not found.")
                return

            self.editing_id = vehicle_id

            # Set category
            for i, cat in enumerate(self.categories):
                if cat['id'] == vehicle['category_id']:
                    self.category_combo.current(i)
                    break

            self.make_var.set(vehicle['make'])
            self.model_var.set(vehicle['model'])
            self.year_var.set(str(vehicle['year']))
            self.license_plate_var.set(vehicle['license_plate'])
            self.color_var.set(vehicle['color'] if vehicle['color'] else '')
            self.mileage_var.set(str(vehicle['mileage'] if vehicle['mileage'] else 0))
            self.daily_rate_var.set(str(vehicle['daily_rate']))
            self.status_var.set(vehicle['status'])
            self.fuel_type_var.set(vehicle['fuel_type'] if vehicle['fuel_type'] else 'Petrol')
            self.min_period_var.set(str(vehicle['min_rent_period'] if 'min_rent_period' in vehicle.keys() else 1))
            self.max_period_var.set(str(vehicle['max_rent_period'] if 'max_rent_period' in vehicle.keys() else 30))

            self.save_button.config(text="✏️ Update Vehicle")

            # Scroll to form
            self.form_frame.focus_set()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load vehicle:\n\n{str(e)}")

    # ==========================================================
    # SELECTED ID
    # ==========================================================

    def get_selected_vehicle_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a vehicle first.")
            return None

        item = self.tree.item(selection[0])
        return item['values'][0]

    # ==========================================================
    # CONTEXT MENU - Only for admin and manager
    # ==========================================================

    def show_context_menu(self, event):
        """Show context menu - only for admin and manager"""
        if not self.can_edit:
            return
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # ==========================================================
    # CHANGE STATUS - Only for admin and manager
    # ==========================================================

    def change_status(self):
        """Change vehicle status - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify vehicle status.")
            return

        vehicle_id = self.get_selected_vehicle_id()
        if vehicle_id is None:
            return

        try:
            vehicle = self.controller.get_vehicle_by_id(vehicle_id)
            if not vehicle:
                return

            # Create status dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Change Status")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self.parent)
            dialog.grab_set()

            tk.Label(
                dialog,
                text=f"Change status for {vehicle['make']} {vehicle['model']}",
                font=("Segoe UI", 11)
            ).pack(pady=10)

            status_var = tk.StringVar(value=vehicle['status'])
            status_combo = ttk.Combobox(
                dialog,
                textvariable=status_var,
                values=["available", "rented", "maintenance", "reserved"],
                width=15,
                state="readonly"
            )
            status_combo.pack(pady=10)

            def apply_status():
                result = self.controller.update_status(vehicle_id, status_var.get())
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    dialog.destroy()
                    self.load_vehicles()
                else:
                    messagebox.showerror("Error", result['message'])

            tk.Button(
                dialog,
                text="Update Status",
                command=apply_status,
                font=("Segoe UI", 10, "bold"),
                bg="#3498db",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=5
            ).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==========================================================
    # DELETE - Only for admin and manager
    # ==========================================================

    def delete_vehicle(self):
        """Delete vehicle - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to delete vehicles.")
            return

        vehicle_id = self.get_selected_vehicle_id()
        if vehicle_id is None:
            return

        try:
            vehicle = self.controller.get_vehicle_by_id(vehicle_id)
            if not vehicle:
                return

            if not messagebox.askyesno(
                "Confirm Delete",
                f'Are you sure you want to delete "{vehicle["make"]} {vehicle["model"]}"?\n\n'
                f"This action cannot be undone!"
            ):
                return

            result = self.controller.delete_vehicle(vehicle_id)
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.clear_form()
                self.load_vehicles()
            else:
                messagebox.showerror("Error", result['message'])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==========================================================
    # BACK TO DASHBOARD
    # ==========================================================

    def go_back(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        if self.dashboard_controller:
            from views.main_dashboard import MainDashboard
            MainDashboard(self.parent, self.user, self.dashboard_controller)

    # ==========================================================
    # EXPORT - All users can export
    # ==========================================================

    def export_csv(self):
        try:
            vehicles = self.controller.get_all_vehicles()
            if not vehicles:
                messagebox.showwarning("No Data", "No vehicles to export.")
                return
            self.controller.export_to_csv(vehicles)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def export_excel(self):
        try:
            vehicles = self.controller.get_all_vehicles()
            if not vehicles:
                messagebox.showwarning("No Data", "No vehicles to export.")
                return
            self.controller.export_to_excel(vehicles)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def export_pdf(self):
        try:
            vehicles = self.controller.get_all_vehicles()
            if not vehicles:
                messagebox.showwarning("No Data", "No vehicles to export.")
                return
            self.controller.export_to_pdf(vehicles)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")