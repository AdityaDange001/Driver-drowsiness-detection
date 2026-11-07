
import cv2
import mediapipe as mp
import math
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "face_landmarker.task"

# Mouth landmarks
UPPER_LIP = 13
LOWER_LIP = 14
LEFT_CORNER = 61
RIGHT_CORNER = 291

YAWN_THRESHOLD = 0.45
YAWN_SECONDS = 1.0


def distance(p1, p2, width, height):
    x1, y1 = p1.x * width, p1.y * height
    x2, y2 = p2.x * width, p2.y * height
    return math.dist((x1, y1), (x2, y2))


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

start_time = time.monotonic()
last_timestamp_ms = -1
yawn_since = None

print("Yawning detection started!")

try:
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

        if result.face_landmarks:
            face = result.face_landmarks[0]

            mouth_open = distance(
                face[UPPER_LIP],
                face[LOWER_LIP], w, h
            )

            mouth_width = distance(
                face[LEFT_CORNER],
                face[RIGHT_CORNER], w, h
            )

            mar = mouth_open / max(mouth_width, 1)

            # Show mouth landmarks
            for index in [
                UPPER_LIP, LOWER_LIP,
                LEFT_CORNER, RIGHT_CORNER
            ]:
                x = int(face[index].x * w)
                y = int(face[index].y * h)
                cv2.circle(
                    frame, (x, y), 5, (255, 0, 255), -1
                )

            if mar > YAWN_THRESHOLD:
                if yawn_since is None:
                    yawn_since = time.monotonic()

                duration = time.monotonic() - yawn_since

                if duration >= YAWN_SECONDS:
                    status = "YAWNING DETECTED!"
                    color = (0, 0, 255)
                else:
                    status = "Mouth Open"
                    color = (0, 165, 255)
            else:
                yawn_since = None
                status = "Normal"
                color = (0, 255, 0)

            cv2.putText(
                frame, f"MAR: {mar:.3f}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 0), 2
            )

        else:
            yawn_since = None

        cv2.putText(
            frame, status,
            (20, 85), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, color, 2
        )

        cv2.imshow("Yawning Detection Test", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    landmarker.close()
    print("Yawning test closed safely.")
