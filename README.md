# Multi-Camera Face Tracker System 🚀

<div align="center">
  <img src="https://raw.githubusercontent.com/AarambhDevHub/multi-cam-face-tracker/main/assets/logo.png" alt="Logo" width="200" height="200">
</div>

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![InsightFace](https://img.shields.io/badge/ML-InsightFace-orange)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-red)
![Telegram](https://img.shields.io/badge/Alerts-Telegram-blue)


A robust real-time face tracking system with multi-camera support, facial recognition, age & gender detection, and intelligent alerting capabilities including Telegram notifications.

## 🌟 Key Features

### Core Functionality
- **Multi-Camera Support**: Simultaneously monitor multiple video sources (webcams, RTSP streams, video files)
- **Real-Time Face Detection**: Powered by InsightFace with GPU acceleration support
- **Face Recognition**: Identify known individuals with configurable confidence thresholds
- **Age & Gender Detection**: Estimate demographic attributes for each detected face

### Alert System
- ✨ **Telegram Notifications**: Get instant alerts with snapshots on your phone
- 🔔 **Visual & Audio Alerts**: Customizable popups and sound notifications
- 📸 **Automatic Evidence Capture**: Saves screenshots of recognition events
- 📊 **Comprehensive Logging**: Detailed event records with timestamps and confidence levels

### User Interface
- 🖥️ **Live Monitoring Dashboard**: View all camera feeds in real-time
- 👤 **Face Management**: Add/remove known faces with photo uploads
- ⏱️ **History Viewer**: Filter events by date, camera, or individual

## 🛠️ Technical Stack

| Component               | Technology Used               |
|-------------------------|-------------------------------|
| Face Detection          | InsightFace                   |
| Machine Learning        | PyTorch                       |
| Computer Vision         | OpenCV                        |
| GUI Framework           | PyQt5                         |
| Database                | SQLite                        |
| Audio Alerts            | Pygame                        |
| Telegram Alerts         | python-telegram-bot           |
| **Alert Channels**      | Telegram Bot                  |
| Demographics            | Age & Gender via InsightFace  |

## 📦 Installation Guide

### Prerequisites
- Python 3.8+
- NVIDIA GPU (recommended for best performance)
- FFmpeg (for RTSP streams)

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AarambhDevHub/multi-cam-face-tracker.git
   cd multi-cam-face-tracker
   ```

2. **Create virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the system**:
    - Edit `config/config.yaml` for application settings
    - Edit `config/camera_config.yaml` for camera configurations

5. **Directory setup**:
    ```bash
    mkdir -p data/{known_faces,screenshots} config logs
    ```

6. Run the application:
    ```
    python main.py
    ```

## ⚙️ Configuration

### Application Settings (`config/config.yaml`)
```yaml
app:
  name: "Multi-Cam Face Tracker"
  version: "1.0.0"
  threshold: 0.6
  screenshot_dir: "data/screenshots"
  known_faces_dir: "data/known_faces"
  database_path: "data/database.db"
  alert_sound: "assets/alert.wav"
  log_dir: "logs"
recognition:
  detection_threshold: 0.5
  recognition_threshold: 0.6
  max_batch_size: 8
  device: "cpu"  # or "cuda"
  age_estimation: true
  gender_detection: true
```

### Camera Configuration (`config/camera_config.yaml`)
```yaml
cameras:
  - id: 0
    name: "Front Camera"
    source: 0  # Camera index or RTSP URL # Camera index or "rtsp://..."
    enabled: true
    resolution:
      width: 1280
      height: 720
    fps: 30
    rotate: 0 # Degrees (0,90,180,270)
```

## ⚙️ Telegram Configuration
### Add to `config/config.yaml`:
```yaml
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN"  # From @BotFather
  chat_id: "YOUR_CHAT_ID"      # Get from @getidsbot
  rate_limit: 30  # Seconds between alerts
```
## Setup Guide:
- Create bot with @BotFather
- Get chat ID with @getidsbot
- Add bot to your alert channel as admin
- Enable in config and restart app

## 🔍 Learn More on DeepWiki
Want to dive deeper into how this system works, including architecture insights and real-world deployment tips?
📖 Explore the project on DeepWiki:
👉 [https://deepwiki.com/AarambhDevHub/multi-cam-face-tracker](https://deepwiki.com/AarambhDevHub/multi-cam-face-tracker)

## 🖥️ User Manual
### Adding Known Faces
1. Click "Face Manager" in the Tools menu
2. Select "Add Face" and upload a clear photo
3. Enter the person's name and save

### Camera Controls
    Button	                    Functionality
    ▶️ Start	      Activates selected camera feed
    ⏹️ Stop	                Halts camera processing
    ⚙️ Settings	          Adjust resolution/FPS
    
### Alert Management
- Configure sound preferences in Alert Panel
- Set minimum confidence threshold (0.5-1.0)
- Enable/disable screenshot capture
- View age and gender next to each recognized face

## 🚀 Performance Tips
1. For RTSP Streams:
    - Use tcp transport protocol for stability
    - Example: `rtsp://user:pass@ip:port/stream?tcp`

2. GPU Acceleration:
    ```yaml
    recognition:
        device: "cuda"  # In config.yaml
    ```

3. Optimization:
    - Lower processing intervals for fewer cameras
    - Reduce resolution for distant facial recognition
    - Use JPEG compression for RTSP streams

## 📊 Sample Use Cases
- Office Security: Monitor entrances for unauthorized personnel
- Smart Home: Get alerts when family members arrive
- Retail Analytics: Track customer demographics

## 📜 License
MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing
We welcome contributions! Please see our [Contribution Guidelines](CONTRIBUTING.md)

## ☕ Support the Project
If you find this project helpful, consider buying me a coffee!
[Buy Me a Coffee](https://buymeacoffee.com/aarambhdevhub)
