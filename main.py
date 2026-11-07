
import cv2
import mediapipe as mp
import math
import time
import winsound
import threading

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "face_landmarker.task"

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.20
CLOSED_EYE_SECONDS = 1.5

# Alarm controls
alarm_active = threading.Event()
shutdown_alarm = threading.Event()


def calculate_ear(landmarks, eye_indices, width, height):
    points = []

    for index in eye_indices:
        x = landmarks[index].x * width
        y = landmarks[index].y * height
        points.append((x, y))

    vertical_1 = math.dist(points[1], points[5])
    vertical_2 = math.dist(points[2], points[4])
    horizontal = math.dist(points[0], points[3])

    if horizontal == 0:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def alarm_worker():
    while not shutdown_alarm.is_set():
        if alarm_active.wait(timeout=0.1):
            if shutdown_alarm.is_set():
                break

            try:
                # Short beep
                winsound.Beep(1000, 350)
            except RuntimeError:
                print("Laptop beep play nahi ho payi.")

            # Pause between beeps
            shutdown_alarm.wait(0.65)


camera = cv2.VideoCapture(0)

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# Start one background alarm worker
alarm_thread = threading.Thread(
    target=alarm_worker,
    daemon=True
)
alarm_thread.start()

print("Eye closure detection ready!")

closed_since = None

start_time = time.monotonic()
last_timestamp_ms = -1

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Webcam se video nahi mil raha!")
            break

        rgb_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )

        timestamp_ms = max(
            timestamp_ms, last_timestamp_ms + 1
        )
        last_timestamp_ms = timestamp_ms

        result = landmarker.detect_for_video(
            mp_image, timestamp_ms
        )

        if result.face_landmarks:
            h, w, _ = frame.shape
            face = result.face_landmarks[0]

            left_ear = calculate_ear(
                face, LEFT_EYE, w, h
            )
            right_ear = calculate_ear(
                face, RIGHT_EYE, w, h
            )

            average_ear = (left_ear + right_ear) / 2.0

            # Green face landmarks
            for point in face:
                x = int(point.x * w)
                y = int(point.y * h)
                cv2.circle(
                    frame, (x, y), 1, (0, 255, 0), -1
                )

            # Red eye landmarks
            for index in LEFT_EYE + RIGHT_EYE:
                x = int(face[index].x * w)
                y = int(face[index].y * h)
                cv2.circle(
                    frame, (x, y), 4, (0, 0, 255), -1
                )

            # Eye closure detection
            if average_ear < EAR_THRESHOLD:
                if closed_since is None:
                    closed_since = time.monotonic()

                closed_duration = (
                    time.monotonic() - closed_since
                )

                if closed_duration >= CLOSED_EYE_SECONDS:
                    status = "DROWSINESS WARNING!"
                    color = (0, 0, 255)

                    # Start repeating alarm
                    alarm_active.set()

                else:
                    status = "Eyes Closed"
                    color = (0, 165, 255)

            else:
                closed_since = None
                closed_duration = 0.0

                # Stop repeating alarm
                alarm_active.clear()

                status = "Eyes Open"
                color = (0, 255, 0)

            cv2.putText(
                frame,
                f"EAR: {average_ear:.3f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
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

            if closed_since is not None:
                cv2.putText(
                    frame,
                    f"Closed: {closed_duration:.1f}s",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

        else:
            closed_since = None

            # Stop alarm if face is not detected
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

        cv2.imshow(
            "Driver Drowsiness Detection", frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    alarm_active.clear()
    shutdown_alarm.set()

    camera.release()
    cv2.destroyAllWindows()
    landmarker.close()

    print("Camera closed safely.")
