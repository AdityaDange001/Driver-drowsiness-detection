
import serial
import time

ESP32_PORT = None  # Hardware connect hone par COM port set karenge
BAUD_RATE = 115200

esp32 = None
last_buzzer_state = None


def connect_esp32():
    global esp32, last_buzzer_state

    if ESP32_PORT is None:
        print("ESP32 not configured yet. Hardware pending.")
        return False

    try:
        esp32 = serial.Serial(
            ESP32_PORT,
            BAUD_RATE,
            timeout=1,
            write_timeout=1
        )
        time.sleep(2)
        last_buzzer_state = None
        print("ESP32 connected:", ESP32_PORT)
        return True

    except (serial.SerialException, OSError) as error:
        esp32 = None
        print("ESP32 connection unavailable:", error)
        return False


def set_buzzer(state):
    global last_buzzer_state

    if esp32 is None or not esp32.is_open:
        return

    state = bool(state)

    # Same command repeatedly send nahi karna
    if state == last_buzzer_state:
        return

    command = "ON\n" if state else "OFF\n"

    try:
        esp32.write(command.encode("utf-8"))
        last_buzzer_state = state
    except (serial.SerialException, OSError) as error:
        print("Buzzer command failed:", error)
        last_buzzer_state = None


def disconnect_esp32():
    global esp32, last_buzzer_state

    if esp32 is not None:
        try:
            if esp32.is_open:
                esp32.write(b"OFF\n")
                esp32.close()
        except (serial.SerialException, OSError):
            pass

    esp32 = None
    last_buzzer_state = None


if __name__ == "__main__":
    connect_esp32()
    disconnect_esp32()
