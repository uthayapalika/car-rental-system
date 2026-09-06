# controllers/app_controller.py
class AppController:
    def __init__(self, db):
        self.db = db
        self.current_user = None
    
    def logout(self):
        """Logout user"""
        self.current_user = None
        # Return to login screen
        from main import CarRentalApp
        app = CarRentalApp()
        app.show_login()
    
    def get_db(self):
        """Get database connection"""
        return self.db