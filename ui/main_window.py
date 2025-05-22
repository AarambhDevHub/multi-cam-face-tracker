import sys
import time
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QTabWidget, QScrollArea, QGridLayout,
                            QMessageBox, QFileDialog, QComboBox, QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QIcon
from loguru import logger
from typing import Dict, Optional, Tuple
import numpy as np
import cv2
from pathlib import Path

from core.face_detection import FaceDetector
from core.camera_manager import CameraManager
from core.alert_system import AlertEvent, AlertSystem
from core.database import FaceDatabase
from core.utils import numpy_to_pixmap, resize_image, draw_face_info
from .face_manager import FaceManagerDialog
from .alert_panel import AlertPanel
from .history_viewer import HistoryViewer

class MainWindow(QMainWindow):
    def __init__(self, config):
        """
        Initialize the main window and all core components.
        
        Args:
            config (dict): The application configuration dictionary.
        """
        super().__init__()
        self.config = config
        self.setWindowTitle(f"{config['app']['name']} v{config['app']['version']}")
        self.setWindowIcon(QIcon(config['app']['logo']))
        self.setGeometry(100, 100, 1200, 800)
        
        self.processing_interval = 0.5  # seconds
        # Initialize core components
        self.face_detector = FaceDetector(config)
        self.camera_manager = CameraManager('config/camera_config.yaml')
        self.alert_system = AlertSystem(config)
        self.database = FaceDatabase(config['app']['database_path'])
        
        # Load known faces
        self.face_detector.load_known_faces(config['app']['known_faces_dir'])
        
        # UI Components
        self.init_ui()
        
        # Start camera threads
        self.camera_manager.start_all_cameras()
        
        # Setup update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(30)  # ~30 FPS
        
        # Track last processed time per camera to limit processing
        self.last_processed: Dict[int, float] = {}
        
    def init_ui(self):
        """
        Set up the main user interface, including tabs, layouts, and status/menu bars.
        """
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.setup_monitor_tab()
        self.setup_controls_tab()
        self.setup_history_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Menu bar
        self.setup_menu_bar()
        
    def setup_menu_bar(self):
        """
        Set up the application's menu bar with actions like exiting, opening tools, and toggling fullscreen.
        """
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        face_manager_action = tools_menu.addAction('Face Manager')
        face_manager_action.triggered.connect(self.open_face_manager)
        
        alert_panel_action = tools_menu.addAction('Alert Panel')
        alert_panel_action.triggered.connect(self.open_alert_panel)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        fullscreen_action = view_menu.addAction('Toggle Fullscreen')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
    def setup_monitor_tab(self):
        """
        Set up the 'Monitor' tab which displays live camera feeds in a scrollable grid layout.
        """

        monitor_tab = QWidget()
        self.tab_widget.addTab(monitor_tab, "Monitor")
        
        # Scroll area for camera feeds
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container for camera feeds
        self.camera_container = QWidget()
        self.camera_grid = QGridLayout(self.camera_container)
        self.camera_grid.setSpacing(10)
        
        scroll.setWidget(self.camera_container)
        
        # Layout for monitor tab
        layout = QVBoxLayout(monitor_tab)
        layout.addWidget(scroll)
        
        # Add camera labels
        self.camera_labels = {}
        for cam_id in self.camera_manager.cameras:
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(400, 300)
            self.camera_labels[cam_id] = label
            self.camera_grid.addWidget(label, (cam_id // 2), (cam_id % 2))
            
    def setup_controls_tab(self):
        """
        Set up the 'Controls' tab, which allows users to start/stop cameras,
        adjust recognition threshold, and modify processing intervals.
        """
        controls_tab = QWidget()
        self.tab_widget.addTab(controls_tab, "Controls")
        
        layout = QVBoxLayout(controls_tab)
        
        # Camera controls
        camera_group = QWidget()
        camera_layout = QVBoxLayout(camera_group)
        
        camera_title = QLabel("Camera Controls")
        camera_title.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(camera_title)
        
        # Camera selection combo
        self.camera_combo = QComboBox()
        for cam_id, cam_config in self.camera_manager.cameras.items():
            self.camera_combo.addItem(f"Camera {cam_id}: {cam_config.name}", cam_id)
        camera_layout.addWidget(self.camera_combo)
        
        # Camera control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_selected_camera)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_selected_camera)
        btn_layout.addWidget(self.stop_btn)
        
        camera_layout.addLayout(btn_layout)
        
        # Recognition threshold control
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Recognition Threshold:")
        threshold_layout.addWidget(threshold_label)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(50, 100)  # 0.5 to 1.0 in 0.01 increments
        self.threshold_slider.setValue(int(self.config['recognition']['recognition_threshold'] * 100))
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_value = QLabel(f"{self.threshold_slider.value() / 100:.2f}")
        threshold_layout.addWidget(self.threshold_value)
        
        camera_layout.addLayout(threshold_layout)
        
        layout.addWidget(camera_group)
        
        # Processing interval control
        interval_group = QWidget()
        interval_layout = QHBoxLayout(interval_group)
        
        interval_label = QLabel("Processing Interval (ms):")
        interval_layout.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 5000)
        self.interval_spin.setValue(int(self.processing_interval * 1000))
        self.interval_spin.valueChanged.connect(self.update_processing_interval)
        interval_layout.addWidget(self.interval_spin)
        
        layout.addWidget(interval_group)
        
        # Status display
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        
        status_title = QLabel("System Status")
        status_title.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_title)
        
        self.status_display = QLabel("Loading status...")
        self.status_display.setWordWrap(True)
        status_layout.addWidget(self.status_display)
        
        layout.addWidget(status_group)
        
    def setup_history_tab(self):
        """
        Set up the 'History' tab, which displays historical records of recognized faces or alerts.
        """
        self.history_viewer = HistoryViewer(self.database, self.config)
        self.tab_widget.addTab(self.history_viewer, "History")
        
    def open_face_manager(self):
        """
        Open the face manager dialog to allow adding or removing known faces,
        and reloads known faces into the face detector after closing the dialog.
        """
        dialog = FaceManagerDialog(self.face_detector, self.config['app']['known_faces_dir'])
        dialog.exec_()
        # Refresh known faces after dialog closes
        self.face_detector.load_known_faces(self.config['app']['known_faces_dir'])
        
    def open_alert_panel(self):
        """
        Open the alert panel dialog to view and manage triggered alerts.
        """
        dialog = AlertPanel(self.alert_system)
        dialog.exec_()
        
    def toggle_fullscreen(self):
        """
        Toggle the application's fullscreen mode.
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def start_selected_camera(self):
        """
        Start the camera selected from the combo box.
        Updates the status label upon success.
        """
        cam_id = self.camera_combo.currentData()
        if self.camera_manager.start_camera(cam_id):
            self.status_label.setText(f"Started camera {cam_id}")
            
    def stop_selected_camera(self):
        """
        Stop the camera selected from the combo box.
        Updates the status label upon success.
        """
        cam_id = self.camera_combo.currentData()
        if self.camera_manager.stop_camera(cam_id):
            self.status_label.setText(f"Stopped camera {cam_id}")
            
    def update_threshold(self, value):
        """
        Update the face recognition threshold used by the face detector.
        
        Args:
            value (int): New threshold slider value (scaled to 0.0 - 1.0).
        """
        threshold = value / 100
        self.face_detector.recognition_threshold = threshold
        self.threshold_value.setText(f"{threshold:.2f}")
        
    def update_processing_interval(self, value):
        """
        Update the interval (in seconds) for how frequently frames should be processed.
        
        Args:
            value (int): Interval in milliseconds.
        """
        self.processing_interval = value / 1000
        
    def update(self):
        """
        Main update loop called by the QTimer every ~30ms.
        It fetches frames from cameras, processes them if the interval allows,
        and displays them on the GUI. Also updates system status.
        """
        try:
            # Update camera feeds
            frames = self.camera_manager.get_all_frames()
            
            for cam_id, frame in frames.items():
                if frame is None:
                    continue
                    
                # Check if we should process this frame
                current_time = time.time()
                last_time = self.last_processed.get(cam_id, 0)
                if current_time - last_time < self.processing_interval:
                    # Just display the frame without processing
                    self.display_frame(cam_id, frame)
                    continue
                    
                # Process the frame (face detection and recognition)
                processed_frame, alert_triggered = self.process_frame(cam_id, frame)
                
                # Display the processed frame
                self.display_frame(cam_id, processed_frame)
                
                # Update last processed time
                self.last_processed[cam_id] = current_time
                
            # Update status display
            self.update_status()
            
        except Exception as e:
            logger.error(f"Error in update loop: {e}")
            self.status_label.setText(f"Error: {str(e)}")
            
    def process_frame(self, cam_id: int, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Process a video frame for face detection and recognition.

        Args:
            cam_id (int): ID of the camera providing the frame.
            frame (np.ndarray): The frame to process.

        Returns:
            Tuple[np.ndarray, bool]: The processed frame and a boolean indicating if an alert was triggered.
        """
        alert_triggered = False
        try:
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            if not faces:
                return frame, False
                
            # Recognize faces
            recognized_faces = self.face_detector.recognize_faces(faces)
            
            # Draw face info and check for alerts
            for face, known_face, confidence in recognized_faces:
                camera_name = self.camera_manager.cameras[cam_id].name
                
                if known_face:
                    # Known face detected
                    frame = draw_face_info(
                        frame, face.bbox,
                        name=known_face.name,
                        confidence=confidence,
                        camera_name=camera_name,
                        age=face.age,
                        gender=face.gender,
                        timestamp=time.time()
                    )
                    
                    # Trigger alert
                    alert_event = self.alert_system.trigger_alert(
                        cam_id, camera_name,
                        known_face.name, face, confidence,
                        frame
                    )
                    alert_triggered = True
                    
                    # Log to database
                    self.database.log_face_event(alert_event)
                else:
                    # Unknown face
                    frame = draw_face_info(
                        frame, face.bbox,
                        name="Unknown",
                        confidence=confidence,
                        camera_name=camera_name,
                        timestamp=time.time()
                    )
                    
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            
        return frame, alert_triggered
        
    def display_frame(self, cam_id: int, frame: np.ndarray):
        """
        Display the processed frame in the corresponding camera view.

        Args:
            cam_id (int): ID of the camera.
            frame (np.ndarray): Frame to display.
        """
        try:
            if frame is None:
                return
                
            # Convert to QPixmap and display
            pixmap = numpy_to_pixmap(frame)
            self.camera_labels[cam_id].setPixmap(pixmap)
            
        except Exception as e:
            logger.error(f"Error displaying frame: {e}")
            
    def update_status(self):
        """
        Update the application's status display with:
        - Camera running/stopped status
        - Known faces in the database
        - Recent alerts (last 3)
        """
        try:
            status_text = []
            
            # Camera status
            status_text.append("=== Camera Status ===")
            for cam_id, cam_config in self.camera_manager.cameras.items():
                running = cam_id in self.camera_manager.capture_threads
                status_text.append(
                    f"Camera {cam_id} ({cam_config.name}): {'Running' if running else 'Stopped'}"
                )
                
            # Face database status
            status_text.append("\n=== Face Database ===")
            status_text.append(f"Known faces: {len(self.face_detector.known_faces)}")
            
            # Alert status
            status_text.append("\n=== Alerts ===")
            recent_alerts = self.alert_system.get_recent_alerts(3)
            if recent_alerts:
                for alert in recent_alerts:
                    time_str = time.strftime("%H:%M:%S", time.localtime(alert.timestamp))
                    status_text.append(
                        f"{time_str}: {alert.face_name} on {alert.camera_name} "
                        f"(Confidence: {alert.confidence:.2f})"
                    )
            else:
                status_text.append("No recent alerts")
                
            self.status_display.setText("\n".join(status_text))
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            
    def closeEvent(self, event):
        """
        Handle the application window close event.

        Performs cleanup:
        - Stops all camera threads
        - Stops the UI update timer
        - Saves configuration (if needed)
        """
        try:
            # Stop all cameras
            self.camera_manager.stop_all_cameras()
            
            # Stop update timer
            self.update_timer.stop()
            
            # Save configuration
            # (Add configuration saving logic here if needed)
            
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()