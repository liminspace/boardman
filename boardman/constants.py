DEVICES = {
    "Raspberry Pi Pico": [
        {"hwid": "VID:PID=2E8A:0005", "manufacturer": "MicroPython"},
    ],
    "ESP32": [
        {"hwid": "VID:PID=1A86:55D4", "manufacturer": None},
        {"hwid": "VID:PID=1A86:7523", "manufacturer": None},
    ],
}

MICROPYTHON_URL_TPL = "https://github.com/micropython/micropython/archive/refs/tags/v{ver}.zip"
