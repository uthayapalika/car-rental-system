import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from models.customer_model import CustomerModel
from db_setup import Database  

class MainDashboard:
    def __init__(self, parent, user, controller):
        self.parent = parent
        self.user = user
        self.controller = controller
        self.db = Database()  
        self.time_label = None
        self.running = True
        self.customer_model = None
        self.stat_labels = {}
        
        self.setup_ui()
        
        if self.user.get('role') == 'customer':
            self.parent.after(100, self.load_customer_dashboard)
        else:
            self.load_dashboard_stats()

    def setup_ui(self):
        """Setup the main dashboard interface"""
        self.parent.configure(bg='#f0f0f0')
        
        # Top header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create header with user info"""
        header_frame = tk.Frame(self.parent, bg='#2c3e50', height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🚗 Car Rental System",
            font=('Segoe UI', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT, padx=30, pady=15)
        
        # User info
        user_frame = tk.Frame(header_frame, bg='#2c3e50')
        user_frame.pack(side=tk.RIGHT, padx=30, pady=15)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 {self.user['username']}",
            font=('Segoe UI', 12),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        user_label.pack(side=tk.LEFT, padx=10)
        
        role_label = tk.Label(
            user_frame,
            text=f"({self.user['role'].upper()})",
            font=('Segoe UI', 10, 'bold'),
            fg='#3498db' if self.user['role'] != 'admin' else '#e74c3c',
            bg='#2c3e50'
        )
        role_label.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(
            user_frame,
            text="🔄 Refresh",
            command=self.refresh_dashboard,
            font=('Segoe UI', 10),
            bg='#2ecc71',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        logout_btn = tk.Button(
            user_frame,
            text="🚪 Logout",
            command=self.controller.logout,
            font=('Segoe UI', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        logout_btn.pack(side=tk.LEFT, padx=10)
        
        # Hover effects
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(bg='#27ae60'))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(bg='#2ecc71'))
        logout_btn.bind('<Enter>', lambda e: logout_btn.config(bg='#c0392b'))
        logout_btn.bind('<Leave>', lambda e: logout_btn.config(bg='#e74c3c'))

    def load_customer_dashboard(self):
        """Load customer dashboard for customer users"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        from views.customer_dashboard import CustomerDashboard
        CustomerDashboard(self.parent, self.user, self.controller)

    def create_main_content(self):
        """Create main content area"""
        main_frame = tk.Frame(self.parent, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome message with time
        welcome_frame = tk.Frame(main_frame, bg='#f0f0f0')
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        welcome_label = tk.Label(
            welcome_frame,
            text=f"Welcome, {self.user['username']}!",
            font=('Segoe UI', 24, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        )
        welcome_label.pack(side=tk.LEFT)
        
        # Last updated time
        self.last_updated_label = tk.Label(
            welcome_frame,
            text="Last updated: Just now",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='#f0f0f0'
        )
        self.last_updated_label.pack(side=tk.RIGHT)
        
        # Stats cards
        stats_frame = tk.Frame(main_frame, bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Create stats cards with dynamic data
        stats_data = [
            ("Total Customers", "0", "#3498db", "total_customers"),
            ("Active Rentals", "0", "#2ecc71", "active_rentals"),
            ("Available Vehicles", "0", "#f39c12", "available_vehicles"),
            ("Pending Bookings", "0", "#e74c3c", "pending_bookings")
        ]
        
        for i, (title, value, color, key) in enumerate(stats_data):
            self.create_stat_card(stats_frame, title, value, color, key, i)
        
        # Quick action buttons - ROLE BASED
        self.create_action_buttons(main_frame)

    def create_stat_card(self, parent, title, value, color, key, index):
        """Create a statistics card"""
        card = tk.Frame(
            parent,
            bg='white',
            relief=tk.RAISED,
            bd=1,
            width=250,
            height=100
        )
        card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        card.pack_propagate(False)
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            font=('Segoe UI', 28, 'bold'),
            fg=color,
            bg='white'
        )
        value_label.pack(pady=(15, 5))
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=('Segoe UI', 12),
            fg='#7f8c8d',
            bg='white'
        )
        title_label.pack()
        
        # Store reference to value label for dynamic updates
        self.stat_labels[key] = value_label

    def create_action_buttons(self, parent):
        """Create quick action buttons based on user role"""
        # Use a frame with grid layout for better control
        action_frame = tk.Frame(parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, pady=20)
        
        # Get user role
        role = self.user.get('role', 'staff')
        
        # Define actions based on role
        if role == 'admin':
            # ADMIN: Full access to everything
            actions = [
                ('👥 Customers', self.open_customers),
                ('🚗 Categories', self.open_vehicle_categories),
                ('🚙 Vehicles', self.open_vehicles),
                ('🛠️ Maintenance', self.open_maintenance),
                ('📋 Bookings', self.view_bookings),
                ('💳 Payments', self.view_payments),
                ('👥 Users', self.manage_users),
            ]
        elif role == 'manager':
            # MANAGER: Can view Vehicles, Categories, Maintenance, Bookings, Payments
            actions = [
                ('🚙 Vehicles', self.open_vehicles),
                ('🚗 Categories', self.open_vehicle_categories),
                ('🛠️ Maintenance', self.open_maintenance),
                ('📋 Bookings', self.view_bookings),
                ('💳 Payments', self.view_payments),
                
            ]
        elif role == 'staff':
            # STAFF: Limited access 
            actions = [
                ('📋 Bookings', self.view_bookings),
                ('💳 Payments', self.view_payments),
                ('🛠️ Maintenance', self.open_maintenance)
            ]
        else:
            # Default: basic access
            actions = [
                ('🚙 Vehicles', self.open_vehicles),
                ('📋 Bookings', self.view_bookings),
            ]
        
        # Create buttons in a grid with 4 columns
        row = 0
        col = 0
        max_cols = 4
        
        for text, command in actions:
            btn = tk.Button(
                action_frame,
                text=text,
                command=command,
                font=('Segoe UI', 11),
                bg='white',
                fg='#2c3e50',
                relief=tk.RAISED,
                bd=1,
                width=18,
                height=2,
                cursor='hand2'
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#ecf0f1'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='white'))
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid columns to expand equally
        for i in range(max_cols):
            action_frame.grid_columnconfigure(i, weight=1)

    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.parent, bg='#ecf0f1', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Current time
        self.time_label = tk.Label(
            status_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c5d'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Status message
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c5d'
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Update time
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
            # Widget was destroyed, stop the timer
            self.running = False

    # ==========================================================
    # DYNAMIC DATA LOADING
    # ==========================================================

    def load_dashboard_stats(self):
        """Load statistics from database in background"""
        if self.db is None:
            self.update_status("Database connection not available")
            return
        
        self.update_status("Loading dashboard data...")
        
        # Run in a separate thread to prevent UI freezing
        thread = threading.Thread(target=self._fetch_stats, daemon=True)
        thread.start()

    def _fetch_stats(self):
        """Fetch statistics from database"""
        try:
            # Initialize variables
            total_customers = 0
            active_rentals = 0
            available_vehicles = 0
            pending_bookings = 0
            
            # Get database connection
            conn = self._get_connection()
            
            if conn:
                cursor = conn.cursor()
                
                # ---- GET TOTAL CUSTOMERS ----
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM customers")
                    result = cursor.fetchone()
                    if result:
                        total_customers = result['count']
                except Exception as e:
                    print(f"Error getting total customers: {e}")
                
                # ---- GET ACTIVE RENTALS ----
                try:
                    # Check if rentals table exists
                    cursor.execute("SELECT COUNT(*) as count FROM rentals WHERE status IN ('active', 'overdue')")
                    result = cursor.fetchone()
                    if result:
                        active_rentals = result['count']
                except:
                    # If rentals table doesn't exist, try bookings with active status
                    try:
                        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE booking_status = 'active'")
                        result = cursor.fetchone()
                        if result:
                            active_rentals = result['count']
                    except:
                        pass
                
                # ---- GET AVAILABLE VEHICLES ----
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE status = 'available'")
                    result = cursor.fetchone()
                    if result:
                        available_vehicles = result['count']
                except Exception as e:
                    print(f"Error getting available vehicles: {e}")
                
                # ---- GET PENDING BOOKINGS ----
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE booking_status = 'pending'")
                    result = cursor.fetchone()
                    if result:
                        pending_bookings = result['count']
                except Exception as e:
                    print(f"Error getting pending bookings: {e}")
                
                cursor.close()
            
            # Update UI in main thread
            self.parent.after(0, lambda: self.update_stats(
                total_customers,
                active_rentals,
                available_vehicles,
                pending_bookings
            ))
            
        except Exception as e:
            self.parent.after(0, lambda: self.update_status(f"Error loading stats: {str(e)}"))

    def _get_connection(self):
        """Get database connection from various sources"""
        try:
            # Try from customer_model first
            if self.customer_model and hasattr(self.customer_model, 'get_connection'):
                return self.customer_model.get_connection()
            
            # Try from db object
            if self.db:
                if hasattr(self.db, 'get_connection'):
                    return self.db.get_connection()
                elif hasattr(self.db, 'connection'):
                    return self.db.connection
            
            return None
        except:
            return None

    def update_stats(self, total_customers, active_rentals, available_vehicles, pending_bookings):
        """Update stat labels with fetched data"""
        try:
            # Update stat labels
            if "total_customers" in self.stat_labels:
                self.stat_labels["total_customers"].config(text=str(total_customers))
            
            if "active_rentals" in self.stat_labels:
                self.stat_labels["active_rentals"].config(text=str(active_rentals))
            
            if "available_vehicles" in self.stat_labels:
                self.stat_labels["available_vehicles"].config(text=str(available_vehicles))
            
            if "pending_bookings" in self.stat_labels:
                self.stat_labels["pending_bookings"].config(text=str(pending_bookings))
            
            # Update last updated time
            now = datetime.now().strftime("%I:%M:%S %p")
            self.last_updated_label.config(text=f"Last updated: {now}")
            
            self.update_status("Dashboard updated successfully")
            
        except Exception as e:
            self.update_status(f"Error updating stats: {str(e)}")

    def refresh_dashboard(self):
        """Manually refresh dashboard data"""
        self.update_status("Refreshing dashboard...")
        self.load_dashboard_stats()

    def update_status(self, message):
        """Update status bar message"""
        try:
            if hasattr(self, 'status_label') and self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=message)
        except:
            pass

    # ==========================================================
    # ACTION METHODS - WITH ROLE-BASED ACCESS CONTROL
    # ==========================================================

    def _check_role_access(self, required_roles):
        """Check if user has required role"""
        user_role = self.user.get('role', 'staff')
        return user_role in required_roles

    def _show_access_denied(self):
        """Show access denied message"""
        messagebox.showerror('Access Denied', 'You do not have permission to access this feature.')

    def open_customers(self):
        """Open customer management view - Admin and Manager only"""
        if not self._check_role_access(['admin', 'manager']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror('Error', 'Database connection not available.')
                return

            # Clear current content
            for widget in self.parent.winfo_children():
                widget.destroy()

            from views.customer_view import CustomerView

            CustomerView(
                self.parent,
                self.db,
                self.user,
                self.controller
            )

        except ImportError as e:
            messagebox.showerror('Error', f'Could not load customer module:\n{e}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not open customer management:\n{e}')
    
    def open_vehicle_categories(self):
        """Open vehicle categories management view - Admin, Manager, Staff"""
        if not self._check_role_access(['admin', 'manager', 'staff']):
            self._show_access_denied()
            return
            
        try:
            # Clear current content
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            from views.vehicle_categories_view import VehicleCategoriesView
            VehicleCategoriesView(self.parent, self.db, self.user, self.controller)
            
        except ImportError as e:
            messagebox.showerror('Error', f'Could not load vehicle categories module: {str(e)}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not open dashboard: {str(e)}')

    def open_vehicles(self):
        """Open vehicle management view - All roles can view"""
        if not self._check_role_access(['admin', 'manager', 'staff', 'customer']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror('Error', 'Database connection not available.')
                return
            
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            from views.vehicle_view import VehicleView
            VehicleView(self.parent, self.db, self.user, self.controller)
            
        except ImportError as e:
            messagebox.showerror('Error', f'Could not load vehicle module: {str(e)}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not open vehicle management: {str(e)}')

    def open_maintenance(self):
        """Open maintenance management view - Admin, Manager, Staff"""
        if not self._check_role_access(['admin', 'manager', 'staff']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror('Error', 'Database connection not available.')
                return
            
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            from views.maintenance_view import MaintenanceView
            MaintenanceView(self.parent, self.db, self.user, self.controller)
            
        except ImportError as e:
            messagebox.showerror('Error', f'Could not load maintenance module: {str(e)}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not open maintenance: {str(e)}')

    def view_bookings(self):
        """Open booking management view - Admin, Manager, Staff, Customer"""
        if not self._check_role_access(['admin', 'manager', 'staff', 'customer']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror("Error", "Database connection not available.")
                return

            for widget in self.parent.winfo_children():
                widget.destroy()

            from views.booking_view import BookingView

            BookingView(self.parent, self.db, self.user, self.controller)

        except ImportError as e:
            messagebox.showerror("Error", f"Could not load booking module:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open bookings:\n{e}")

    def view_payments(self):
        """Open payment management view - Admin, Manager, Staff"""
        if not self._check_role_access(['admin', 'manager', 'staff']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror("Error", "Database connection not available.")
                return

            for widget in self.parent.winfo_children():
                widget.destroy()

            from views.payment_view import PaymentView

            PaymentView(self.parent, self.db, self.user, self.controller)

        except ImportError as e:
            messagebox.showerror("Error", f"Could not load payment module:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open payments:\n{e}")

    def manage_users(self):
        """Open user management view - Admin only"""
        if not self._check_role_access(['admin']):
            self._show_access_denied()
            return
            
        try:
            if self.db is None:
                messagebox.showerror('Error', 'Database connection not available.')
                return
            
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            from views.user_management_view import UserManagementView
            UserManagementView(self.parent, self.db, self.user, self.controller)
            
        except ImportError as e:
            messagebox.showerror('Error', f'Could not load user management module: {str(e)}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not open user management: {str(e)}')

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.customer_model and hasattr(self.customer_model, 'close'):
            try:
                self.customer_model.close()
            except:
                pass
        self.parent.destroy()