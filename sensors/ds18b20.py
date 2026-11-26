"""DS18B20 1-Wire temperature sensor driver."""

import logging
import re
from pathlib import Path

from sensors.base import BaseSensor, SensorError

logger = logging.getLogger(__name__)

W1_BASE = Path("/sys/bus/w1/devices")
DEVICE_PATTERN = "28-*"
TEMP_MIN = -55.0
TEMP_MAX = 125.0


class Ds18b20Sensor(BaseSensor):
    """Driver for DS18B20 waterproof temperature probe via 1-Wire."""

    def __init__(self, sensor_id: str = None, location: str = "unknown"):
        super().__init__(name="temperature", pin="gpio4", enabled=True)
        self.sensor_id = sensor_id
        self.location = location
        self._device_path = None

    def initialize(self) -> bool:
        """Find the DS18B20 sensor on the 1-Wire bus."""
        devices = sorted(W1_BASE.glob(DEVICE_PATTERN))
        if not devices:
            logger.error("No 1-Wire devices found. Check dtoverlay=w1-gpio in /boot/config.txt")
            self._online = False
            return False

        if self.sensor_id:
            for d in devices:
                if d.name == self.sensor_id:
                    self._device_path = d / "w1_slave"
                    self.name = f"temperature_{self.location}"
                    self._online = True
                    logger.info(f"Found DS18B20: {self.sensor_id} at {self.location}")
                    return True
            logger.warning(f"Sensor {self.sensor_id} not found. Available: {[d.name for d in devices]}")
            self._online = False
            return False
        else:
            self._device_path = devices[0] / "w1_slave"
            self.sensor_id = devices[0].name
            self.name = f"temperature_{self.location}"
            self._online = True
            logger.info(f"Using first DS18B20: {self.sensor_id}")
            return True

    def read(self) -> float:
        """Read temperature from the sensor. Returns Celsius."""
        if not self._device_path or not self._device_path.exists():
            raise SensorError(f"Device path not found: {self._device_path}")

        raw = self._device_path.read_text().strip()
        first_line = raw.split("\n")[0]
        if "YES" not in first_line:
            raise SensorError(f"CRC check failed: {first_line}")

        match = re.search(r"t=(\-?\d+)", raw)
        if not match:
            raise SensorError(f"Could not parse temperature: {raw}")

        temp_raw = int(match.group(1))
        temperature = temp_raw / 1000.0

        if not self.validate_reading(temperature, TEMP_MIN, TEMP_MAX):
            logger.warning(f"Out-of-range temp: {temperature}C from {self.sensor_id}")

        return temperature

    def get_id(self) -> str:
        """Return the sensor's 64-bit ID."""
        return self.sensor_id or "unknown"

    def __repr__(self) -> str:
        return f"DS18B20(id={self.sensor_id}, loc={self.location}, temp={self._last_value})"
