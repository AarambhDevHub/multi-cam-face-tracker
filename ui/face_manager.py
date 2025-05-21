import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                            QLabel, QFileDialog, QMessageBox, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from loguru import logger
import cv2
import numpy as np
from pathlib import Path

from core.utils import numpy_to_pixmap, resize_image

class FaceManagerDialog(QDialog):
    def __init__(self, face_detector, known_faces_dir):
        """
        Initialize the FaceManagerDialog.

        Args:
            face_detector: An instance responsible for face detection and management.
            known_faces_dir (str or Path): Directory path where known face images are stored.
        """
        super().__init__()
        self.face_detector = face_detector
        self.known_faces_dir = known_faces_dir
        self.current_image = None
        
        self.setWindowTitle("Face Manager")
        self.setGeometry(200, 200, 800, 600)
        
        self.init_ui()
        self.load_face_list()
        
    def init_ui(self):
        """
        Set up the UI components of the dialog, including face list, preview,
        input fields, and control buttons.
        """
        layout = QVBoxLayout()
        
        # Top section - face list and controls
        top_layout = QHBoxLayout()
        
        # Face list
        self.face_list = QListWidget()
        self.face_list.currentItemChanged.connect(self.on_face_selected)
        top_layout.addWidget(self.face_list, 3)
        
        # Face preview
        self.face_preview = QLabel()
        self.face_preview.setAlignment(Qt.AlignCenter)
        self.face_preview.setMinimumSize(300, 300)
        top_layout.addWidget(self.face_preview, 2)
        
        layout.addLayout(top_layout)
        
        # Middle section - face details
        middle_layout = QHBoxLayout()
        
        # Name input
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        middle_layout.addLayout(name_layout)
        
        layout.addLayout(middle_layout)
        
        # Bottom section - buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Face")
        self.add_btn.clicked.connect(self.add_face)
        button_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("Update Face")
        self.update_btn.clicked.connect(self.update_face)
        button_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("Delete Face")
        self.delete_btn.clicked.connect(self.delete_face)
        button_layout.addWidget(self.delete_btn)
        
        self.import_btn = QPushButton("Import Image")
        self.import_btn.clicked.connect(self.import_image)
        button_layout.addWidget(self.import_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_face_list(self):
        """
        Load and display all face images from the known faces directory into the list widget.
        Only image files with extensions .jpg, .jpeg, .png are considered.
        """
        self.face_list.clear()
        known_faces_dir = Path(self.known_faces_dir)
        
        if not known_faces_dir.exists():
            logger.warning(f"Known faces directory {known_faces_dir} does not exist")
            return
            
        for face_file in known_faces_dir.glob('*.*'):
            if face_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                self.face_list.addItem(face_file.stem)
                
    def on_face_selected(self, current, previous):
        """
        Triggered when a face is selected from the list.

        Loads and displays the corresponding face image in the preview area
        and updates the name input field.

        Args:
            current: The currently selected QListWidgetItem.
            previous: The previously selected QListWidgetItem.
        """
        if current is None:
            self.face_preview.clear()
            self.name_input.clear()
            return
            
        face_name = current.text()
        self.name_input.setText(face_name)
        
        # Load and display the face image
        face_path = Path(self.known_faces_dir) / f"{face_name}{self.get_face_extension(face_name)}"
        if not face_path.exists():
            QMessageBox.warning(self, "Error", f"Image file not found: {face_path}")
            return
            
        try:
            image = cv2.imread(str(face_path))
            if image is None:
                raise ValueError("Could not read image")
                
            self.current_image = image
            pixmap = numpy_to_pixmap(image)
            self.face_preview.setPixmap(pixmap.scaled(
                self.face_preview.width(), self.face_preview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            logger.error(f"Error loading face image: {e}")
            
    def get_face_extension(self, face_name: str) -> str:
        """
        Search for the file extension of a face image by checking common image formats.

        Args:
            face_name (str): The base filename (without extension) of the face.

        Returns:
            str: The file extension including the dot (e.g., '.jpg'), or empty string if not found.
        """
        known_faces_dir = Path(self.known_faces_dir)
        for ext in ['.jpg', '.jpeg', '.png']:
            if (known_faces_dir / f"{face_name}{ext}").exists():
                return ext
        return ''
        
    def add_face(self):
        """
        Add a new face image to the known faces directory and update the face detector.

        Checks if a name is entered and an image is loaded, prevents overwriting existing faces.
        Shows relevant messages for success or errors.
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name for the face")
            return
            
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Please import or select an image first")
            return
            
        # Check if face already exists
        existing_files = list(Path(self.known_faces_dir).glob(f"{name}.*"))
        if existing_files:
            QMessageBox.warning(self, "Error", f"A face with name '{name}' already exists")
            return
            
        # Add the face
        success = self.face_detector.add_known_face(
            self.current_image, name, self.known_faces_dir)
            
        if success:
            QMessageBox.information(self, "Success", f"Face '{name}' added successfully")
            self.load_face_list()
        else:
            QMessageBox.warning(self, "Error", "Failed to add face")
            
    def update_face(self):
        """
        Update an existing face image and/or rename it.

        Validates that a face is selected, name input is filled, and image is loaded.
        Renames the file if the name has changed and saves the new image.
        Reloads known faces in the detector and refreshes the UI.
        """
        current_item = self.face_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Error", "Please select a face to update")
            return
            
        old_name = current_item.text()
        new_name = self.name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "Error", "Please enter a name for the face")
            return
            
        if self.current_image is None:
            QMessageBox.warning(self, "Error", "Please import or select an image first")
            return
            
        # Rename file if name changed
        if old_name != new_name:
            old_path = Path(self.known_faces_dir) / f"{old_name}{self.get_face_extension(old_name)}"
            new_path = Path(self.known_faces_dir) / f"{new_name}{old_path.suffix}"
            
            if new_path.exists():
                QMessageBox.warning(self, "Error", f"A face with name '{new_name}' already exists")
                return
                
            try:
                old_path.rename(new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename face: {str(e)}")
                return
                
        # Update the face image if it's different
        try:
            current_path = Path(self.known_faces_dir) / f"{new_name}{self.get_face_extension(new_name)}"
            cv2.imwrite(str(current_path), self.current_image)
            
            # Reload the face in the detector
            self.face_detector.load_known_faces(self.known_faces_dir)
            
            QMessageBox.information(self, "Success", "Face updated successfully")
            self.load_face_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update face: {str(e)}")
            
    def delete_face(self):
        """
        Delete the selected face image from the known faces directory.

        Asks for user confirmation before deleting.
        Refreshes the face list and reloads the face detector on success.
        """
        current_item = self.face_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Error", "Please select a face to delete")
            return
            
        name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete face '{name}'?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.No:
            return
            
        # Delete the face file
        face_path = Path(self.known_faces_dir) / f"{name}{self.get_face_extension(name)}"
        try:
            face_path.unlink()
            
            # Reload the face list and detector
            self.face_detector.load_known_faces(self.known_faces_dir)
            self.load_face_list()
            
            QMessageBox.information(self, "Success", "Face deleted successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete face: {str(e)}")
            
    def import_image(self):
        """
        Open a file dialog to select an image file to import.

        Loads the selected image, shows a preview, and fills the name input with the filename stem.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)")
            
        if not file_path:
            return
            
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not read image")
                
            self.current_image = image
            pixmap = numpy_to_pixmap(image)
            self.face_preview.setPixmap(pixmap.scaled(
                self.face_preview.width(), self.face_preview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
            # Suggest a name based on the filename
            suggested_name = Path(file_path).stem
            self.name_input.setText(suggested_name)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            logger.error(f"Error importing image: {e}")