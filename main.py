import database
from ui import MentalHealthApp
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # ✅ Reset old removed activities before showing recommendations
    database.reset_old_removed_activities()
    
    # Initialize and launch the UI
    app = QApplication(sys.argv)
    window = MentalHealthApp()
    window.show()
    
    # Run the app event loop
    sys.exit(app.exec_())  # No need to call collect_feedback() here
