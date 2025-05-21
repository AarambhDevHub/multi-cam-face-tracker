# Contribution Guidelines for Multi-Camera Face Tracker

Thank you for considering contributing to our project! This document outlines the process for contributing to the Multi-Camera Face Tracker system.

## 🏁 Getting Started

### Prerequisites
- Python 3.8+ installed
- Git version control
- Basic understanding of:
  - Computer Vision (OpenCV)
  - Face Recognition (InsightFace)
  - GUI Development (PyQt5)

### Development Environment Setup

1. **Fork the Repository**
   ```bash
   git clone https://github.com/AarambhDevHub/multi-cam-face-tracker.git
   cd multi-cam-face-tracker
   ```

2. **Set Up Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/MacOS
    .venv\Scripts\activate    # Windows
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    pre-commit install
    ```

4. **Branch Naming Convention**
    ```
    feature/[short-description]  # For new features
    bugfix/[issue-number]       # For bug fixes
    docs/[topic]               # For documentation
    ```

## 🛠 Development Workflow
Code Structure Overview
```
├── core/          # Business logic
│   ├── face_detection.py
│   ├── camera_manager.py
│   └── ...
├── ui/            # User interface
├── config/        # Configuration files
├── tests/         # Unit and integration tests
└── main.py        # Entry point
```

### Making Changes
1. Create a Feature Branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement Your Changes
    - Follow PEP 8 style guide
    - Include type hints for all functions
    - Add docstrings for public methods

3. Documentation Updates
    - Update relevant docstrings
    - Modify README if introducing new features
    - Add example configs if adding new settings

## 🧑‍💻 Coding Standards
Python Style
 - Follow Google Python Style Guide
 - Maximum line length: 88 characters
 - Use f-strings over .format()

### Type Hints Example
```python
def recognize_faces(
    self, 
    faces: List[Face]
) -> List[Tuple[Face, Optional[KnownFace], float]]:
    """Recognize faces against known database.
    
    Args:
        faces: List of detected Face objects
        
    Returns:
        List of tuples containing:
        - Original face
        - Matched KnownFace (or None)
        - Confidence score
    """
```

### Logging Standards
```python
logger.debug("Processing frame %s", frame_id)  # Detailed debugging
logger.info("Camera %d started", cam_id)      # Important events
logger.warning("Low confidence: %.2f", score) # Potential issues
logger.error("Failed to save screenshot")     # Recoverable errors
logger.critical("DB connection lost")         # Critical failures
```

## 🐛 Issue Reporting
Bug Report Template
```markdown
**Description**
Clear explanation of the bug

**Reproduction Steps**
1. Start the application with...
2. Navigate to...
3. Observe...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g. Windows 10]
- Python Version: [e.g. 3.9.7]
- GPU: [e.g. NVIDIA RTX 3080]

**Screenshots/Logs**
2025-05-20 14:12:08.012 | ERROR | module:line | Error message

**Additional Context**
Any other relevant information
```

## 🌟 Feature Requests
1. Check existing issues for duplicates
2. Use the template
    ```markdown
    **Is your feature request related to a problem?**
    A clear description of what the problem is

    **Describe the solution you'd like**
    Detailed explanation of proposed solution

    **Describe alternatives considered**
    Other approaches you've considered

    **Additional context**
    Any other context or screenshots
    ```
    
## 🏆 Recognition
Great contributions will be:
 - Featured in release notes
 - Added to CONTRIBUTORS.md
 - Eligible for "Contributor of the Month"

We appreciate your contributions! For questions, join our [Discord](https://discord.gg/HDth6PfCnp) community or open a discussion.