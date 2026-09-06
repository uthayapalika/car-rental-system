# controllers/login_controller.py
import tkinter as tk
from tkinter import messagebox
from views.main_dashboard import MainDashboard
from views.registration_view import RegistrationView
from controllers.registration_controller import RegistrationController
#from models.customer_model import CustomerModel
from factories import ModelFactory


class LoginController:
    def __init__(self, parent, view=None, db=None):
        self.parent = parent
        self.view = view
        self.db = db  
        self.model = None  
        self.current_user = None
        self.dashboard = None
        self.dashboard_frame = None
        self.registration_frame = None
        self.registration_controller = None
    
    def _init_model(self):
        """Lazy initialize the model"""
        if self.model is None and self.db is not None:
            try:
                self.model = ModelFactory.create_model("customer", db=self.db)
                print("CustomerModel initialized successfully")
            except Exception as e:
                print(f"Error initializing CustomerModel: {e}")
        return self.model
        
    def login(self):
        """Handle login process"""
        if self.view is None:
            print("Error: View is not set in controller!")
            return
            
        username, password = self.view.get_credentials()
        
        if not username or not password:
            self.view.show_error("Please enter both username and password!")
            return
        
        self.view.set_loading()
        
        # Initialize model if needed
        model = self._init_model()
        
        if model:
            try:
                success, user = model.authenticate_user(username, password)
                if success:
                    self.view.show_success("Login successful!")
                    self.current_user = user
                    self.view.window.after(500, self.open_dashboard)
                else:
                    self.view.show_error("Invalid username or password!")
                    self.view.clear_fields()
                    self.view.reset_loading()
            except Exception as e:
                self.view.show_error(f"Authentication error: {str(e)}")
                self.view.reset_loading()
                print(f"❌ Login error details: {e}")
        else:
            self.view.show_error("Database connection failed!")
            self.view.reset_loading()

    def open_registration(self):
        """Open registration in the same window"""
        try:
            # Initialize model if needed
            model = self._init_model()
            
            # Hide login view
            self.view.hide()
            
            # Create registration frame in the same window
            self.registration_frame = tk.Frame(self.parent, bg='#f0f0f0')
            self.registration_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create registration controller with model
            self.registration_controller = RegistrationController(None, model)
            
            # Create registration view
            reg_view = RegistrationView(self.registration_frame, self.registration_controller)
            
            # Set view in registration controller
            self.registration_controller.set_view(reg_view)
            
            # Set the view reference
            self.registration_controller.login_controller = self
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open registration: {str(e)}")

    def close_registration(self):
        """Close registration and show login"""
        if self.registration_frame:
            self.registration_frame.destroy()
            self.registration_frame = None
            self.registration_controller = None
        
        # Show login view
        if self.view:
            self.view.show()

    def open_dashboard(self):
        """Open dashboard view"""
        try:
            self.view.reset_loading()
            
            # Hide login view
            self.view.hide()
            
            # Create dashboard frame in the same window
            self.dashboard_frame = tk.Frame(self.parent, bg='#f0f0f0')
            self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create dashboard view
            self.dashboard = MainDashboard(
                self.dashboard_frame, 
                self.current_user, 
                self
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open dashboard: {str(e)}")
            self.view.show()
            self.view.reset_loading()

    def handle_dashboard_close(self):
        """Handle dashboard close event"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.logout()

    def logout(self):
        """Handle logout"""
        if self.dashboard_frame:
            self.dashboard_frame.destroy()
            self.dashboard_frame = None
            self.dashboard = None
        
        if self.view:
            self.view.show()
            self.view.clear_fields()
            self.view.status_label.config(text="")
            self.view.login_button.config(state=tk.NORMAL, text="Login")
        
        self.current_user = None