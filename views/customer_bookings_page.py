# views/customer_bookings_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.qr_generator import QRCodeGenerator


class CustomerBookingsPage:
    def __init__(self, parent, db, customer_id, update_status_callback, show_payment_callback=None):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.update_status = update_status_callback
        self.show_payment = show_payment_callback
        self.qr_generator = QRCodeGenerator()
        self.setup_ui()
        self.load_bookings()

    def setup_ui(self):
        """Setup the bookings page UI"""
        # Title with refresh button
        header_frame = tk.Frame(self.parent, bg='#f0f0f0')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="📝 My Bookings",
            font=('Segoe UI', 20, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        ).pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self.load_bookings,
            font=('Segoe UI', 10),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(bg='#2980b9'))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(bg='#3498db'))
        
        if not self.customer_id:
            tk.Label(
                self.parent,
                text="Customer profile not found.",
                font=('Segoe UI', 12),
                fg='#e74c3c',
                bg='#f0f0f0'
            ).pack(pady=20)
            return
        
        # Bookings container with scrollbar
        self.bookings_container = tk.Frame(self.parent, bg='#f0f0f0')
        self.bookings_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.bookings_container, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.bookings_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_bookings(self):
        """Load customer's bookings"""
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn is None:
                return
            
            cursor = conn.cursor()
            
            # Query with payment info
            query = """
                SELECT 
                    b.booking_id,
                    b.booking_ref,
                    v.make || ' ' || v.model as vehicle_name,
                    b.start_date,
                    b.end_date,
                    b.total_amount,
                    b.total_days,
                    b.booking_status,
                    b.notes,
                    b.created_at,
                    COALESCE(
                        (SELECT SUM(amount) FROM payments WHERE booking_id = b.booking_id AND payment_status = 'paid'),
                        0
                    ) as paid_amount
                FROM bookings b
                JOIN vehicles v ON b.vehicle_id = v.id
                WHERE b.customer_id = ?
                ORDER BY b.created_at DESC
            """
            
            cursor.execute(query, (self.customer_id,))
            bookings = cursor.fetchall()
            cursor.close()
            
            if not bookings:
                tk.Label(
                    self.scrollable_frame,
                    text="No bookings found.",
                    font=('Segoe UI', 14),
                    fg='#7f8c8d',
                    bg='#f0f0f0'
                ).pack(pady=50)
                return
            
            for booking in bookings:
                self.create_booking_card(booking)
            
            self.update_status(f"Showing {len(bookings)} bookings")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load bookings: {str(e)}")

    def create_booking_card(self, booking):
        """Create a booking card with QR button"""
        # Status colors based on booking_status
        status_colors = {
            'pending': '#f39c12',
            'approved': '#3498db',
            'rejected': '#e74c3c',
            'active': '#2ecc71',
            'completed': '#27ae60',
            'cancelled': '#95a5a6'
        }
        
        card = tk.Frame(
            self.scrollable_frame,
            bg='white',
            relief=tk.RAISED,
            bd=1,
            padx=15,
            pady=12
        )
        card.pack(fill=tk.X, pady=5)
        
        # Header
        header_frame = tk.Frame(card, bg='white')
        header_frame.pack(fill=tk.X)
        
        # Booking Reference
        tk.Label(
            header_frame,
            text=f"Booking: {booking['booking_ref']}",
            font=('Segoe UI', 12, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(side=tk.LEFT)
        
        # Status
        status_color = status_colors.get(booking['booking_status'], '#7f8c8d')
        status_display = booking['booking_status'].upper() if booking['booking_status'] else 'PENDING'
        tk.Label(
            header_frame,
            text=f" {status_display} ",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg=status_color,
            padx=10,
            pady=2
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Booking ID
        tk.Label(
            card,
            text=f"ID: #{booking['booking_id']}",
            font=('Segoe UI', 9),
            fg='#bdc3c7',
            bg='white'
        ).pack(anchor='e')
        
        # Vehicle name
        tk.Label(
            card,
            text=f"🚗 {booking['vehicle_name']}",
            font=('Segoe UI', 12),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(5, 0))
        
        # Details grid
        details_frame = tk.Frame(card, bg='white')
        details_frame.pack(fill=tk.X, pady=5)
        
        # Calculate remaining amount
        total = booking['total_amount'] or 0
        paid = booking['paid_amount'] or 0
        remaining = total - paid
        
        details = [
            f"📅 From: {booking['start_date']}",
            f"📅 To: {booking['end_date']}",
            f"📊 Days: {booking['total_days'] or 0}",
            f"💰 Total: ${total:.2f}",
            f"💳 Paid: ${paid:.2f}",
            f"📊 Remaining: ${remaining:.2f}"
        ]
        
        for detail in details:
            tk.Label(
                details_frame,
                text=detail,
                font=('Segoe UI', 10),
                fg='#7f8c8d',
                bg='white'
            ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Notes
        if booking['notes']:
            tk.Label(
                card,
                text=f"📝 Notes: {booking['notes']}",
                font=('Segoe UI', 10, 'italic'),
                fg='#34495e',
                bg='white'
            ).pack(anchor='w', pady=(5, 0))
        
        # Submitted date
        tk.Label(
            card,
            text=f"Submitted: {booking['created_at']}",
            font=('Segoe UI', 9),
            fg='#bdc3c7',
            bg='white'
        ).pack(anchor='e', pady=(5, 0))
        
        # Buttons frame
        btn_frame = tk.Frame(card, bg='white')
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Pay Now button (only for approved bookings with remaining amount > 0)
        status = booking['booking_status']
        if status == 'approved' and remaining > 0:
            tk.Button(
                btn_frame,
                text="💳 Pay Now",
                command=lambda: self.show_payment(
                    booking['booking_id'],
                    booking['booking_ref'],
                    remaining
                ),
                font=('Segoe UI', 10, 'bold'),
                bg='#2ecc71',
                fg='white',
                cursor='hand2',
                relief=tk.FLAT,
                padx=20,
                pady=5
            ).pack(side=tk.RIGHT, padx=5)
            
            tk.Label(
                btn_frame,
                text=f"Amount Due: ${remaining:.2f}",
                font=('Segoe UI', 10, 'bold'),
                fg='#e74c3c',
                bg='white'
            ).pack(side=tk.RIGHT, padx=(0, 10))
            
        elif status == 'approved' and remaining <= 0:
            tk.Label(
                card,
                text="✅ Fully Paid",
                font=('Segoe UI', 10, 'bold'),
                fg='#27ae60',
                bg='white'
            ).pack(anchor='e', pady=(5, 0))
        
        # QR Code button (for all bookings)
        qr_btn = tk.Button(
            btn_frame,
            text="📱 QR Code",
            command=lambda b=booking: self.show_qr_viewer(b),
            font=('Segoe UI', 9, 'bold'),
            bg='#9b59b6',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        qr_btn.pack(side=tk.LEFT, padx=5)
        qr_btn.bind('<Enter>', lambda e, b=qr_btn: b.config(bg='#8e44ad'))
        qr_btn.bind('<Leave>', lambda e, b=qr_btn: b.config(bg='#9b59b6'))

    def show_qr_viewer(self, booking):
        """Show QR code viewer for booking"""
        try:
            # Get full booking details
            conn = self.db.get_connection() if hasattr(self.db, 'get_connection') else None
            if conn is None:
                return
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    b.*,
                    c.first_name,
                    c.last_name,
                    c.email,
                    v.make,
                    v.model,
                    v.license_plate
                FROM bookings b
                JOIN customers c ON b.customer_id = c.customer_id
                JOIN vehicles v ON b.vehicle_id = v.id
                WHERE b.booking_id = ?
            """, (booking['booking_id'],))
            
            booking_data = cursor.fetchone()
            cursor.close()
            
            if not booking_data:
                messagebox.showerror("Error", "Booking not found")
                return
            
            # Convert to dict
            booking_dict = dict(booking_data)
            
            # Create QR viewer popup
            self._show_qr_popup(booking_dict)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate QR: {str(e)}")

    def _show_qr_popup(self, booking_dict):
        """Show QR in a popup window"""
        from views.qr_viewer_page import QRViewerPage
        import tkinter as tk
        
        popup = tk.Toplevel(self.parent)
        popup.title("QR Code Viewer")
        popup.geometry("900x600")
        popup.configure(bg='#f0f0f0')
        popup.transient(self.parent)
        popup.grab_set()
        popup.resizable(False, False)
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (900 // 2)
        y = (popup.winfo_screenheight() // 2) - (600 // 2)
        popup.geometry(f'900x600+{x}+{y}')
        
        # Create a frame inside popup for QR viewer
        content_frame = tk.Frame(popup, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        QRViewerPage(
            content_frame,
            self.db,
            'booking',
            booking_dict,
            popup.destroy,
            self.update_status
        )

    def update_status(self, message):
        """Update status bar"""
        if self.update_status:
            self.update_status(message)