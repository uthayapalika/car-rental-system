import tkinter as tk
from tkinter import messagebox
from views.login_view import LoginView
from controllers.login_controller import LoginController
from db_setup import Database 
from factories import ModelFactory
from version import APP_VERSION
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Car Rental System - Version {APP_VERSION}")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)

        # Initialize factories
        self.model_factory = ModelFactory()
        
        # Initialize database 
        try:
            self.db = Database()
            print("Database connected successfully!")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.db = None
        
        # Create controller (pass db instead of model)
        self.controller = LoginController(self.root, None, self.db)
        
        # Create view with controller
        self.view = LoginView(self.root, self.controller)
        
        # Set the view in controller
        self.controller.view = self.view
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        """Handle application close"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            if hasattr(self, 'db') and self.db:
                self.db.close()
            self.root.quit()
            self.root.destroy()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()