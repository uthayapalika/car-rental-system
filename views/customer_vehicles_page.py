# views/customer_vehicles_page.py
import tkinter as tk
from tkinter import ttk, messagebox


class CustomerVehiclesPage:
    def __init__(self, parent, db, customer_id, show_booking_callback, update_status_callback):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.show_booking = show_booking_callback
        self.update_status = update_status_callback
        
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All")
        
        self.setup_ui()
        self.load_categories()
        self.load_vehicles()

    def setup_ui(self):
        """Setup the vehicles page UI"""
        # Title
        tk.Label(
            self.parent,
            text="🚗 Available Vehicles",
            font=('Segoe UI', 20, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 15))
        
        # Search and filter frame
        filter_frame = tk.Frame(self.parent, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            filter_frame,
            text="Search:",
            font=('Segoe UI', 11),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var.trace_add("write", self.on_search)
        
        tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 11),
            width=25
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            filter_frame,
            text="Category:",
            font=('Segoe UI', 11),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            font=('Segoe UI', 10),
            width=15,
            state='readonly'
        )
        self.category_combo.pack(side=tk.LEFT)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_filter)
        
        # Scrollable vehicles container
        self.vehicles_container = tk.Frame(self.parent, bg='#f0f0f0')
        self.vehicles_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.vehicles_container, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.vehicles_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_categories(self):
        """Load vehicle categories"""
        try:
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM vehicle_categories ORDER BY name")
                categories = cursor.fetchall()
                cursor.close()
                
                values = ["All"] + [cat['name'] for cat in categories]
                self.category_combo['values'] = values
                self.category_var.set("All")
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_vehicles(self, search_term="", category="All"):
        """Load vehicles into the scrollable frame"""
        # Clear existing cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn is None:
                return
            
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    v.id,
                    v.make,
                    v.model,
                    v.year,
                    v.license_plate,
                    v.daily_rate,
                    v.status,
                    v.fuel_type,
                    v.mileage,
                    v.color,
                    v.min_rent_period,
                    v.max_rent_period,
                    vc.name as category_name,
                    vc.late_fee_rate
                FROM vehicles v
                LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
                WHERE v.status = 'available'
            """
            
            params = []
            
            if search_term:
                query += " AND (v.make LIKE ? OR v.model LIKE ? OR v.license_plate LIKE ?)"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param])
            
            if category != "All":
                query += " AND vc.name = ?"
                params.append(category)
            
            query += " ORDER BY v.make, v.model"
            
            cursor.execute(query, params)
            vehicles = cursor.fetchall()
            cursor.close()
            
            if not vehicles:
                tk.Label(
                    self.scrollable_frame,
                    text="No vehicles available at the moment.",
                    font=('Segoe UI', 14),
                    fg='#7f8c8d',
                    bg='#f0f0f0'
                ).pack(pady=50)
                return
            
            for vehicle in vehicles:
                self.create_vehicle_card(vehicle)
            
            self.update_status(f"Showing {len(vehicles)} vehicles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load vehicles: {str(e)}")

    def create_vehicle_card(self, vehicle):
        """Create a vehicle card"""
        card = tk.Frame(
            self.scrollable_frame,
            bg='white',
            relief=tk.RAISED,
            bd=1,
            pady=15,
            padx=15
        )
        card.pack(fill=tk.X, pady=5)
        
        # Vehicle name
        tk.Label(
            card,
            text=f"{vehicle['make']} {vehicle['model']} ({vehicle['year']})",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w')
        
        # Details row
        details_frame = tk.Frame(card, bg='white')
        details_frame.pack(fill=tk.X, pady=5)
        
        details = [
            f"License: {vehicle['license_plate']}",
            f"Fuel: {vehicle['fuel_type']}",
            f"Mileage: {vehicle['mileage']} km",
            f"Color: {vehicle['color'] or 'N/A'}",
            f"Category: {vehicle['category_name'] or 'N/A'}"
        ]
        
        for detail in details:
            tk.Label(
                details_frame,
                text=detail,
                font=('Segoe UI', 10),
                fg='#7f8c8d',
                bg='white'
            ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Pricing and rental info
        price_frame = tk.Frame(card, bg='white')
        price_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            price_frame,
            text=f"💰 Daily Rate: ${vehicle['daily_rate']:.2f}",
            font=('Segoe UI', 12, 'bold'),
            fg='#27ae60',
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        min_period = vehicle['min_rent_period'] or 1
        max_period = vehicle['max_rent_period'] or 30
        
        tk.Label(
            price_frame,
            text=f"📅 Min: {min_period} day(s) | Max: {max_period} day(s)",
            font=('Segoe UI', 10),
            fg='#7f8c8d',
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        if vehicle['late_fee_rate']:
            tk.Label(
                price_frame,
                text=f"⚠️ Late Fee: ${vehicle['late_fee_rate']:.2f}/day",
                font=('Segoe UI', 10),
                fg='#e74c3c',
                bg='white'
            ).pack(side=tk.LEFT)
        
        # Book button
        tk.Button(
            card,
            text="📝 Book This Vehicle",
            command=lambda vid=vehicle['id']: self.show_booking(vid),
            font=('Segoe UI', 10, 'bold'),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(anchor='e', pady=(5, 0))

    def on_search(self, *args):
        """Handle search input"""
        search_term = self.search_var.get().strip()
        category = self.category_var.get()
        self.load_vehicles(search_term, category)

    def on_category_filter(self, event):
        """Handle category filter change"""
        search_term = self.search_var.get().strip()
        category = self.category_var.get()
        self.load_vehicles(search_term, category)

    def update_status(self, message):
        """Update status bar"""
        if self.update_status:
            self.update_status(message)