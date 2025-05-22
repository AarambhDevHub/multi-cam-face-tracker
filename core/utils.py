import cv2
import numpy as np
from typing import Tuple, Optional
from loguru import logger
import time
from PyQt5.QtGui import QPixmap

def draw_face_info(image: np.ndarray, 
                  face_bbox: Tuple[int, int, int, int],
                  name: Optional[str] = None,
                  confidence: Optional[float] = None,
                  age: Optional[int] = None,
                  gender: Optional[str] = None,
                  camera_name: Optional[str] = None,
                  timestamp: Optional[float] = None) -> np.ndarray:
    """
    Draw face bounding box and information on the image
    """
    try:
        img = image.copy()
        x1, y1, x2, y2 = map(int, face_bbox)
        
        # Draw bounding box
        color = (0, 255, 0) if name else (0, 0, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Create info text
        info_text = []
        if name:
            info_text.append(f"Name: {name}")
        if confidence is not None:
            info_text.append(f"Confidence: {confidence:.2f}")
        if age:
            info_text.append(f"Age: {age}")
        if gender:
            info_text.append(f"Gender: {gender}")
        if camera_name:
            info_text.append(f"Camera: {camera_name}")
        if timestamp:
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            info_text.append(f"Time: {time_str}")
        
        # Draw text background
        text_y = y1 - 10 if y1 - 10 > 10 else y2 + 20
        for i, text in enumerate(info_text):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(img, 
                         (x1, text_y - 15 - i * 20),
                         (x1 + text_size[0] + 5, text_y - i * 20),
                         color, -1)
            
            # Draw text
            cv2.putText(img, text, 
                       (x1 + 3, text_y - 5 - i * 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                       (0, 0, 0), 1)
                       
        return img
        
    except Exception as e:
        logger.error(f"Error drawing face info: {e}")
        return image

def numpy_to_pixmap(image: np.ndarray) -> 'QPixmap':
    """Convert numpy array to QPixmap"""
    try:
        from PyQt5.QtGui import QImage, QPixmap
        from PyQt5.QtCore import Qt
        
        if image is None:
            return QPixmap()
            
        if len(image.shape) == 2:  # Grayscale
            h, w = image.shape
            qimg = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
        else:  # BGR
            h, w, ch = image.shape
            bytes_per_line = ch * w
            qimg = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)
            
        return QPixmap.fromImage(qimg).scaled(
            w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
    except Exception as e:
        logger.error(f"Error converting numpy to QPixmap: {e}")
        return QPixmap()

def resize_image(image: np.ndarray, max_width: int = 800, max_height: int = 600) -> np.ndarray:
    """Resize image while maintaining aspect ratio"""
    try:
        if image is None:
            return None
            
        h, w = image.shape[:2]
        
        if w <= max_width and h <= max_height:
            return image
            
        ratio = min(max_width / w, max_height / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return image