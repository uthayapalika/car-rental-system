# views/vehicle_categories_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.vehicle_category_controller import VehicleCategoryController  # This should work now


class VehicleCategoriesView:
    def __init__(self, parent, db, user, dashboard_controller=None):
        self.parent = parent
        self.db = db
        self.user = user
        self.dashboard_controller = dashboard_controller

        # Database/controller
        self.controller = VehicleCategoryController(db)

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
        self.name_var = tk.StringVar()
        self.base_rate_var = tk.StringVar()
        self.late_fee_var = tk.StringVar()
        self.status_var = tk.StringVar(value="1")

        self.setup_ui()
        self.load_categories()
    
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

        # Title with view-only indicator for staff
        title_text = "🚗 Vehicle Categories Management"
        if self.is_view_only:
            title_text = "🚗 Vehicle Categories Management (View Only)"
            
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
            text="Active: 0",
            font=("Segoe UI", 12),
            fg="#27ae60",
            bg="#f0f0f0"
        )

        self.active_label.pack(
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

        self.search_var = tk.StringVar()

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
            command=self.load_categories,
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

        # Add New Category button - Only for admin and manager
        if self.can_edit:
            tk.Button(
                button_frame,
                text="➕ Add New Category",
                command=self.clear_form,
                font=("Segoe UI", 10, "bold"),
                bg="#9b59b6",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=7
            ).pack(side=tk.LEFT, padx=5)

        # ------------------------------------------------------
        # ADD / EDIT FORM - Only for admin and manager
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
                text="ℹ️ You are in View-Only mode. You can view and export category data but cannot modify it.",
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
            text=" Add / Edit Vehicle Category ",
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

        # Row 1
        row1 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row1.pack(
            fill=tk.X,
            pady=5
        )

        # Name
        tk.Label(
            row1,
            text="Category Name *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.name_var,
            font=("Segoe UI", 10),
            width=25
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Base rate
        tk.Label(
            row1,
            text="Base Rate ($) *",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.base_rate_var,
            font=("Segoe UI", 10),
            width=15
        ).pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Late fee
        tk.Label(
            row1,
            text="Late Fee ($)",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        tk.Entry(
            row1,
            textvariable=self.late_fee_var,
            font=("Segoe UI", 10),
            width=15
        ).pack(
            side=tk.LEFT
        )

        # Row 2
        row2 = tk.Frame(
            self.form_frame,
            bg="white"
        )

        row2.pack(
            fill=tk.X,
            pady=5
        )

        # Description
        tk.Label(
            row2,
            text="Description",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        self.description_text = tk.Text(
            row2,
            font=("Segoe UI", 10),
            height=3,
            width=60
        )

        self.description_text.pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        # Status
        status_frame = tk.Frame(
            row2,
            bg="white"
        )

        status_frame.pack(
            side=tk.LEFT,
            anchor=tk.N
        )

        tk.Label(
            status_frame,
            text="Status",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            status_frame,
            text="Active",
            variable=self.status_var,
            value="1",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        tk.Radiobutton(
            status_frame,
            text="Inactive",
            variable=self.status_var,
            value="0",
            bg="white"
        ).pack(
            side=tk.LEFT
        )

        # Row 3 buttons
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
            text="➕ Save Category",
            command=self.save_category,
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
            "Name",
            "Description",
            "Base Rate",
            "Late Fee Rate",
            "Status",
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
            "Name": "Name",
            "Description": "Description",
            "Base Rate": "Base Rate ($)",
            "Late Fee Rate": "Late Fee Rate ($)",
            "Status": "Status",
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
            "Name",
            width=150
        )

        self.tree.column(
            "Description",
            width=300
        )

        self.tree.column(
            "Base Rate",
            width=110,
            anchor="center"
        )

        self.tree.column(
            "Late Fee Rate",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "Status",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "Created At",
            width=160,
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

        # Bind events - different behavior based on role
        if self.can_edit:
            # Right-click menu - Only for admin and manager
            self.context_menu = tk.Menu(
                self.parent,
                tearoff=0
            )

            self.context_menu.add_command(
                label="✏️ Edit",
                command=self.edit_selected
            )

            self.context_menu.add_command(
                label="🔄 Toggle Status",
                command=self.toggle_status
            )

            self.context_menu.add_command(
                label="🗑️ Delete",
                command=self.delete_category
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
                lambda event: self.view_category_details()
            )

    # ==========================================================
    # VIEW DETAILS (for view-only users)
    # ==========================================================

    def view_category_details(self):
        """Show category details in a read-only dialog"""
        category_id = self.get_selected_category_id()
        if category_id is None:
            return

        try:
            category = self.controller.get_category_by_id(category_id)
            if not category:
                messagebox.showerror("Error", "Category not found.")
                return

            # Create details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Category Details - {category['name']}")
            dialog.geometry("500x420")
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
                text=f"🚗 {category['name']}",
                font=("Segoe UI", 16, "bold"),
                fg="white",
                bg='#2c3e50'
            ).pack(pady=15)

            # Details
            details_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            status_text = "Active" if category['category_status'] == 1 else "Inactive"
            status_color = "#27ae60" if category['category_status'] == 1 else "#e74c3c"

            details = [
                ("ID", str(category['id'])),
                ("Name", category['name']),
                ("Description", category['description'] or 'No description provided'),
                ("Base Rate", f"${float(category['base_rate']):.2f}"),
                ("Late Fee Rate", f"${float(category['late_fee_rate'] or 0):.2f}"),
                ("Status", status_text),
                ("Created At", category['created_at'][:16] if category['created_at'] else 'N/A')
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
                    width=15,
                    anchor='w'
                ).pack(side=tk.LEFT)
                
                # Apply color to status
                if label == "Status":
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
            messagebox.showerror("Error", f"Could not load category details:\n\n{str(e)}")

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_categories(self):

        try:

            for item in self.tree.get_children():
                self.tree.delete(item)

            categories = self.controller.get_all_categories()

            if categories:

                for row in categories:

                    status = (
                        "🟢 Active"
                        if row["category_status"] == 1
                        else "🔴 Inactive"
                    )

                    created_at = row["created_at"]

                    if created_at:
                        created_at = created_at[:16]
                    else:
                        created_at = "-"

                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            row["id"],
                            row["name"],
                            row["description"] or "-",
                            f"${float(row['base_rate']):.2f}",
                            f"${float(row['late_fee_rate'] or 0):.2f}",
                            status,
                            created_at
                        ),
                        tags=(
                            "active"
                            if row["category_status"] == 1
                            else "inactive",
                        )
                    )

            self.tree.tag_configure(
                "active",
                background="#e8f5e9"
            )

            self.tree.tag_configure(
                "inactive",
                background="#ffebee"
            )

            self.update_stats(categories)

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to load categories:\n\n{str(e)}"
            )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def update_stats(self, categories=None):

        try:

            if categories is None:
                categories = self.controller.get_all_categories()

            total = len(categories)

            active = sum(
                1
                for category in categories
                if category["category_status"] == 1
            )

            self.total_label.config(
                text=f"Total: {total}"
            )

            self.active_label.config(
                text=f"Active: {active}"
            )

        except Exception:
            pass

    # ==========================================================
    # SEARCH
    # ==========================================================

    def on_search(self, *args):

        try:

            search_term = self.search_var.get().strip()

            if search_term:
                categories = self.controller.search_categories(
                    search_term
                )
            else:
                categories = self.controller.get_all_categories()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in categories:

                status = (
                    "🟢 Active"
                    if row["category_status"] == 1
                    else "🔴 Inactive"
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["name"],
                        row["description"] or "-",
                        f"${float(row['base_rate']):.2f}",
                        f"${float(row['late_fee_rate'] or 0):.2f}",
                        status,
                        row["created_at"][:16]
                        if row["created_at"]
                        else "-"
                    )
                )

        except Exception as e:

            print("Search error:", e)

    # ==========================================================
    # SAVE / UPDATE - Only for admin and manager
    # ==========================================================

    def save_category(self):
        """Save category - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify categories.")
            return

        name = self.name_var.get().strip()
        base_rate = self.base_rate_var.get().strip()
        late_fee_rate = self.late_fee_var.get().strip()

        description = self.description_text.get(
            "1.0",
            "end-1c"
        ).strip()

        status = self.status_var.get()

        # Validation
        if not name:

            messagebox.showwarning(
                "Validation",
                "Category name is required."
            )

            return

        if not base_rate:

            messagebox.showwarning(
                "Validation",
                "Base rate is required."
            )

            return

        try:
            float(base_rate)
        except ValueError:

            messagebox.showwarning(
                "Validation",
                "Base rate must be a number."
            )

            return

        if late_fee_rate:

            try:
                float(late_fee_rate)
            except ValueError:

                messagebox.showwarning(
                    "Validation",
                    "Late fee rate must be a number."
                )

                return

        if not late_fee_rate:
            late_fee_rate = "0"

        data = {
            "name": name,
            "description": description,
            "base_rate": base_rate,
            "late_fee_rate": late_fee_rate,
            "status": status
        }

        try:

            # UPDATE
            if self.editing_id is not None:

                result = self.controller.update_category(
                    self.editing_id,
                    data
                )

                if result["success"]:

                    messagebox.showinfo(
                        "Success",
                        result["message"]
                    )

                    self.clear_form()
                    self.load_categories()

                else:

                    messagebox.showerror(
                        "Error",
                        result["message"]
                    )

            # ADD
            else:

                result = self.controller.add_category(
                    data
                )

                if result["success"]:

                    messagebox.showinfo(
                        "Success",
                        result["message"]
                    )

                    self.clear_form()
                    self.load_categories()

                else:

                    messagebox.showerror(
                        "Error",
                        result["message"]
                    )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to save category:\n\n{str(e)}"
            )

    # ==========================================================
    # CLEAR FORM - Only for admin and manager
    # ==========================================================

    def clear_form(self):
        """Clear form - only for admin and manager"""
        if not self.can_edit:
            return

        self.editing_id = None

        self.name_var.set("")
        self.base_rate_var.set("")
        self.late_fee_var.set("")
        self.status_var.set("1")

        self.description_text.delete(
            "1.0",
            tk.END
        )

        if hasattr(self, 'save_button'):
            self.save_button.config(
                text="➕ Save Category"
            )

    # ==========================================================
    # EDIT - Only for admin and manager
    # ==========================================================

    def edit_selected(self):
        """Edit selected category - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to edit categories.")
            return

        category_id = self.get_selected_category_id()

        if category_id is None:
            return

        try:

            category = self.controller.get_category_by_id(
                category_id
            )

            if not category:

                messagebox.showerror(
                    "Error",
                    "Category not found."
                )

                return

            self.editing_id = category_id

            self.name_var.set(
                category["name"]
            )

            self.base_rate_var.set(
                str(category["base_rate"])
            )

            self.late_fee_var.set(
                str(category["late_fee_rate"] or 0)
            )

            self.status_var.set(
                str(category["category_status"])
            )

            self.description_text.delete(
                "1.0",
                tk.END
            )

            self.description_text.insert(
                "1.0",
                category["description"] or ""
            )

            self.save_button.config(
                text="✏️ Update Category"
            )

            # Scroll to form
            self.form_frame.focus_set()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not load category:\n\n{str(e)}"
            )

    # ==========================================================
    # SELECTED ID
    # ==========================================================

    def get_selected_category_id(self):

        selection = self.tree.selection()

        if not selection:

            messagebox.showwarning(
                "No Selection",
                "Please select a category first."
            )

            return None

        item = self.tree.item(
            selection[0]
        )

        return item["values"][0]

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
    # TOGGLE STATUS - Only for admin and manager
    # ==========================================================

    def toggle_status(self):
        """Toggle category status - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to modify category status.")
            return

        category_id = self.get_selected_category_id()

        if category_id is None:
            return

        try:

            category = self.controller.get_category_by_id(
                category_id
            )

            if not category:
                return

            current_status = category["category_status"]

            action = (
                "deactivate"
                if current_status == 1
                else "activate"
            )

            if not messagebox.askyesno(
                "Confirm",
                f"Are you sure you want to {action} "
                f'"{category["name"]}"?'
            ):
                return

            result = self.controller.toggle_status(
                category_id,
                current_status
            )

            if result["success"]:

                messagebox.showinfo(
                    "Success",
                    result["message"]
                )

                self.load_categories()

            else:

                messagebox.showerror(
                    "Error",
                    result["message"]
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # ==========================================================
    # DELETE - Only for admin and manager
    # ==========================================================

    def delete_category(self):
        """Delete category - only for admin and manager"""
        if not self.can_edit:
            messagebox.showwarning("Access Denied", "You do not have permission to delete categories.")
            return

        category_id = self.get_selected_category_id()

        if category_id is None:
            return

        try:

            category = self.controller.get_category_by_id(
                category_id
            )

            if not category:
                return

            if not messagebox.askyesno(
                "Confirm Delete",
                f'Are you sure you want to delete '
                f'the category "{category["name"]}"?\n\n'
                f"This action cannot be undone!"
            ):
                return

            result = self.controller.delete_category(
                category_id
            )

            if result["success"]:

                messagebox.showinfo(
                    "Success",
                    result["message"]
                )

                self.clear_form()
                self.load_categories()

            else:

                messagebox.showerror(
                    "Error",
                    result["message"]
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

        # Remove current page
        for widget in self.parent.winfo_children():
            widget.destroy()

        # IMPORTANT:
        # Use the ORIGINAL dashboard controller.
        # Do NOT pass self.db here.
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

        try:

            categories = self.controller.get_all_categories()

            if not categories:

                messagebox.showwarning(
                    "No Data",
                    "No categories to export."
                )

                return

            self.controller.export_to_csv(
                categories
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )

    def export_excel(self):

        try:

            categories = self.controller.get_all_categories()

            if not categories:

                messagebox.showwarning(
                    "No Data",
                    "No categories to export."
                )

                return

            self.controller.export_to_excel(
                categories
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )

    def export_pdf(self):

        try:

            categories = self.controller.get_all_categories()

            if not categories:

                messagebox.showwarning(
                    "No Data",
                    "No categories to export."
                )

                return

            self.controller.export_to_pdf(
                categories
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to export:\n{str(e)}"
            )