# Driver Drowsiness Detection System

A real-time driver drowsiness detection prototype built using Python, OpenCV, MediaPipe, and Flask. The system monitors facial landmarks to detect prolonged eye closure and possible yawning, generates audible warnings, logs events, and displays detection information on a web dashboard.

> **Project type:** Student project / Educational prototype  
> **Status:** Core software implemented; hardware integration and further validation pending.

## Overview

Driver drowsiness can reduce attention and reaction time. This project explores a computer-vision-based approach to identifying possible signs of drowsiness through a webcam.

The system analyzes facial landmarks, checks eye closure and mouth opening, generates warnings when configured conditions are met, and records detected events in an SQLite database.

## Features

- **Eye Closure Detection:** Uses MediaPipe facial landmarks to monitor eye closure.
- **Drowsiness Warning:** Activates an audible alarm when the configured detection condition is met.
- **Yawning Detection:** Estimates mouth opening using facial landmarks to identify possible yawning.
- **Event Logging:** Stores detection events and timestamps in SQLite.
- **Web Dashboard:** Displays event counts, current detection status, and recent event history.
- **Live Status Updates:** Shares detection status with the dashboard through a JSON file.
- **Modular Design:** Separates detection, event logging, and dashboard functionality.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| OpenCV | Webcam access and image processing |
| MediaPipe Tasks | Facial landmark detection |
| NumPy | Numerical calculations |
| Flask | Web dashboard |
| SQLite | Event storage |
| HTML and CSS | Dashboard interface |
| JSON | Detection status communication |

## Project Structure

```text
DriverDrowsinessProject/
├── main.py
├── integrated_system.py
├── app.py
├── esp32_bridge.py
├── database_test.py
├── yawn_test.py
├── check_db.py
├── face_landmarker.task
├── requirements.txt
├── README.md
├── drowsiness.db
└── system_status.json
```

**Important:** The SQLite database and generated status file are created or updated locally when the application runs. They are excluded from version control.

## Getting Started

### Prerequisites

- Windows PC or laptop
- Python installed and accessible using the `py` command
- A working webcam
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/AdityaDange001/Driver-drowsiness-detection.git
cd Driver-drowsiness-detection
```

Alternatively, download the repository as a ZIP file from GitHub.

### 2. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

### 3. Start the Detection System

Open a terminal in the project folder and run:

```bash
py integrated_system.py
```

Allow webcam access if prompted.

### 4. Start the Web Dashboard

Open a second terminal in the same project folder and run:

```bash
py app.py
```

Open the dashboard in your browser:

http://127.0.0.1:5000

Keep both terminals running while using the integrated system. To stop a program, press `Ctrl + C` in its terminal.

## How It Works

1. The webcam captures video frames.
2. MediaPipe detects facial landmarks.
3. The application analyzes eye closure and mouth opening.
4. Configured detection conditions determine when a warning or event should be triggered.
5. Events are recorded in the SQLite database.
6. The Flask dashboard displays the available status and event history.

## Database and Monitoring

The SQLite database stores detected event types and timestamps. The dashboard presents event counts and recent history based on the recorded data.

The database and live status file are local application data and are not included in the repository.

## Future Improvements

- Integrate an ESP32 with an external buzzer.
- Improve robustness under different lighting conditions.
- Add configurable detection thresholds.
- Expand testing and error handling.
- Add downloadable event reports.
- Evaluate detection performance under controlled conditions.

## Safety Disclaimer

This project is an educational prototype and has not been validated as a safety-critical driver-monitoring system. Detection may produce false positives or miss signs of drowsiness. **Do not rely on this system as a substitute for adequate rest or safe driving practices.**

## Author

**Aditya Dange**

GitHub: [@AdityaDange001](https://github.com/AdityaDange001)

## License

No license has been added yet. Unless a license is selected, others do not automatically receive permission to reuse or redistribute the project's code.
