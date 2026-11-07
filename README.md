
# Driver Drowsiness Detection System

## 1. Project Overview

The Driver Drowsiness Detection System is a computer-vision-based project designed to detect signs of driver drowsiness and yawning using a webcam.

When signs of drowsiness are detected, the system activates an audible warning. It also records detected events in an SQLite database and displays the information on a web dashboard.

This is a student prototype intended for learning and demonstration.

## 2. Project Objectives

- Detect eye closure using facial landmarks.
- Identify possible drowsiness.
- Detect yawning using facial features.
- Generate an audible warning.
- Store detected events and timestamps in a database.
- Display event counts and history on a web dashboard.
- Prepare the software for future ESP32 and external buzzer integration.

## 3. Technologies Used

- Python
- OpenCV
- MediaPipe Tasks
- NumPy
- Flask
- SQLite
- HTML and CSS
- JSON
- ESP32 (planned hardware integration)

## 4. Main Features

### Eye Closure Detection
Uses facial landmarks to monitor eye closure and identify possible drowsiness.

### Alarm System
Generates an audible warning when the configured drowsiness condition is met.

### Yawning Detection
Uses facial landmarks to estimate mouth opening and detect possible yawning.

### Event Logging
Stores drowsiness warnings and yawning events in an SQLite database.

### Web Dashboard
Displays the current detection status, event counts, and recent event history.

### Live Status
Uses a JSON file to share detection status between the detection program and dashboard.

## 5. Project Files

- `main.py` — standalone eye-closure detection.
- `yawn_test.py` — yawning detection test.
- `database_test.py` — database functionality test.
- `integrated_system.py` — integrated webcam detection, alarm, and event logging.
- `app.py` — Flask web dashboard.
- `face_landmarker.task` — MediaPipe face-landmarker model.
- `drowsiness.db` — SQLite database.
- `system_status.json` — latest detection status, when generated.
- `README.md` — project documentation.

## 6. Requirements

Install Python and ensure that the webcam is available.

Install the required packages using:

```bash
py -m pip install opencv-python mediapipe numpy flask requests
```

## 7. How to Run

Open the project folder in VS Code.

### Terminal 1: Start Detection

```bash
py integrated_system.py
```

Allow webcam access if prompted.

### Terminal 2: Start the Dashboard

Open a second terminal and run:

```bash
py app.py
```

Open this address in your browser:

http://127.0.0.1:5000

Keep both terminals running while using the system.

To stop either program, select its terminal and press `Ctrl + C`.

## 8. Database

The SQLite database stores detected events, including event type and timestamp.

The dashboard displays the total number of drowsiness warnings, yawning events, total recorded events, and recent event history.

## 9. Future Enhancements

- Integrate an ESP32 with an external buzzer.
- Improve detection accuracy under different lighting conditions.
- Add configurable warning thresholds.
- Improve error handling and testing.
- Add exportable event reports.
- Evaluate performance under controlled test conditions.

## 10. Safety Disclaimer

This project is an educational prototype. It has not been validated as a safety-critical driver-monitoring system and must not be relied upon while driving.

## 11. Project Status

Core software features have been implemented. Final testing, hardware integration, and validation remain pending.
