from datetime import datetime
from tkinter import messagebox
import sqlite3


class CustomerBookingController:
    def __init__(self, db):
        self.db = db

    def get_connection(self):
        """Get database connection"""
        if hasattr(self.db, 'get_connection'):
            return self.db.get_connection()
        elif hasattr(self.db, 'connection'):
            return self.db.connection
        return None

    def get_vehicle_details(self, vehicle_id):
        """Get vehicle details by ID"""
        try:
            conn = self.get_connection()
            if conn is None:
                return None
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    v.*,
                    vc.name as category_name,
                    vc.late_fee_rate
                FROM vehicles v
                LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
                WHERE v.id = ?
            """, (vehicle_id,))
            
            vehicle = cursor.fetchone()
            cursor.close()
            
            return vehicle
            
        except Exception as e:
            print(f"Error getting vehicle details: {e}")
            return None

    def get_next_booking_ref(self):
        """
        Generate booking reference.
        Format: BR-001-YYYYMMDD
        """
        try:
            conn = self.get_connection()
            if conn is None:
                return f"BR-001-{datetime.now().strftime('%Y%m%d')}"
            
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(booking_id), 0) + 1 AS next_number FROM bookings")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                next_number = int(result['next_number'])
            else:
                next_number = 1
            
            date_part = datetime.now().strftime('%Y%m%d')
            return f"BR-{next_number:03d}-{date_part}"
            
        except Exception as e:
            print(f"Error generating booking ref: {e}")
            return f"BR-001-{datetime.now().strftime('%Y%m%d')}"

    def create_booking(self, customer_id, vehicle_id, start_date, end_date, daily_rate, total_days, total_amount, notes=""):
        """
        Create a new booking for customer
        
        Returns:
            (success, message, booking_ref)
        """
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Database connection not available", None
            
            # Generate booking reference
            booking_ref = self.get_next_booking_ref()
            
            cursor = conn.cursor()
            
            # Check vehicle availability
            cursor.execute("""
                SELECT booking_id
                FROM bookings
                WHERE vehicle_id = ?
                AND booking_status NOT IN ('rejected', 'cancelled', 'completed')
                AND start_date <= ?
                AND end_date >= ?
            """, (vehicle_id, end_date, start_date))
            
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                return False, "Vehicle is already booked during the selected dates.", None
            
            # Insert booking
            cursor.execute("""
                INSERT INTO bookings (
                    booking_ref,
                    customer_id,
                    vehicle_id,
                    start_date,
                    end_date,
                    daily_rate,
                    total_days,
                    total_amount,
                    booking_status,
                    notes,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_ref,
                customer_id,
                vehicle_id,
                start_date,
                end_date,
                daily_rate,
                total_days,
                total_amount,
                'pending',
                notes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            cursor.close()
            
            return True, "Booking created successfully", booking_ref
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                # Try again with new reference (recursive call)
                return self.create_booking(customer_id, vehicle_id, start_date, end_date, 
                                         daily_rate, total_days, total_amount, notes)
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            return False, f"Error creating booking: {str(e)}", None

    def get_customer_bookings(self, customer_id):
        """Get all bookings for a customer"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            
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
                    b.created_at
                FROM bookings b
                JOIN vehicles v ON b.vehicle_id = v.id
                WHERE b.customer_id = ?
                ORDER BY b.created_at DESC
            """
            
            cursor.execute(query, (customer_id,))
            bookings = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dictionaries
            result = []
            for row in bookings:
                result.append(dict(row))
            
            return result
            
        except Exception as e:
            print(f"Error getting customer bookings: {e}")
            return []

    def check_vehicle_availability(self, vehicle_id, start_date, end_date, exclude_booking_id=None):
        """
        Check if vehicle is available for the given dates
        """
        try:
            conn = self.get_connection()
            if conn is None:
                return False
            
            cursor = conn.cursor()
            
            query = """
                SELECT booking_id
                FROM bookings
                WHERE vehicle_id = ?
                AND booking_status NOT IN ('rejected', 'cancelled', 'completed')
                AND start_date <= ?
                AND end_date >= ?
            """
            
            params = [vehicle_id, end_date, start_date]
            
            if exclude_booking_id:
                query += " AND booking_id != ?"
                params.append(exclude_booking_id)
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            cursor.close()
            
            return result is None
            
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False

    def get_vehicle_info_for_booking(self, vehicle_id):
        """
        Get vehicle information needed for booking form
        Returns: (make, model, daily_rate, min_period, max_period, late_fee)
        """
        try:
            vehicle = self.get_vehicle_details(vehicle_id)
            if not vehicle:
                return None, None, 0, 1, 30, 0
            
            return (
                vehicle.get('make', ''),
                vehicle.get('model', ''),
                vehicle.get('daily_rate', 0),
                vehicle.get('min_rent_period', 1),
                vehicle.get('max_rent_period', 30),
                vehicle.get('late_fee_rate', 0)
            )
        except Exception as e:
            print(f"Error getting vehicle info: {e}")
            return None, None, 0, 1, 30, 0

    def cancel_booking(self, booking_id, customer_id):
        """
        Cancel a booking (only if it's pending)
        Returns: (success, message)
        """
        try:
            conn = self.get_connection()
            if conn is None:
                return False, "Database connection not available"
            
            cursor = conn.cursor()
            
            # Verify booking belongs to customer and is pending
            cursor.execute("""
                SELECT booking_status
                FROM bookings
                WHERE booking_id = ? AND customer_id = ?
            """, (booking_id, customer_id))
            
            booking = cursor.fetchone()
            if not booking:
                cursor.close()
                return False, "Booking not found"
            
            if booking['booking_status'] != 'pending':
                cursor.close()
                return False, "Only pending bookings can be cancelled"
            
            # Update status to cancelled
            cursor.execute("""
                UPDATE bookings
                SET booking_status = 'cancelled',
                    updated_at = ?
                WHERE booking_id = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), booking_id))
            
            conn.commit()
            cursor.close()
            
            return True, "Booking cancelled successfully"
            
        except Exception as e:
            return False, f"Error cancelling booking: {str(e)}"