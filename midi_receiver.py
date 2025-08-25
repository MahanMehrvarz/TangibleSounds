# Motion MIDI Controller - Receiver
# For Adafruit ItsyBitsy connected to computer via USB

import time
import board
import json
import usb_midi
from MQTT import Create_MQTT
from settings import settings

# Try to import MIDI libraries in different ways
try:
    # Method 1: Using the newer adafruit_midi library
    import adafruit_midi
    from adafruit_midi.control_change import ControlChange

    # Initialize MIDI
    midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

    # Function to send MIDI CC
    def send_midi_cc(cc_number, value):
        midi.send(ControlChange(cc_number, value))

    print("Using adafruit_midi library")

except ImportError:
    try:
        # Method 2: Alternative approach with direct USB MIDI
        def send_midi_cc(cc_number, value):
            # Format for Control Change: 0xB0 (status byte) + channel, control number, value
            usb_midi.ports[1].write(bytes([0xB0, cc_number, value]))

        print("Using direct USB MIDI")

    except Exception as e:
        print(f"MIDI setup failed: {e}")

        # Method 3: Fall back to just printing (for debugging)
        def send_midi_cc(cc_number, value):
            print(f"Would send MIDI CC {cc_number}: {value}")

        print("Using debug MIDI (not sending actual MIDI)")

##--- MIDI CC numbers for X, Y, Z axes
X_CC = 20
Y_CC = 21
Z_CC = 22

##--- Last values for debouncing
last_x = 0
last_y = 0
last_z = 0
# Threshold for sending new MIDI CC (to reduce MIDI traffic)
MIDI_THRESHOLD = 2

##--- MQTT message handler
def handle_message(client, topic, message):
    global last_x, last_y, last_z

    try:
        # Parse JSON data
        data = json.loads(message)

        # Extract X, Y, Z values
        x = data.get("x", 0)
        y = data.get("y", 0)
        z = data.get("z", 0)

        print(f"Received: X={x}, Y={y}, Z={z}")

        # Only send MIDI if value has changed significantly
        if abs(x - last_x) >= MIDI_THRESHOLD:
            send_midi_cc(X_CC, x)
            last_x = x
            print(f"Sent MIDI CC {X_CC}: {x}")

        if abs(y - last_y) >= MIDI_THRESHOLD:
            send_midi_cc(Y_CC, y)
            last_y = y
            print(f"Sent MIDI CC {Y_CC}: {y}")

        if abs(z - last_z) >= MIDI_THRESHOLD:
            send_midi_cc(Z_CC, z)
            last_z = z
            print(f"Sent MIDI CC {Z_CC}: {z}")

    except Exception as e:
        print(f"Error processing message: {e}")

##--- MQTT configuration
client_id = settings["mqtt_clientid"] + "_receiver"
mqtt_client = Create_MQTT(client_id, handle_message)
mqtt_topic = "motion/data"
mqtt_client.subscribe(mqtt_topic)

print("Receiver initialized - waiting for MQTT messages...")

##--- Main loop
while True:
    try:
        # Check for new MQTT messages
        mqtt_client.loop(0.1)

    except (ValueError, RuntimeError) as e:
        print(f"Failed to get data, retrying\n", e)
        mqtt_client.reconnect()
        mqtt_client.subscribe(mqtt_topic)
