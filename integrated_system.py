
import cv2
import mediapipe as mp
import math
import time
import sqlite3
import winsound
import threading
import esp32_bridge
from datetime import datetime
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "face_landmarker.task"
DATABASE_PATH = "drowsiness.db"
STATUS_PATH = "system_status.json"

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

UPPER_LIP = 13
LOWER_LIP = 14
LEFT_CORNER = 61
RIGHT_CORNER = 291

EAR_THRESHOLD = 0.20
CLOSED_EYE_SECONDS = 1.5

MAR_THRESHOLD = 0.45
YAWN_SECONDS = 1.0

alarm_active = threading.Event()
shutdown_alarm = threading.Event()


def distance(p1, p2, width, height):
    return math.dist(
        (p1.x * width, p1.y * height),
        (p2.x * width, p2.y * height)
    )


def calculate_ear(landmarks, eye_indices, width, height):
    points = [
        (
            landmarks[i].x * width,
            landmarks[i].y * height
        )
        for i in eye_indices
    ]

    vertical_1 = math.dist(points[1], points[5])
    vertical_2 = math.dist(points[2], points[4])
    horizontal = math.dist(points[0], points[3])

    if horizontal == 0:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


import json

def update_live_status(status):
    data = {
        "status": status,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(STATUS_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file)

def save_event(cursor, connection, event_type):
    event_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        "INSERT INTO events (event_type, event_time) VALUES (?, ?)",
        (event_type, event_time)
    )
    connection.commit()

    print(f"[EVENT] {event_type} - {event_time}")


def alarm_worker():
    while not shutdown_alarm.is_set():
        if alarm_active.wait(timeout=0.1):
            if shutdown_alarm.is_set():
                break

            try:
                winsound.Beep(1000, 350)
            except RuntimeError:
                print("Laptop beep play nahi ho payi.")

            shutdown_alarm.wait(0.65)


# Prepare database
connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_time TEXT NOT NULL
)
""")
connection.commit()

camera = None
landmarker = None
alarm_thread = None

try:
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Webcam open nahi ho raha!")

    base_options = python.BaseOptions(
        model_asset_path=MODEL_PATH
    )

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1
    )

    landmarker = vision.FaceLandmarker.create_from_options(
        options
    )

    alarm_thread = threading.Thread(
        target=alarm_worker,
        daemon=True
    )
    alarm_thread.start()

    print("Integrated system started!")

    closed_since = None
    yawn_since = None

    eye_warning_logged = False
    yawn_logged = False

    start_time = time.monotonic()
    last_timestamp_ms = -1

    while True:
        success, frame = camera.read()

        if not success:
            print("Webcam video nahi mil raha!")
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )
        timestamp_ms = max(
            timestamp_ms, last_timestamp_ms + 1
        )
        last_timestamp_ms = timestamp_ms

        result = landmarker.detect_for_video(
            image, timestamp_ms
        )

        status = "No Face Detected"
        color = (0, 0, 255)
        current_time = time.monotonic()

        if result.face_landmarks:
            face = result.face_landmarks[0]

            # Draw face landmarks
            for point in face:
                cv2.circle(
                    frame,
                    (int(point.x * w), int(point.y * h)),
                    1,
                    (0, 255, 0),
                    -1
                )

            # Eye closure detection
            left_ear = calculate_ear(
                face, LEFT_EYE, w, h
            )
            right_ear = calculate_ear(
                face, RIGHT_EYE, w, h
            )
            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                if closed_since is None:
                    closed_since = current_time

                closed_duration = current_time - closed_since

                if closed_duration >= CLOSED_EYE_SECONDS:
                    status = "DROWSINESS WARNING!"
                    color = (0, 0, 255)
                    alarm_active.set()

                    if not eye_warning_logged:
                        save_event(
                            cursor,
                            connection,
                            "Drowsiness Warning"
                        )
                        eye_warning_logged = True
                else:
                    status = "Eyes Closed"
                    color = (0, 165, 255)

            else:
                closed_since = None
                eye_warning_logged = False
                alarm_active.clear()
                closed_duration = 0.0

                status = "Eyes Open"
                color = (0, 255, 0)

            # Yawning detection
            mouth_open = distance(
                face[UPPER_LIP],
                face[LOWER_LIP],
                w,
                h
            )

            mouth_width = distance(
                face[LEFT_CORNER],
                face[RIGHT_CORNER],
                w,
                h
            )

            mar = mouth_open / max(mouth_width, 1)

            if mar > MAR_THRESHOLD:
                if yawn_since is None:
                    yawn_since = current_time

                yawn_duration = current_time - yawn_since

                if yawn_duration >= YAWN_SECONDS:
                    if not yawn_logged:
                        save_event(
                            cursor,
                            connection,
                            "Yawning Detected"
                        )
                        yawn_logged = True
            else:
                yawn_since = None
                yawn_logged = False

            # Display values
            cv2.putText(
                frame,
                f"EAR: {ear:.3f}  MAR: {mar:.3f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                status,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            if yawn_since is not None:
                cv2.putText(
                    frame,
                    f"Mouth open: {current_time - yawn_since:.1f}s",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 255),
                    2
                )

        else:
            closed_since = None
            yawn_since = None
            eye_warning_logged = False
            yawn_logged = False
            alarm_active.clear()

            cv2.putText(
                frame,
                "No Face Detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )
        update_live_status(status)
        cv2.imshow("Driver Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    alarm_active.clear()
    esp32_bridge.set_buzzer(False)
    shutdown_alarm.set()

    if alarm_thread is not None:
        alarm_thread.join(timeout=1.5)

    if camera is not None:
        camera.release()

    cv2.destroyAllWindows()

    if landmarker is not None:
        landmarker.close()
    esp32_bridge.disconnect_esp32()
    connection.close()

    print("System stopped. Database saved safely.")
