# views/maintenance_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from controllers.maintenance_controller import MaintenanceController


class MaintenanceView:
    def __init__(self, parent, db, user, dashboard_controller=None):
        self.parent = parent
        self.db = db
        self.user = user
        self.dashboard_controller = dashboard_controller

        # Database/controller
        self.controller = MaintenanceController(db)

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
        self.vehicle_id_var = tk.StringVar()
        self.maintenance_type_var = tk.StringVar()
        self.service_date_var = tk.StringVar()
        self.odometer_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.provider_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.status_var = tk.StringVar(value="pending")
        self.next_service_var = tk.StringVar()

        # Vehicle list
        self.vehicles = []

        self.setup_ui()
        self.load_vehicles()
        self.load_maintenance()

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
        title_text = "🛠️ Maintenance Management"
        if self.is_view_only:
            title_text = "🛠️ Maintenance Management (View Only)"
            
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

        self.pending_label = tk.Label(
            stats_frame,
            text="Pending: 0",
            font=("Segoe UI", 12),
            fg="#f39c12",
            bg="#f0f0f0"
        )
        self.pending_label.pack(side=tk.LEFT, padx=10)

        self.completed_label = tk.Label(
            stats_frame,
            text="Completed: 0",
            font=("Segoe UI", 12),
            fg="#27ae60",
            bg="#f0f0f0"
        )
        self.completed_label.pack(side=tk.LEFT, padx=10)

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
            width=30
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
            values=["all", "pending", "completed", "cancelled"],
            width=12,
            state="readonly"
        )
        status_filter.pack(side=tk.LEFT)
        status_filter.bind("<<ComboboxSelected>>", lambda e: self.load_maintenance())

        # ------------------------------------------------------
        # ACTION BUTTONS
        # ------------------------------------------------------

        button_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.load_maintenance,
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

        # Add New Record button - Only for admin and manager
        if self.can_edit:
            tk.Button(
                button_frame,
                text="➕ Add New Record",
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
                text="ℹ️ You are in View-Only mode. You can view and export maintenance records but cannot modify them.",
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
            text=" Add / Edit Maintenance Record ",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=10
        )
        self.form_frame.pack(fill=tk.X, pady=(0, 15))

        # Row 1: Vehicle, Maintenance Type
        row1 = tk.Frame(self.form_frame, bg="white")
        row1.pack(fill=tk.X, pady=5)

        # Vehicle
        tk.Label(row1, text="Vehicle *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.vehicle_combo = ttk.Combobox(
            row1,
            textvariable=self.vehicle_id_var,
            width=25,
            state="readonly"
        )
        self.vehicle_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Maintenance Type - DROPDOWN
        tk.Label(row1, text="Maintenance Type *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.type_combo = ttk.Combobox(
            row1,
            textvariable=self.maintenance_type_var,
            width=20,
            state="readonly"
        )
        self.type_combo['values'] = [
            "Oil Change",
            "Tire Replacement",
            "Brake Service",
            "Engine Service",
            "Transmission Service",
            "Battery Replacement",
            "Wheel Alignment",
            "AC Service",
            "General Inspection",
            "Body Repair",
            "Paint Work",
            "Accident Repair",
            "Routine Service",
            "Major Service",
            "Other"
        ]
        self.type_combo.pack(side=tk.LEFT)

        # Row 2: Service Date, Odometer, Cost
        row2 = tk.Frame(self.form_frame, bg="white")
        row2.pack(fill=tk.X, pady=5)

        # Service Date
        tk.Label(row2, text="Service Date *", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = tk.Entry(row2, textvariable=self.service_date_var, font=("Segoe UI", 10), width=15)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 20))
        # Set default date
        self.service_date_var.set(datetime.now().strftime("%Y-%m-%d"))

        # Odometer
        tk.Label(row2, text="Odometer", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.odometer_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT, padx=(0, 20))

        # Cost
        tk.Label(row2, text="Cost ($)", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.cost_var, font=("Segoe UI", 10), width=12).pack(side=tk.LEFT)

        # Row 3: Provider, Status
        row3 = tk.Frame(self.form_frame, bg="white")
        row3.pack(fill=tk.X, pady=5)

        # Service Provider
        tk.Label(row3, text="Provider", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row3, textvariable=self.provider_var, font=("Segoe UI", 10), width=20).pack(side=tk.LEFT, padx=(0, 20))

        # Status
        tk.Label(row3, text="Status", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        status_combo = ttk.Combobox(
            row3,
            textvariable=self.status_var,
            values=["pending", "completed", "cancelled"],
            width=12,
            state="readonly"
        )
        status_combo.pack(side=tk.LEFT)

        # Row 4: Description
        row4 = tk.Frame(self.form_frame, bg="white")
        row4.pack(fill=tk.X, pady=5)

        tk.Label(row4, text="Description", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.desc_entry = tk.Text(row4, font=("Segoe UI", 10), height=3, width=50)
        self.desc_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Row 5: Next Service Due
        row5 = tk.Frame(self.form_frame, bg="white")
        row5.pack(fill=tk.X, pady=5)

        tk.Label(row5, text="Next Service Due", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.next_service_entry = tk.Entry(row5, textvariable=self.next_service_var, font=("Segoe UI", 10), width=15)
        self.next_service_entry.pack(side=tk.LEFT)

        # Row 6: Buttons
        row6 = tk.Frame(self.form_frame, bg="white")
        row6.pack(fill=tk.X, pady=(8, 0))

        self.save_button = tk.Button(
            row6,
            text="➕ Save Record",
            command=self.save_record,
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

        # Set default next service date (6 months from now)
        default_next = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        self.next_service_var.set(default_next)

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
            "ID", "Vehicle", "Type", "Date", "Odometer", 
            "Cost", "Provider", "Status", "Next Service"
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
            "Vehicle": "Vehicle",
            "Type": "Maintenance Type",
            "Date": "Service Date",
            "Odometer": "Odometer",
            "Cost": "Cost ($)",
            "Provider": "Provider",
            "Status": "Status",
            "Next Service": "Next Service Due"
        }

        for column, heading in headings.items():
            self.tree.heading(column, text=heading)

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Vehicle", width=200)
        self.tree.column("Type", width=150)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Odometer", width=80, anchor="center")
        self.tree.column("Cost", width=90, anchor="center")
        self.tree.column("Provider", width=150)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Next Service", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Right-click menu - Only for admin and manager
        if self.can_edit:
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="✏️ Edit", command=self.edit_selected)
            self.context_menu.add_command(label="🔄 Change Status", command=self.change_status)
            self.context_menu.add_command(label="🗑️ Delete", command=self.delete_record)
            self.tree.bind("<Button-3>", self.show_context_menu)
            self.tree.bind("<Double-1>", lambda event: self.edit_selected())
        else:
            # View-only users can double-click to view details
            self.tree.bind("<Double-1>", lambda event: self.view_record_details())

    # ==========================================================
    # VIEW DETAILS (for view-only users)
    # ==========================================================

    def view_record_details(self):
        """Show maintenance record details in a read-only dialog"""
        record_id = self.get_selected_id()
        if record_id is None:
            return

        try:
            all_records = self.controller.get_all()
            record = None
            for r in all_records:
                if r['maintenance_id'] == record_id:
                    record = r
                    break

            if not record:
                messagebox.showerror("Error", "Record not found.")
                return

            # Create details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Maintenance Record #{record_id}")
            dialog.geometry("500x450")
            dialog.resizable(False, False)
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Set background
            dialog.configure(bg='#f0f0f0')

            # Header
            header_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"
            tk.Label(
                header_frame,
                text=f"🛠️ {record['maintenance_type']}",
                font=("Segoe UI", 16, "bold"),
                fg="white",
                bg='#2c3e50'
            ).pack(pady=15)

            # Details
            details_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            details = [
                ("ID", str(record['maintenance_id'])),
                ("Vehicle", vehicle_name),
                ("Type", record['maintenance_type']),
                ("Service Date", record['service_date']),
                ("Odometer", str(record['odometer_reading'] if record['odometer_reading'] else 0)),
                ("Cost", f"${record['cost']:.2f}"),
                ("Provider", record['service_provider'] or 'N/A'),
                ("Status", record['status'].title()),
                ("Next Service Due", record['next_service_due'] or 'Not set'),
                ("Description", record['description'] or 'No description provided')
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
                    width=16,
                    anchor='w'
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    row_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    bg='white',
                    fg='#34495e',
                    wraplength=300,
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
            messagebox.showerror("Error", f"Could not load record details:\n\n{str(e)}")

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_vehicles(self):
        """Load vehicles into combobox"""
        try:
            from models.vehicle_model import VehicleModel
            model = VehicleModel(self.db)
            self.vehicles = model.get_all()

            # Clear and populate combobox - only if form exists
            if hasattr(self, 'vehicle_combo'):
                values = [f"{v['id']}: {v['make']} {v['model']} ({v['license_plate']})" for v in self.vehicles]
                self.vehicle_combo['values'] = values

                if values:
                    self.vehicle_combo.current(0)
        except Exception as e:
            print(f"Error loading vehicles: {e}")

    def load_maintenance(self):
        """Load maintenance records into treeview"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Apply status filter
            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "all":
                records = self.controller.get_by_status(status_filter)
            else:
                records = self.controller.get_all()

            # Status colors
            status_colors = {
                'pending': '#fff3e0',    # Orange
                'completed': '#e8f5e9',  # Green
                'cancelled': '#ffebee'   # Red
            }

            if records:
                for row in records:
                    vehicle_name = f"{row['make']} {row['model']}" if 'make' in row.keys() else ''
                    status = row['status'].title()
                    tags = (row['status'],)

                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            row['maintenance_id'],
                            vehicle_name,
                            row['maintenance_type'],
                            row['service_date'],
                            row['odometer_reading'] if row['odometer_reading'] else 0,
                            f"${row['cost']:.2f}",
                            row['service_provider'] or '',
                            status,
                            row['next_service_due'] or ''
                        ),
                        tags=tags
                    )

            # Configure tags for color coding
            for status, color in status_colors.items():
                self.tree.tag_configure(status, background=color)

            self.update_stats(records)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maintenance records:\n\n{str(e)}")

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def update_stats(self, records=None):
        try:
            if records is None:
                records = self.controller.get_all()

            total = len(records)
            pending = sum(1 for r in records if r['status'] == 'pending')
            completed = sum(1 for r in records if r['status'] == 'completed')

            self.total_label.config(text=f"Total: {total}")
            self.pending_label.config(text=f"Pending: {pending}")
            self.completed_label.config(text=f"Completed: {completed}")
        except Exception:
            pass

    # ==========================================================
    # SEARCH
    # ==========================================================

    def on_search(self, *args):
        try:
            search_term = self.search_var.get().strip()
            
            if search_term:
                all_records = self.controller.get_all()
                records = []
                for r in all_records:
                    vehicle_name = f"{r.get('make', '')} {r.get('model', '')} {r.get('license_plate', '')}"
                    if (search_term.lower() in vehicle_name.lower() or
                        search_term.lower() in r['maintenance_type'].lower() or
                        search_term.lower() in (r['service_provider'] or '').lower()):
                        records.append(r)
            else:
                records = self.controller.get_all()

            # Apply status filter
            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "all":
                records = [r for r in records if r['status'] == status_filter]

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in records:
                vehicle_name = f"{row['make']} {row['model']}" if 'make' in row.keys() else ''
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row['maintenance_id'],
                        vehicle_name,
                        row['maintenance_type'],
                        row['service_date'],
                        row['odometer_reading'] if row['odometer_reading'] else 0,
                        f"${row['cost']:.2f}",
                        row['service_provider'] or '',
                        row['status'].title(),
                        row['next_service_due'] or ''
                    ),
                    tags=(row['status'],)
                )
        except Exception as e:
            print("Search error:", e)

    # ==========================================================
    # SAVE / UPDATE - Only for admin and manager
    # ==========================================================

    def save_record(self):
        """Save record - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify maintenance records.")
            return

        # Get form data
        vehicle_text = self.vehicle_combo.get()
        if not vehicle_text:
            messagebox.showwarning("Validation", "Please select a vehicle.")
            return

        vehicle_id = int(vehicle_text.split(':')[0])

        if not self.maintenance_type_var.get():
            messagebox.showwarning("Validation", "Please select a maintenance type.")
            return

        if not self.service_date_var.get():
            messagebox.showwarning("Validation", "Please enter a service date.")
            return

        data = {
            'vehicle_id': vehicle_id,
            'maintenance_type': self.maintenance_type_var.get(),
            'service_date': self.service_date_var.get(),
            'odometer_reading': self.odometer_var.get() or 0,
            'cost': self.cost_var.get() or 0,
            'service_provider': self.provider_var.get(),
            'description': self.desc_entry.get('1.0', 'end-1c').strip(),
            'status': self.status_var.get(),
            'next_service_due': self.next_service_var.get()
        }

        try:
            if self.editing_id is not None:
                result = self.controller.update(self.editing_id, data)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    self.clear_form()
                    self.load_maintenance()
                else:
                    messagebox.showerror("Error", result['message'])
            else:
                result = self.controller.add(data)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    self.clear_form()
                    self.load_maintenance()
                else:
                    messagebox.showerror("Error", result['message'])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record:\n\n{str(e)}")

    # ==========================================================
    # CLEAR FORM - Only for admin and manager
    # ==========================================================

    def clear_form(self):
        """Clear form - only for admin and manager"""
        if not self.can_edit:
            return

        self.editing_id = None

        self.maintenance_type_var.set("")
        self.service_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.odometer_var.set("")
        self.cost_var.set("")
        self.provider_var.set("")
        self.status_var.set("pending")
        self.next_service_var.set((datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"))
        self.desc_entry.delete('1.0', tk.END)

        if self.vehicles and hasattr(self, 'vehicle_combo'):
            self.vehicle_combo.current(0)

        if hasattr(self, 'save_button'):
            self.save_button.config(text="➕ Save Record")

    # ==========================================================
    # EDIT - Only for admin and manager
    # ==========================================================

    def edit_selected(self):
        """Edit selected record - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to edit maintenance records.")
            return

        record_id = self.get_selected_id()
        if record_id is None:
            return

        try:
            all_records = self.controller.get_all()
            record = None
            for r in all_records:
                if r['maintenance_id'] == record_id:
                    record = r
                    break

            if not record:
                messagebox.showerror("Error", "Record not found.")
                return

            self.editing_id = record_id

            # Set vehicle
            for i, v in enumerate(self.vehicles):
                if v['id'] == record['vehicle_id']:
                    self.vehicle_combo.current(i)
                    break

            self.maintenance_type_var.set(record['maintenance_type'])
            self.service_date_var.set(record['service_date'])
            self.odometer_var.set(str(record['odometer_reading'] if record['odometer_reading'] else 0))
            self.cost_var.set(str(record['cost']))
            self.provider_var.set(record['service_provider'] or '')
            self.status_var.set(record['status'])
            self.next_service_var.set(record['next_service_due'] or '')
            self.desc_entry.delete('1.0', tk.END)
            self.desc_entry.insert('1.0', record['description'] or '')

            self.save_button.config(text="✏️ Update Record")

            # Scroll to form
            self.form_frame.focus_set()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load record:\n\n{str(e)}")

    # ==========================================================
    # SELECTED ID
    # ==========================================================

    def get_selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record first.")
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
        """Change record status - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify maintenance record status.")
            return

        record_id = self.get_selected_id()
        if record_id is None:
            return

        try:
            # Create status dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Change Status")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self.parent)
            dialog.grab_set()

            tk.Label(
                dialog,
                text="Select new status:",
                font=("Segoe UI", 11)
            ).pack(pady=10)

            status_var = tk.StringVar(value="pending")
            status_combo = ttk.Combobox(
                dialog,
                textvariable=status_var,
                values=["pending", "completed", "cancelled"],
                width=15,
                state="readonly"
            )
            status_combo.pack(pady=10)

            def apply_status():
                result = self.controller.update_status(record_id, status_var.get())
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    dialog.destroy()
                    self.load_maintenance()
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

    def delete_record(self):
        """Delete record - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to delete maintenance records.")
            return

        record_id = self.get_selected_id()
        if record_id is None:
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this maintenance record?\n\nThis action cannot be undone!"
        ):
            return

        try:
            result = self.controller.delete(record_id)
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.clear_form()
                self.load_maintenance()
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
            records = self.controller.get_all()
            if not records:
                messagebox.showwarning("No Data", "No records to export.")
                return
            self.controller.export_to_csv(records)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def export_excel(self):
        try:
            records = self.controller.get_all()
            if not records:
                messagebox.showwarning("No Data", "No records to export.")
                return
            self.controller.export_to_excel(records)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def export_pdf(self):
        try:
            records = self.controller.get_all()
            if not records:
                messagebox.showwarning("No Data", "No records to export.")
                return
            self.controller.export_to_pdf(records)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")