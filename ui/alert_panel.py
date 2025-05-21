from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                            QLabel, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt
from loguru import logger
import time

class AlertPanel(QDialog):
    def __init__(self, alert_system):
        super().__init__()
        self.alert_system = alert_system
        self.setWindowTitle("Alert Panel")
        self.setGeometry(300, 300, 600, 400)
        
        self.init_ui()
        self.load_alerts()
        
    def init_ui(self):
        """Set up and arrange all the UI widgets including the alert list, checkboxes, and control buttons."""
        layout = QVBoxLayout()
        
        # Alert list
        self.alert_list = QListWidget()
        layout.addWidget(self.alert_list)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.enable_alerts_check = QCheckBox("Enable Alerts")
        self.enable_alerts_check.setChecked(self.alert_system.alert_enabled)
        self.enable_alerts_check.stateChanged.connect(self.toggle_alerts)
        controls_layout.addWidget(self.enable_alerts_check)
        
        self.enable_screenshots_check = QCheckBox("Enable Screenshots")
        self.enable_screenshots_check.setChecked(self.alert_system.screenshot_enabled)
        self.enable_screenshots_check.stateChanged.connect(self.toggle_screenshots)
        controls_layout.addWidget(self.enable_screenshots_check)
        
        self.clear_btn = QPushButton("Clear Alerts")
        self.clear_btn.clicked.connect(self.clear_alerts)
        controls_layout.addWidget(self.clear_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        controls_layout.addWidget(self.close_btn)
        
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
    def load_alerts(self):
        """Fetch the latest 50 alerts from the alert system and display them in the alert list with timestamp, face name, camera, and confidence score."""
        self.alert_list.clear()
        alerts = self.alert_system.get_recent_alerts(50)  # Load last 50 alerts
        
        for alert in alerts:
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert.timestamp))
            item_text = f"{time_str} - {alert.face_name} on {alert.camera_name} (Confidence: {alert.confidence:.2f})"
            self.alert_list.addItem(item_text)
            
    def toggle_alerts(self, state):
        """Enable or disable alert sounds based on the checkbox state."""
        self.alert_system.enable_alerts(state == Qt.Checked)
        
    def toggle_screenshots(self, state):
        """Enable or disable automatic screenshot capture on alerts based on the checkbox state."""
        self.alert_system.enable_screenshots(state == Qt.Checked)
        
    def clear_alerts(self):
        """Ask for user confirmation and clear all stored alerts if confirmed, updating the alert list display."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all alerts?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.alert_system.clear_alerts()
            self.alert_list.clear()