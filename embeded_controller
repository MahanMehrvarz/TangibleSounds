import time
import math
import json
import board
import wifi
import socketpool
import ssl
import adafruit_requests
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import bmi088
import os

# === Sensor Setup ===
i2c = board.I2C()
sensor = bmi088.BMI088(i2c)

sensor.set_acc_scale_range(bmi088.ACC_RANGE_3G)
sensor.set_gyro_scale_range(bmi088.GYRO_RANGE_500)
sensor.set_acc_output_data_rate(bmi088.ACC_ODR_200)
sensor.set_gyro_output_data_rate(bmi088.GYRO_ODR_400_BW_47)

# === WiFi Setup ===
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

print(f"Connecting to WiFi: {ssid}")
wifi.radio.connect(ssid, password)
print("Connected to WiFi!")

# === MQTT Setup ===
broker = os.getenv("BROKER")
mqtt_client_id = os.getenv("MQTT_CLIENT_ID")
mqtt_password = os.getenv("MQTT_PASSWORD")
device_id = os.getenv("DEVICE_ID")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

mqtt_client = MQTT.MQTT(
    broker=broker,
    client_id=device_id,
    username=mqtt_client_id,
    password=mqtt_password,
    socket_pool=pool,
)

def connected(client, userdata, flags, rc):
    print("MQTT connected")

def disconnected(client, userdata, rc):
    print("MQTT disconnected")

def message(client, topic, msg):
    print(f"Message on {topic}: {msg}")

mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

print("Connecting to MQTT broker...")
mqtt_client.connect()

# === Orientation Tracking ===
topic = "orientation"
pitch, roll, yaw = 0.0, 0.0, 0.0
last_time = time.monotonic()
THRESHOLD = 2.0
prev_pitch, prev_roll, prev_yaw = None, None, None

print("Starting orientation loop...")

while True:
    try:
        current_time = time.monotonic()
        dt = current_time - last_time
        last_time = current_time

        if dt > 0.5:
            time.sleep(0.02)
            continue

        accel_x, accel_y, accel_z = sensor.get_acceleration()
        gyro_x, gyro_y, gyro_z = sensor.get_gyroscope()

        # Accelerometer-based pitch and roll
        pitch_acc = math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))
        roll_acc = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

        # Gyro integration
        pitch += gyro_x * dt
        roll += gyro_y * dt
        yaw += gyro_z * dt

        # Complementary filter
        alpha = 0.98
        pitch = alpha * pitch + (1 - alpha) * pitch_acc
        roll = alpha * roll + (1 - alpha) * roll_acc

        # Clamp pitch/roll
        pitch = max(-90, min(90, pitch))
        roll = max(-90, min(90, roll))

        # Normalize yaw
        while yaw > 180:
            yaw -= 360
        while yaw < -180:
            yaw += 360

        # Send only if changed significantly
        send_update = False
        if prev_pitch is None or prev_roll is None or prev_yaw is None:
            send_update = True
        elif (abs(pitch - prev_pitch) >= THRESHOLD or
              abs(roll - prev_roll) >= THRESHOLD or
              abs(yaw - prev_yaw) >= THRESHOLD):
            send_update = True

        if send_update:
            orientation_data = {
                "pitch": round(pitch, 2),
                "roll": round(roll, 2),
                "yaw": round(yaw, 2)
            }
            mqtt_client.publish(topic, json.dumps(orientation_data))
            print("Published:", orientation_data)

            prev_pitch, prev_roll, prev_yaw = pitch, roll, yaw

        time.sleep(0.02)

    except Exception as e:
        print("Error:", e)
        time.sleep(0.1)
