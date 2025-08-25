# Haptics to Ableton

CircuitPython projects for turning body movement into real‑time sound control in Ableton Live. The system uses a wearable motion sensor (Seeed XIAO S3 + BMI088) that streams orientation values over MQTT, and a receiver board (Adafruit ItsyBitsy M4) that converts those values into MIDI Control Change messages.

---

## Repository Layout

```
TangibleSounds/
├── embeded_controller.py    # XIAO S3 + BMI088 → MQTT (on‑device code)
├── midi_receiver.py         # ItsyBitsy M4 → USB‑MIDI (receiver code)
└── README.md
```

---

## File Descriptions

### `embeded_controller.py`

**Device:** Seeed XIAO S3 with BMI088 IMU
**Role:** Wearable orientation tracker and wireless publisher
**Description:** Initializes the BMI088 accelerometer and gyroscope, fuses their data with a complementary filter, and computes orientation (pitch, roll, yaw). Connects to Wi‑Fi, authenticates with an MQTT broker, and publishes orientation updates as JSON on the topic `orientation`. Sends only when values change beyond a threshold to reduce jitter and save bandwidth.

---

### `midi_receiver.py`

**Device:** Adafruit ItsyBitsy M4 (CircuitPython, USB‑MIDI capable)
**Role:** MQTT receiver and MIDI bridge
**Description:** Subscribes to the MQTT `orientation` topic, parses incoming JSON (pitch/roll/yaw), scales values to the MIDI CC range (0–127), and outputs them as Control Change messages:

* **CC 20 → Pitch**
* **CC 21 → Roll**
* **CC 22 → Yaw**

The ItsyBitsy enumerates as a USB‑MIDI device and can be mapped directly inside Ableton Live.

---

## Quick Start

### 1. Wearable (XIAO S3)

* Copy `embeded_controller.py` to the XIAO S3 as `code.py`.
* Add Wi‑Fi and MQTT settings in a `settings.toml` on the CIRCUITPY drive:

```toml
CIRCUITPY_WIFI_SSID="your-ssid"
CIRCUITPY_WIFI_PASSWORD="your-password"
BROKER="mqtt-broker.local"
MQTT_CLIENT_ID="your-mqtt-username"
MQTT_PASSWORD="your-mqtt-password"
DEVICE_ID="xiao-s3-01"
```

* After reboot, the device publishes JSON like:

```json
{"pitch": 10.2, "roll": -5.3, "yaw": 42.7}
```

to the MQTT topic `orientation`.

---

### 2. Receiver (ItsyBitsy M4)

* Copy `midi_receiver.py` to the ItsyBitsy M4 as `code.py`.
* Add MQTT credentials if needed in `settings.toml`.
* Connect the board to your computer via USB. It enumerates as a MIDI device and streams CC 20/21/22.

---

### 3. Ableton Live

* Open **Preferences → Link/MIDI**, enable the ItsyBitsy MIDI port for **Track** and **Remote**.
* Click **MIDI Map**, select an effect parameter, then move the wearable — Ableton will learn the CC (20, 21, or 22).
* Exit mapping mode. Moving your body now modulates the assigned effect parameter.
* Record MIDI automation if you want movement to be captured in your project.

---

## Next Steps

* **Test the flow:** Use a MIDI monitor app to confirm CC messages are arriving.
* **Experiment with mappings:** Try CC 20 → Filter Cutoff, CC 21 → Reverb Mix, CC 22 → Delay Feedback.
* **Tune sensitivity:** Adjust thresholds and scaling factors in the code to smooth or exaggerate motion response.
* **Extend the system:**

  * Add new gestures/sensors to `embeded_controller.py`.
  * Map more MQTT topics to additional CCs in `midi_receiver.py`.
  * Run multiple wearables, each with a unique `DEVICE_ID`.

---

## License

