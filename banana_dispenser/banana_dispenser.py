import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QLabel, QSizePolicy
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        
        # Create the stacked widget that will hold multiple pages
        self.stacked_widget = QStackedWidget(self)
        
        # Create main page and settings page
        self.main_page = QWidget()
        self.settings_page = SettingsPage(self.back_to_main)
        
        # Set up layouts for each page
        self.setup_main_page()
        
        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Set the stacked widget layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        
        # Show the first page (main page) initially
        self.stacked_widget.setCurrentWidget(self.main_page)

    def setup_main_page(self):
        layout = QHBoxLayout(self.main_page)
        
        # Create buttons
        self.button_start = QPushButton("Start")
        self.button_setting = QPushButton("Setting")
        self.button_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_setting.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Connect setting button to show settings page
        self.button_setting.clicked.connect(self.show_settings)
        
        # Add buttons to layout
        layout.addWidget(self.button_start)
        layout.addWidget(self.button_setting)

    def show_settings(self):
        # Switch to the settings page
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def back_to_main(self):
        # Switch to the main page
        self.stacked_widget.setCurrentWidget(self.main_page)


class SettingsPage(QWidget):
    def __init__(self, on_back_click=None):
        super().__init__()
        self.setWindowTitle("Settings Page")
        
        layout = QVBoxLayout(self)
        
        # Add a label to the settings page
        label = QLabel("This is the Settings Page")
        layout.addWidget(label)
        
        # Add a button to go back to the main page
        back_button = QPushButton("Back to Main Page")
        back_button.clicked.connect(on_back_click)
        layout.addWidget(back_button)



def program():
    app = QApplication(sys.argv)
    
    # Show the main window
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    
    app.exec()
if __name__ == "__main__":
    program()