import shutil
import os
from datetime import datetime

database = "car_rental_system.db"
backup_folder = "backups"

os.makedirs(backup_folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_file = os.path.join(
    backup_folder,
    f"car_rental_system_{timestamp}.db"
)

shutil.copy2(database, backup_file)

print(f"Database backup created: {backup_file}")