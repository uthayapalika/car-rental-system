# views/customer_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.customer_controller import CustomerController


class CustomerView:
    def __init__(self, parent, db, user, dashboard_controller=None):
        self.parent = parent
        self.db = db  # This is the database connection object
        self.user = user
        self.dashboard_controller = dashboard_controller

        # Database/controller
        self.controller = CustomerController()

        # Customer model - Fix: Pass the db_path string, not the connection object
        from models.customer_model import CustomerModel
        # Check if db is a string (path) or a connection object
        if isinstance(db, str):
            self.model = CustomerModel(db)
        else:
            # If db is a connection object, get the path or use default
            # Try to get the path from the connection
            try:
                db_path = db.db_path if hasattr(db, 'db_path') else "car_rental_system.db"
                self.model = CustomerModel(db_path)
            except:
                self.model = CustomerModel("car_rental_system.db")

        self.controller.set_model(self.model)
        self.controller.set_view(self)

        # Editing state
        self.editing_id = None

        # Form variables - Only customer info
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.driver_license_var = tk.StringVar()
        self.address_var = tk.StringVar()

        # Search
        self.search_var = tk.StringVar()

        self.setup_ui()
        self.load_customers()

    # ==========================================================
    # MAIN UI
    # ==========================================================

    def setup_ui(self):
        self.parent.configure(bg="#f0f0f0")

        # Main container
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
        # HEADER
        # ------------------------------------------------------

        title_frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )
        title_frame.pack(
            fill=tk.X,
            pady=(0, 15)
        )

        tk.Label(
            title_frame,
            text="👤 Customer Management",
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

        self.active_label = tk.Label(
            stats_frame,
            text="Customers: 0",
            font=("Segoe UI", 12),
            fg="#27ae60",
            bg="#f0f0f0"
        )
        self.active_label.pack(
            side=tk.LEFT,
            padx=10
        )

        # ------------------------------------------------------
        # SEARCH
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

        self.search_var.trace_add(
            "write",
            self.on_search
        )

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=35
        )
        self.search_entry.pack(
            side=tk.LEFT
        )

        # ------------------------------------------------------
        # ACTION BUTTONS
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
            command=self.load_customers,
            font=("Segoe UI", 10),
            bg="#3498db",
            fg="white",
            cursor="hand2",
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
            font=("Segoe UI", 10),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
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
            font=("Segoe UI", 10),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
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
            font=("Segoe UI", 10),
            bg="#e74c3c",
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
        # EDIT FORM (Only customer info, no username/password)
        # ------------------------------------------------------

        self.create_form()

        # ------------------------------------------------------
        # TABLE
        # ------------------------------------------------------

        self.create_table()

    # ==========================================================
    # EDIT FORM (No username/password fields)
    # ==========================================================

    def create_form(self):

        self.form_frame = tk.LabelFrame(
            self.main_container,
            text=" Edit Customer Information ",
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
        # ROW 1
        # ------------------------------------------------------

        row1 = tk.Frame(
            self.form_frame,
            bg="white"
        )
        row1.pack(
            fill=tk.X,
            pady=5
        )

        # First Name
        tk.Label(
            row1,
            text="First Name *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.first_name_var,
            font=("Segoe UI", 10),
            width=15
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Last Name
        tk.Label(
            row1,
            text="Last Name *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.last_name_var,
            font=("Segoe UI", 10),
            width=15
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Email
        tk.Label(
            row1,
            text="Email *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.email_var,
            font=("Segoe UI", 10),
            width=25
        ).pack(
            side=tk.LEFT
        )

        # ------------------------------------------------------
        # ROW 2
        # ------------------------------------------------------

        row2 = tk.Frame(
            self.form_frame,
            bg="white"
        )
        row2.pack(
            fill=tk.X,
            pady=5
        )

        # Phone
        tk.Label(
            row2,
            text="Phone *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row2,
            textvariable=self.phone_var,
            font=("Segoe UI", 10),
            width=15
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Driver License
        tk.Label(
            row2,
            text="Driver License *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row2,
            textvariable=self.driver_license_var,
            font=("Segoe UI", 10),
            width=18
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Address
        tk.Label(
            row2,
            text="Address",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row2,
            textvariable=self.address_var,
            font=("Segoe UI", 10),
            width=30
        ).pack(
            side=tk.LEFT
        )

        # ------------------------------------------------------
        # ROW 3 - BUTTONS
        # ------------------------------------------------------

        row3 = tk.Frame(
            self.form_frame,
            bg="white"
        )
        row3.pack(
            fill=tk.X,
            pady=(8, 0)
        )

        self.save_button = tk.Button(
            row3,
            text="✏️ Update Customer",
            command=self.update_customer_info,
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=25,
            pady=7
        )

        self.save_button.pack(
            side=tk.RIGHT,
            padx=5
        )

        tk.Button(
            row3,
            text="Clear",
            command=self.clear_form,
            font=("Segoe UI", 10),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=25,
            pady=7
        ).pack(
            side=tk.RIGHT,
            padx=5
        )

        # Disable form by default (enable when editing)
        self.set_form_state("disabled")

    def set_form_state(self, state):
        """Enable or disable form fields"""
        for child in self.form_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Entry):
                        grandchild.config(state=state)

    # ==========================================================
    # TABLE
    # ==========================================================

    def create_table(self):

        table_frame = tk.Frame(
            self.main_container,
            bg="#f0f0f0"
        )

        table_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        scroll_y = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL
        )
        scroll_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        scroll_x = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL
        )
        scroll_x.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        columns = (
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "Driver License",
            "Address",
            "Created At"
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
            "First Name": "First Name",
            "Last Name": "Last Name",
            "Email": "Email",
            "Phone": "Phone",
            "Driver License": "Driver License",
            "Address": "Address",
            "Created At": "Created At"
        }

        for column, heading in headings.items():
            self.tree.heading(
                column,
                text=heading
            )

        self.tree.column(
            "ID",
            width=50,
            anchor="center"
        )

        self.tree.column(
            "First Name",
            width=120
        )

        self.tree.column(
            "Last Name",
            width=120
        )

        self.tree.column(
            "Email",
            width=200
        )

        self.tree.column(
            "Phone",
            width=130,
            anchor="center"
        )

        self.tree.column(
            "Driver License",
            width=140,
            anchor="center"
        )

        self.tree.column(
            "Address",
            width=250
        )

        self.tree.column(
            "Created At",
            width=150,
            anchor="center"
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

        # Right-click menu
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
            command=self.delete_customer
        )

        self.tree.bind(
            "<Button-3>",
            self.show_context_menu
        )

        self.tree.bind(
            "<Double-1>",
            lambda event: self.edit_selected()
        )

    # ==========================================================
    # LOAD CUSTOMERS
    # ==========================================================

    def load_customers(self):

        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            customers = self.model.get_all_customers()

            if customers:
                for row in customers:
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            row.get("customer_id", ""),
                            row.get("first_name", ""),
                            row.get("last_name", ""),
                            row.get("email", ""),
                            row.get("phone", ""),
                            row.get("driver_license_num", ""),
                            row.get("address", ""),
                            row.get("created_at", "")
                        )
                    )

            self.update_stats(customers)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load customers:\n\n{str(e)}"
            )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def update_stats(self, customers=None):

        try:
            if customers is None:
                customers = self.model.get_all_customers()

            if customers is None:
                customers = []

            total = len(customers)

            self.total_label.config(
                text=f"Total: {total}"
            )

            self.active_label.config(
                text=f"Customers: {total}"
            )

        except Exception as e:
            print(
                f"Error updating customer stats: {e}"
            )

    # ==========================================================
    # SEARCH
    # ==========================================================

    def on_search(self, *args):

        try:
            search_term = (
                self.search_var.get()
                .strip()
                .lower()
            )

            customers = self.model.get_all_customers()

            if search_term:
                customers = [
                    customer
                    for customer in customers
                    if (
                        search_term in str(
                            customer.get("customer_id", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("first_name", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("last_name", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("email", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("phone", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("driver_license_num", "")
                        ).lower()
                        or
                        search_term in str(
                            customer.get("address", "")
                        ).lower()
                    )
                ]

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in customers:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("customer_id", ""),
                        row.get("first_name", ""),
                        row.get("last_name", ""),
                        row.get("email", ""),
                        row.get("phone", ""),
                        row.get("driver_license_num", ""),
                        row.get("address", ""),
                        row.get("created_at", "")
                    )
                )

            self.update_stats(customers)

        except Exception as e:
            print(
                "Customer search error:",
                e
            )

    # ==========================================================
    # UPDATE CUSTOMER INFO (Only customer data)
    # ==========================================================

    def update_customer_info(self):
        """Update only customer information (no username/password)"""

        if self.editing_id is None:
            messagebox.showwarning(
                "No Selection",
                "Please select a customer to edit."
            )
            return

        data = {
            "first_name": self.first_name_var.get().strip(),
            "last_name": self.last_name_var.get().strip(),
            "email": self.email_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "driver_license_num": self.driver_license_var.get().strip(),
            "address": self.address_var.get().strip()
        }

        # Validation
        if not data["first_name"]:
            messagebox.showwarning(
                "Validation",
                "First name is required."
            )
            return

        if not data["last_name"]:
            messagebox.showwarning(
                "Validation",
                "Last name is required."
            )
            return

        if not data["email"]:
            messagebox.showwarning(
                "Validation",
                "Email is required."
            )
            return

        if not data["phone"]:
            messagebox.showwarning(
                "Validation",
                "Phone number is required."
            )
            return

        if not data["driver_license_num"]:
            messagebox.showwarning(
                "Validation",
                "Driver license number is required."
            )
            return

        try:
            # Use the model's get_connection method
            conn = self.model.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE customers
                SET
                    first_name = ?,
                    last_name = ?,
                    email = ?,
                    phone = ?,
                    driver_license_num = ?,
                    address = ?,
                    updated_at = ?
                WHERE customer_id = ?
                """,
                (
                    data["first_name"],
                    data["last_name"],
                    data["email"],
                    data["phone"],
                    data["driver_license_num"],
                    data["address"],
                    self.get_current_datetime(),
                    self.editing_id
                )
            )

            conn.commit()
            cursor.close()

            messagebox.showinfo(
                "Success",
                "Customer information updated successfully!"
            )

            self.clear_form()
            self.load_customers()

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: customers.email" in str(e):
                messagebox.showerror("Error", "Email already exists!")
            elif "UNIQUE constraint failed: customers.phone" in str(e):
                messagebox.showerror("Error", "Phone number already exists!")
            elif "UNIQUE constraint failed: customers.driver_license_num" in str(e):
                messagebox.showerror("Error", "Driver license number already exists!")
            else:
                messagebox.showerror("Error", f"Database error: {str(e)}")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not update customer:\n\n{str(e)}"
            )

    # ==========================================================
    # CURRENT DATETIME
    # ==========================================================

    def get_current_datetime(self):

        from datetime import datetime

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # ==========================================================
    # CLEAR FORM
    # ==========================================================

    def clear_form(self):

        self.editing_id = None

        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.driver_license_var.set("")
        self.address_var.set("")

        self.set_form_state("disabled")
        self.save_button.config(
            text="✏️ Update Customer"
        )

    # ==========================================================
    # EDIT
    # ==========================================================

    def edit_selected(self):

        customer_id = self.get_selected_customer_id()

        if customer_id is None:
            return

        try:
            customer = self.model.get_customer_by_id(
                customer_id
            )

            if not customer:
                messagebox.showerror(
                    "Error",
                    "Customer not found."
                )
                return

            self.editing_id = customer_id

            self.first_name_var.set(
                customer.get("first_name", "")
            )

            self.last_name_var.set(
                customer.get("last_name", "")
            )

            self.email_var.set(
                customer.get("email", "")
            )

            self.phone_var.set(
                customer.get("phone", "")
            )

            self.driver_license_var.set(
                customer.get(
                    "driver_license_num",
                    ""
                )
            )

            self.address_var.set(
                customer.get("address", "")
            )

            # Enable form for editing
            self.set_form_state("normal")
            self.save_button.config(
                text="✏️ Update Customer"
            )

            self.form_frame.focus_set()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not load customer:\n\n{str(e)}"
            )

    # ==========================================================
    # SELECTED ID
    # ==========================================================

    def get_selected_customer_id(self):

        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select a customer first."
            )
            return None

        item = self.tree.item(
            selection[0]
        )

        return item["values"][0]

    # ==========================================================
    # CONTEXT MENU
    # ==========================================================

    def show_context_menu(self, event):

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
    # DELETE
    # ==========================================================

    def delete_customer(self):

        customer_id = self.get_selected_customer_id()

        if customer_id is None:
            return

        try:
            customer = self.model.get_customer_by_id(
                customer_id
            )

            if not customer:
                return

            customer_name = (
                f"{customer.get('first_name', '')} "
                f"{customer.get('last_name', '')}"
            )

            if not messagebox.askyesno(
                "Confirm Delete",
                f'Are you sure you want to delete '
                f'"{customer_name}"?\n\n'
                f"This will also delete their user account.\n\n"
                f"This action cannot be undone!"
            ):
                return

            success, message = (
                self.model.delete_customer(
                    customer_id
                )
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    message
                )

                self.clear_form()
                self.load_customers()

            else:
                messagebox.showerror(
                    "Error",
                    message
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    # ==========================================================
    # BACK TO DASHBOARD
    # ==========================================================

    def go_back(self):

        for widget in self.parent.winfo_children():
            widget.destroy()

        if self.dashboard_controller:
            from views.main_dashboard import MainDashboard

            MainDashboard(
                self.parent,
                self.user,
                self.dashboard_controller
            )

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_csv(self):

        try:
            customers = self.model.get_all_customers()

            if not customers:
                messagebox.showwarning(
                    "No Data",
                    "No customers to export."
                )
                return

            if hasattr(
                self.controller,
                "export_to_csv"
            ):
                self.controller.export_to_csv(
                    customers
                )
            else:
                self.export_customers_csv(
                    customers
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )

    # ==========================================================
    # EXPORT EXCEL
    # ==========================================================

    def export_excel(self):

        try:
            customers = self.model.get_all_customers()

            if not customers:
                messagebox.showwarning(
                    "No Data",
                    "No customers to export."
                )
                return

            if hasattr(
                self.controller,
                "export_to_excel"
            ):
                self.controller.export_to_excel(
                    customers
                )
            else:
                self.export_customers_excel(
                    customers
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )

    # ==========================================================
    # EXPORT PDF
    # ==========================================================

    def export_pdf(self):

        try:
            customers = self.model.get_all_customers()

            if not customers:
                messagebox.showwarning(
                    "No Data",
                    "No customers to export."
                )
                return

            if hasattr(
                self.controller,
                "export_to_pdf"
            ):
                self.controller.export_to_pdf(
                    customers
                )
            else:
                self.export_customers_pdf(
                    customers
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )

    # ==========================================================
    # BASIC CSV EXPORT
    # ==========================================================

    def export_customers_csv(self, customers):

        import csv
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            title="Export Customers",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if not file_path:
            return

        columns = [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "driver_license_num",
            "address",
            "created_at"
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=columns
            )

            writer.writeheader()

            for customer in customers:
                writer.writerow({
                    column:
                        customer.get(column, "")
                    for column in columns
                })

        messagebox.showinfo(
            "Export Complete",
            "Customers exported successfully."
        )

    # ==========================================================
    # BASIC EXCEL EXPORT
    # ==========================================================

    def export_customers_excel(self, customers):

        from tkinter import filedialog

        try:
            import openpyxl
        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Please install openpyxl:\n\n"
                "pip install openpyxl"
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Customers",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Files", "*.xlsx")
            ]
        )

        if not file_path:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Customers"

        headers = [
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "Driver License",
            "Address",
            "Created At"
        ]

        sheet.append(headers)

        for customer in customers:
            sheet.append([
                customer.get("customer_id", ""),
                customer.get("first_name", ""),
                customer.get("last_name", ""),
                customer.get("email", ""),
                customer.get("phone", ""),
                customer.get("driver_license_num", ""),
                customer.get("address", ""),
                customer.get("created_at", "")
            ])

        workbook.save(file_path)

        messagebox.showinfo(
            "Export Complete",
            "Customers exported successfully."
        )

    # ==========================================================
    # BASIC PDF EXPORT
    # ==========================================================

    def export_customers_pdf(self, customers):

        from tkinter import filedialog

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle
            )
        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Please install reportlab:\n\n"
                "pip install reportlab"
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Customers",
            defaultextension=".pdf",
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not file_path:
            return

        document = SimpleDocTemplate(
            file_path,
            pagesize=landscape(A4)
        )

        data = [[
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "Driver License",
            "Address"
        ]]

        for customer in customers:
            data.append([
                customer.get("customer_id", ""),
                customer.get("first_name", ""),
                customer.get("last_name", ""),
                customer.get("email", ""),
                customer.get("phone", ""),
                customer.get("driver_license_num", ""),
                customer.get("address", "")
            ])

        table = Table(
            data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        document.build([table])

        messagebox.showinfo(
            "Export Complete",
            "Customers exported successfully."
        )

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def close(self):

        try:
            self.model.close()
        except Exception:
            pass