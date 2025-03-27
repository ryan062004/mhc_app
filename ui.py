from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import sys
import pso


class MentalHealthApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up layout
        layout = QVBoxLayout()
        
        # Set up font and colors
        self.setAppStyle()

        # Title label
        self.label = QLabel("Click below to get your mental health recommendation")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16))
        layout.addWidget(self.label)
        
        # Recommendation button
        self.button = QPushButton("Get Recommendation")
        self.button.setStyleSheet("background-color: #5C6BC0; color: white; font-size: 14px; border-radius: 8px; padding: 10px;")
        self.button.clicked.connect(self.get_recommendation)
        layout.addWidget(self.button)

        # Spacer
        layout.addStretch()

        # Mood feedback section
        self.mood_label = QLabel("How did this activity make you feel?")
        self.mood_label.setAlignment(Qt.AlignCenter)
        self.mood_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.mood_label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        layout.addWidget(self.slider)

        # Submit mood feedback button
        self.submit_button = QPushButton("Submit Feedback")
        self.submit_button.setStyleSheet("background-color: #42A5F5; color: white; font-size: 14px; border-radius: 8px; padding: 10px;")
        self.submit_button.setEnabled(False)  # Disable until recommendation is shown
        self.submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(self.submit_button)

        # Set the main layout and window title
        self.setLayout(layout)
        self.setWindowTitle("Mental Health Companion")
        self.resize(400, 350)

        # Initialize activity list for feedback
        self.activity_queue = []
        self.current_activity_index = 0

    def setAppStyle(self):
        """Sets the overall style of the app (color palette, font size, etc.)"""
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#E8F5E9"))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #E8F5E9;
            }
            QLabel {
                color: #455A64;
            }
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3949AB;
            }
        """)

    def get_recommendation(self):
        """Display recommended activities when the button is clicked"""
        recommendations = pso.selected_activities
        self.activity_queue = recommendations
        self.current_activity_index = 0

        # Show the first activity for feedback
        self.show_activity_for_feedback()

    def show_activity_for_feedback(self):
        """Show the next activity and allow feedback submission"""
        if self.current_activity_index < len(self.activity_queue):
            activity = self.activity_queue[self.current_activity_index]
            self.label.setText(f"How did {activity} make you feel?")
            self.submit_button.setEnabled(True)
        else:
            self.label.setText("Thank you for your feedback!")
            self.submit_button.setEnabled(False)
            QTimer.singleShot(2000, self.reset_ui)

    def submit_feedback(self):
        """Collect mood feedback from the slider and show success message"""
        mood_score = self.slider.value()
        activity = self.activity_queue[self.current_activity_index]

        # Save feedback using the correct function
        pso.save_mood_feedback(activity, mood_score)

        # Proceed to the next activity
        self.current_activity_index += 1
        self.slider.setValue(5)  # Reset slider to default

        # Show the next activity for feedback
        self.show_activity_for_feedback()


    def reset_ui(self):
        """Reset the UI to allow for new recommendations and feedback"""
        self.label.setText("Click below to get your mental health recommendation")
        self.activity_queue = []
        self.current_activity_index = 0
        self.submit_button.setEnabled(False)
        self.slider.setValue(5)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MentalHealthApp()
    window.show()
    sys.exit(app.exec_())
