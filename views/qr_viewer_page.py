# views/qr_viewer_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import webbrowser
import os


class QRViewerPage:
    """Page to display QR code for booking/vehicle with scan functionality"""
    
    def __init__(self, parent, db, qr_type, data, go_back_callback, update_status_callback):
        self.parent = parent
        self.db = db
        self.qr_type = qr_type  # 'booking', 'vehicle', 'payment'
        self.data = data
        self.go_back = go_back_callback
        self.update_status = update_status_callback
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the QR viewer page"""
        # Main container
        main_frame = tk.Frame(self.parent, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Back button
        back_frame = tk.Frame(main_frame, bg='#f0f0f0')
        back_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(
            back_frame,
            text="◀ Back",
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
        title_text = "📱 QR Code Viewer"
        tk.Label(
            main_frame,
            text=title_text,
            font=('Segoe UI', 24, 'bold'),
            fg='#2c3e50',
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 20))
        
        # Create two columns
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - QR Code
        left_frame = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📷 Scan QR Code",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(pady=(0, 15))
        
        # QR Code display
        self.qr_label = tk.Label(
            left_frame,
            text="Generating QR Code...",
            font=('Segoe UI', 12),
            fg='#7f8c8d',
            bg='white'
        )
        self.qr_label.pack(pady=20)
        
        # Scan instructions
        instructions_frame = tk.Frame(left_frame, bg='white')
        instructions_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            instructions_frame,
            text="📱 How to use:",
            font=('Segoe UI', 12, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w')
        
        instructions = [
            "1. Open your phone's camera app",
            "2. Point it at the QR code above",
            "3. Tap the link that appears",
            "4. View details on your mobile device"
        ]
        
        for instruction in instructions:
            tk.Label(
                instructions_frame,
                text=instruction,
                font=('Segoe UI', 10),
                fg='#7f8c8d',
                bg='white'
            ).pack(anchor='w', pady=2)
        
        # Right column - Details
        right_frame = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="📋 Details",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 15))
        
        # Details content
        self.details_frame = tk.Frame(right_frame, bg='white')
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Generate QR and show details
        self.generate_qr_and_details()
        
        # Action buttons
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            btn_frame,
            text="🌐 Open in Browser",
            command=self.open_in_browser,
            font=('Segoe UI', 10, 'bold'),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="💾 Save QR Code",
            command=self.save_qr_code,
            font=('Segoe UI', 10, 'bold'),
            bg='#2ecc71',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    def generate_qr_and_details(self):
        """Generate QR code and display details"""
        try:
            from utils.qr_generator import QRCodeGenerator
            qr_gen = QRCodeGenerator()
            
            # Generate QR based on type
            if self.qr_type == 'booking':
                self._generate_booking_qr(qr_gen)
            elif self.qr_type == 'vehicle':
                self._generate_vehicle_qr(qr_gen)
            elif self.qr_type == 'payment':
                self._generate_payment_qr(qr_gen)
            else:
                self.qr_label.config(text="❌ Unknown QR type")
            
        except ImportError as e:
            self.qr_label.config(text="❌ QR Generator not installed")
            messagebox.showerror("Error", "Please install qrcode: pip install qrcode[pil]")
        except Exception as e:
            self.qr_label.config(text=f"❌ Error: {str(e)}")
    
    def _generate_booking_qr(self, qr_gen):
        """Generate booking QR code"""
        # Create QR data
        qr_data = {
            'type': 'booking',
            'booking_id': self.data.get('booking_id'),
            'booking_ref': self.data.get('booking_ref'),
            'vehicle': f"{self.data.get('make', '')} {self.data.get('model', '')}",
            'start_date': self.data.get('start_date'),
            'end_date': self.data.get('end_date'),
            'total_days': self.data.get('total_days'),
            'total_amount': self.data.get('total_amount'),
            'status': self.data.get('booking_status'),
            'customer_name': f"{self.data.get('first_name', '')} {self.data.get('last_name', '')}"
        }
        
        # Generate QR code
        qr_path = qr_gen.generate_qr_code_only(
            json.dumps(qr_data),
            f"booking_{self.data.get('booking_ref')}.png"
        )
        
        # Display QR
        self._display_qr(qr_path)
        
        # Display details
        self._display_booking_details()
    
    def _generate_vehicle_qr(self, qr_gen):
        """Generate vehicle QR code"""
        # Create QR data
        qr_data = {
            'type': 'vehicle',
            'id': self.data.get('id'),
            'make': self.data.get('make'),
            'model': self.data.get('model'),
            'year': self.data.get('year'),
            'license_plate': self.data.get('license_plate'),
            'daily_rate': self.data.get('daily_rate'),
            'fuel_type': self.data.get('fuel_type'),
            'status': self.data.get('status'),
            'color': self.data.get('color'),
            'mileage': self.data.get('mileage')
        }
        
        # Generate QR code
        qr_path = qr_gen.generate_qr_code_only(
            json.dumps(qr_data),
            f"vehicle_{self.data.get('id')}.png"
        )
        
        # Display QR
        self._display_qr(qr_path)
        
        # Display details
        self._display_vehicle_details()
    
    def _generate_payment_qr(self, qr_gen):
        """Generate payment QR code"""
        # Create QR data
        qr_data = {
            'type': 'payment',
            'payment_id': self.data.get('payment_id'),
            'transaction_ref': self.data.get('transaction_reference'),
            'booking_ref': self.data.get('booking_ref'),
            'amount': self.data.get('amount'),
            'payment_type': self.data.get('payment_type'),
            'payment_method': self.data.get('payment_method'),
            'payment_status': self.data.get('payment_status')
        }
        
        # Generate QR code
        qr_path = qr_gen.generate_qr_code_only(
            json.dumps(qr_data),
            f"payment_{self.data.get('transaction_reference')}.png"
        )
        
        # Display QR
        self._display_qr(qr_path)
        
        # Display details
        self._display_payment_details()
    
    def _display_qr(self, qr_path):
        """Display QR code in the label"""
        from PIL import Image, ImageTk
        
        try:
            # Load and resize image
            img = Image.open(qr_path)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.qr_label.config(image=photo, text="")
            self.qr_label.image = photo  # Keep reference
            
            # Store path for saving
            self.qr_image_path = qr_path
            
        except Exception as e:
            self.qr_label.config(text=f"❌ Could not load QR: {str(e)}")
    
    def _display_booking_details(self):
        """Display booking details in the right panel"""
        # Clear previous details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Booking header
        tk.Label(
            self.details_frame,
            text=f"📝 Booking: {self.data.get('booking_ref')}",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        # Status badge
        status = self.data.get('booking_status', 'pending')
        status_colors = {
            'pending': '#f39c12',
            'approved': '#3498db',
            'rejected': '#e74c3c',
            'active': '#2ecc71',
            'completed': '#27ae60',
            'cancelled': '#95a5a6'
        }
        
        status_frame = tk.Frame(self.details_frame, bg='white')
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            status_frame,
            text="Status:",
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            status_frame,
            text=f" {status.upper()} ",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg=status_colors.get(status, '#7f8c8d'),
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=10)
        
        # Details
        details = [
            (f"👤 Customer: {self.data.get('first_name', '')} {self.data.get('last_name', '')}"),
            (f"🚗 Vehicle: {self.data.get('make', '')} {self.data.get('model', '')}"),
            (f"📅 From: {self.data.get('start_date')}"),
            (f"📅 To: {self.data.get('end_date')}"),
            (f"📊 Days: {self.data.get('total_days')}"),
        ]
        
        for detail in details:
            tk.Label(
                self.details_frame,
                text=detail,
                font=('Segoe UI', 11),
                fg='#2c3e50',
                bg='white'
            ).pack(anchor='w', pady=3)
        
        # Total amount
        total = self.data.get('total_amount', 0)
        tk.Label(
            self.details_frame,
            text=f"💰 Total: ${total:.2f}",
            font=('Segoe UI', 13, 'bold'),
            fg='#27ae60',
            bg='white'
        ).pack(anchor='w', pady=(10, 0))
        
        # Notes
        if self.data.get('notes'):
            tk.Label(
                self.details_frame,
                text=f"📝 Notes: {self.data.get('notes')}",
                font=('Segoe UI', 10, 'italic'),
                fg='#7f8c8d',
                bg='white'
            ).pack(anchor='w', pady=(10, 0))
    
    def _display_vehicle_details(self):
        """Display vehicle details"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Vehicle header
        tk.Label(
            self.details_frame,
            text=f"🚗 {self.data.get('make')} {self.data.get('model')}",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        details = [
            (f"Year: {self.data.get('year')}"),
            (f"License: {self.data.get('license_plate')}"),
            (f"Fuel: {self.data.get('fuel_type')}"),
            (f"Color: {self.data.get('color') or 'N/A'}"),
            (f"Mileage: {self.data.get('mileage')} km"),
            (f"Daily Rate: ${self.data.get('daily_rate', 0):.2f}"),
        ]
        
        for detail in details:
            tk.Label(
                self.details_frame,
                text=detail,
                font=('Segoe UI', 11),
                fg='#2c3e50',
                bg='white'
            ).pack(anchor='w', pady=3)
    
    def _display_payment_details(self):
        """Display payment details"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.details_frame,
            text=f"💳 Payment Receipt",
            font=('Segoe UI', 14, 'bold'),
            fg='#2c3e50',
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        details = [
            (f"Transaction: {self.data.get('transaction_reference')}"),
            (f"Booking: {self.data.get('booking_ref')}"),
            (f"Amount: ${self.data.get('amount', 0):.2f}"),
            (f"Type: {self.data.get('payment_type', 'N/A')}"),
            (f"Method: {self.data.get('payment_method', 'N/A')}"),
            (f"Status: {self.data.get('payment_status', 'N/A').upper()}"),
        ]
        
        for detail in details:
            tk.Label(
                self.details_frame,
                text=detail,
                font=('Segoe UI', 11),
                fg='#2c3e50',
                bg='white'
            ).pack(anchor='w', pady=3)
    
    def open_in_browser(self):
        """Open QR code in browser for scanning"""
        if hasattr(self, 'qr_image_path') and self.qr_image_path:
            webbrowser.open(self.qr_image_path)
    
    def save_qr_code(self):
        """Save QR code to a location"""
        from tkinter import filedialog
        import shutil
        
        if hasattr(self, 'qr_image_path') and self.qr_image_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension='.png',
                filetypes=[('PNG files', '*.png'), ('All files', '*.*')],
                initialfile=f"qr_{self.qr_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            
            if file_path:
                shutil.copy2(self.qr_image_path, file_path)
                messagebox.showinfo("Success", f"QR Code saved to:\n{file_path}")