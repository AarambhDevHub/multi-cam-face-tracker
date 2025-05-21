import os
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from loguru import logger
# from playsound import playsound
import cv2
import numpy as np
from pathlib import Path
from pygame import mixer

# The `@dataclass` decorator in Python is used to automatically generate special methods such as
# `__init__`, `__repr__`, `__eq__`, and `__hash__` for a class. In this specific case, the
# `AlertEvent` class is a data class that represents an alert event with the following attributes:
@dataclass
class AlertEvent:
    camera_id: int
    camera_name: str
    face_name: str
    confidence: float
    timestamp: float
    screenshot_path: Optional[str] = None

class AlertSystem:
    def __init__(self, config: dict):
        self.config = config
        self.alert_sound = config['app']['alert_sound']
        self.screenshot_dir = Path(config['app']['screenshot_dir'])
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.alert_history: List[AlertEvent] = []
        self.alert_enabled = True
        self.screenshot_enabled = True
        mixer.init()  # Add this at the start of your application

        
    def trigger_alert(self, camera_id: int, camera_name: str, face_name: str, confidence: float, frame: np.ndarray) -> AlertEvent:
        """Trigger an alert for a recognized face"""
        timestamp = time.time()
        screenshot_path = None
        
        if self.screenshot_enabled:
            screenshot_path = self._capture_screenshot(frame, camera_id, face_name, timestamp)
         # Ensure the path is converted to string and is not None when empty
        
        event = AlertEvent(
            camera_id=camera_id,
            camera_name=camera_name,
            face_name=face_name,
            confidence=confidence,
            timestamp=timestamp,
            screenshot_path=str(screenshot_path) if screenshot_path is not None else None
        )
        logger.debug(f"Event created with screenshot path: {event.screenshot_path}")  # Debug log
        self.alert_history.append(event)
        
        if self.alert_enabled:
            self._play_alert_sound()
            
        logger.info(f"Alert triggered: {face_name} detected on {camera_name} with confidence {confidence:.2f}")
        return event
        
    def _play_alert_sound(self) -> None:
        """
        The function `_play_alert_sound` attempts to play an alert sound file using the `mixer.music`
        module in Python, logging an error if there is an exception.
        """
        try:
            if os.path.exists(self.alert_sound):
                # playsound(self.alert_sound, block=False)
                  mixer.music.load(self.alert_sound)
                  mixer.music.play()
        except Exception as e:
            logger.error(f"Error playing alert sound: {e}")

    def _capture_screenshot(self, frame: np.ndarray, camera_id: int, face_name: str, timestamp: float) -> Optional[Path]:
        """Capture and save a screenshot of the alert"""
        try:
            timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
            filename = f"{timestamp_str}_cam{camera_id}_{face_name}.jpg"
            filepath = self.screenshot_dir / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the image
            success = cv2.imwrite(str(filepath), frame)
            if not success:
                logger.error(f"Failed to save screenshot to {filepath}")
                return None
                
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def get_recent_alerts(self, limit: int = 10) -> List[AlertEvent]:
        """Get most recent alerts"""
        return sorted(self.alert_history, key=lambda x: x.timestamp, reverse=True)[:limit]

    def clear_alerts(self) -> None:
        """Clear alert history"""
        self.alert_history.clear()

    def enable_alerts(self, enabled: bool) -> None:
        """Enable or disable alerts"""
        self.alert_enabled = enabled
        logger.info(f"Alerts {'enabled' if enabled else 'disabled'}")

    def enable_screenshots(self, enabled: bool) -> None:
        """Enable or disable screenshot capture"""
        self.screenshot_enabled = enabled
        logger.info(f"Screenshots {'enabled' if enabled else 'disabled'}")