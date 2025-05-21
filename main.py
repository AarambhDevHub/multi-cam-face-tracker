"""
Multi-Camera Face Tracker System
--------------------------------
This is the main entry point for launching the facial recognition and tracking application.
It initializes the GUI, camera streams, face detection, recognition, alert system, and database.

Features:
- Real-time face detection and recognition across multiple camera feeds
- Target face matching with alert notification
- Event logging with timestamp and screenshot
- User-friendly desktop UI built with PyQt5

Author: Darshan Vichhi (Aarambh Dev Hub)
Created: 2025-05-21
"""



import sys
import yaml
from pathlib import Path
from loguru import logger
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

from ui.main_window import MainWindow

def load_config(config_path: str) -> dict:
    """
    Load the application's configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Parsed configuration settings as a dictionary.

    Side Effects:
        - Creates necessary directories for screenshots, known faces, and logs if they do not exist.

    Raises:
        Exception: If the configuration file cannot be read or parsed.

    Usage:
        config = load_config('config/config.yaml')
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Ensure required directories exist
        Path(config['app']['screenshot_dir']).mkdir(parents=True, exist_ok=True)
        Path(config['app']['known_faces_dir']).mkdir(parents=True, exist_ok=True)
        Path(config['app']['log_dir']).mkdir(parents=True, exist_ok=True)
        
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise

def setup_logging(log_dir: str):
    """
    Initialize application logging using loguru.

    Args:
        log_dir (str): Directory where log files should be stored.

    Behavior:
        - Creates rotating log files for general logs and error logs.
        - Retains log history for maintenance and debugging.

    Log Files:
        - app.log (INFO level, rotated every 10MB, kept for 7 days)
        - error.log (ERROR level, rotated every 10MB, kept for 30 days)

    Usage:
        setup_logging(config['app']['log_dir'])
    """
    logger.add(
        f"{log_dir}/app.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )
    logger.add(
        f"{log_dir}/error.log",
        rotation="10 MB",
        retention="30 days",
        level="ERROR"
    )


def show_splash_screen(config: dict) -> QSplashScreen:
    """Create and display splash screen with logo"""
    try:
        # Get logo path from config with fallback
        logo_path = config.get('app', {}).get('logo', 'assets/logo.png')
        
        # Verify logo exists
        if not Path(logo_path).exists():
            raise FileNotFoundError(f"Logo file not found: {logo_path}")
        
        splash_pix = QPixmap(logo_path)
        if splash_pix.isNull():
            raise ValueError(f"Invalid logo image: {logo_path}")
            
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())

        splash.showMessage(
            "Initializing Face Tracker...",
            Qt.AlignBottom | Qt.AlignCenter,
            Qt.white
        )
        QApplication.processEvents()  # Force UI update
        
        return splash
        
    except Exception as e:
        print(f"Error loading splash screen: {e}")
        # Fallback to blank splash if logo fails
        return QSplashScreen(QPixmap(800, 400))


def main():
    """
    Main entry point of the Multi-Camera Face Tracker System.

    Behavior:
        - Loads application configuration from YAML.
        - Sets up logging to file.
        - Initializes and launches the PyQt5 user interface.
        - Starts the event loop for the desktop application.

    Error Handling:
        - Logs critical error and exits gracefully if any part of initialization fails.
    """
    try:
        # Load configuration
        config = load_config('config/config.yaml')
        
        # Setup logging
        setup_logging(config['app']['log_dir'])
        
        # Create and run application
        app = QApplication(sys.argv)

        splash = show_splash_screen(config)
        splash.show()

        app.processEvents()

        window = MainWindow(config)
        
        def show_ai_loading():
            splash.showMessage(
                "Loading AI Models...",
                Qt.AlignBottom | Qt.AlignCenter,
                Qt.white
            )
            QApplication.processEvents()
            
            # Setup final close timer
            QTimer.singleShot(1500, lambda: splash.finish(window))
        
        # Initial delay before showing AI message
        QTimer.singleShot(2000, show_ai_loading)

        QTimer.singleShot(3500, lambda: window.show())


        logger.info("Application started successfully")
        def on_close():
            window.camera_manager.stop_all_cameras()
            window.alert_system.shutdown()
            app.quit()
            
        app.aboutToQuit.connect(on_close)

        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()