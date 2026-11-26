"""DHT11 humidity + temperature sensor driver.

DHT11 uses a proprietary single-bus protocol with bit-banging on GPIO.
- Humidity range: 20-90% RH
- Temperature range: 0-50°C
- Update rate: 1 sample / 1-2 seconds (slow sensor)
- Accuracy: ±5% RH (hum), ±2°C (temp)

Note: DHT11 is slow — never read more than once per 2 seconds.
This driver enforces a minimum 2s interval between reads.
"""

import logging
import time
from datetime import datetime, timezone

from sensors.base import BaseSensor, SensorError

logger = logging.getLogger(__name__)

# DHT11 timing constants (microseconds)
START_SIGNAL_LOW_MS = 18       # Pi pulls line low for 18ms
RESPONSE_LOW_US = 80           # DHT11 response low
RESPONSE_HIGH_US = 80          # DHT11 response high
BIT_0_LOW_US = 26              # Bit '0' low duration
BIT_0_HIGH_US = 28             # Bit '0' high duration
BIT_1_LOW_US = 26              # Bit '1' low duration
BIT_1_HIGH_US = 70             # Bit '1' high duration
MIN_READ_INTERVAL_S = 2        # Minimum seconds between reads

# DHT11 spec ranges
HUM_MIN = 20.0
HUM_MAX = 90.0
TEMP_MIN = 0.0
TEMP_MAX = 50.0


class Dht11Sensor(BaseSensor):
    """Driver for DHT11 humidity + temperature sensor."""

    def __init__(self, pin: str = "gpio17", location: str = "unknown",
                 use_mock: bool = False):
        super().__init__(name="humidity", pin=pin, enabled=True)
        self.location = location
        self.use_mock = use_mock
        self._device_path = None
        self._last_read_time = 0
        self._humidity = None
        self._temperature = None

    def initialize(self) -> bool:
        """Initialize the sensor.

        For real hardware: imports gpiozero.
        For mock: just sets up and returns True.
        """
        if self.use_mock:
            logger.info(f"DHT11 mock mode (pin={self.pin}, loc={self.location})")
            self._online = True
            return True

        # Try to import gpiozero for bit-banging
        try:
            import gpiozero
            self._device_path = f"/sys/class/gpio/gpio{self._pin_to_number()}"
            logger.info(f"DHT11 initialized: {self.location} on {self.pin}")
            self._online = True
            return True
        except ImportError:
            logger.error("gpiozero not installed. Install with: pip install gpiozero")
            logger.info("DHT11 will operate in mock mode for testing.")
            self.use_mock = True
            self._online = True
            return True

    def _pin_to_number(self) -> int:
        """Convert GPIO name to BCM number."""
        pin_map = {
            "gpio4": 4, "gpio17": 17, "gpio18": 18,
            "gpio19": 19, "gpio20": 20, "gpio21": 21,
            "gpio22": 22, "gpio23": 23, "gpio24": 24,
            "gpio25": 25, "gpio26": 26, "gpio27": 27,
        }
        return pin_map.get(self.pin, 17)

    def read(self) -> dict:
        """Read humidity and temperature from DHT11.

        Returns dict with keys: humidity (float), temperature (float) in C.
        Raises SensorError on read failure.
        """
        # Enforce minimum read interval
        now = time.time()
        if now - self._last_read_time < MIN_READ_INTERVAL_S:
            wait = MIN_READ_INTERVAL_S - (now - self._last_read_time)
            logger.debug(f"DHT11 too soon, waiting {wait:.1f}s")
            time.sleep(wait)

        if self.use_mock:
            return self._read_mock()

        return self._read_real()

    def _read_mock(self) -> dict:
        """Return mock sensor data for testing without hardware."""
        import random
        # Simulate realistic humidity and temperature readings
        humidity = round(random.uniform(40.0, 65.0), 1)
        temperature = round(random.uniform(20.0, 28.0), 1)
        self._humidity = humidity
        self._temperature = temperature
        self._last_read_time = time.time()
        return {"humidity": humidity, "temperature": temperature}

    def _read_real(self) -> dict:
        """Read from real DHT11 hardware using bit-banging."""
        import gpiozero

        pin_num = self._pin_to_number()

        # Step 1: Send start signal (pull LOW for 18ms)
        output = gpiozero.DigitalOutputDevice(pin_num)
        output.off()
        time.sleep(0.018)
        output.on()
        time.sleep(0.000040)  # 40μs

        # Step 2: Switch to input and wait for response
        input_dev = gpiozero.DigitalInputDevice(pin_num, pull_up=False)

        # Wait for DHT11 response (LOW for 80μs, then HIGH for 80μs)
        try:
            input_dev.when_off = None
            input_dev.when_on = None
            # Wait for response high
            if not input_dev.is_active:
                input_dev.wait_for_active(timeout=0.1)
            # Wait for response low
            if input_dev.is_active:
                input_dev.wait_for_inactive(timeout=0.1)
        except Exception as e:
            raise SensorError(f"DHT11 response timeout: {e}")

        # Step 3: Read 40 bits of data
        data = self._read_bits(input_dev)

        if data is None or len(data) != 5:
            raise SensorError("DHT11 returned invalid data length")

        # Step 4: Validate checksum
        humidity_int = data[0]
        humidity_dec = data[1]
        temp_int = data[2]
        temp_dec = data[3]
        checksum = data[4]

        expected_checksum = (humidity_int + humidity_dec + temp_int + temp_dec) & 0xFF
        if checksum != expected_checksum:
            raise SensorError(
                f"DHT11 checksum mismatch: got {checksum}, expected {expected_checksum}"
            )

        # Step 5: Convert to values
        humidity = humidity_int + humidity_dec / 10.0
        temperature = temp_int + temp_dec / 10.0

        self._humidity = humidity
        self._temperature = temperature
        self._last_read_time = time.time()
        input_dev.close()
        output.close()

        # Validate ranges
        if not self.validate_reading(humidity, HUM_MIN, HUM_MAX):
            logger.warning(f"DHT11 humidity {humidity}% out of spec range")
        if not self.validate_reading(temperature, TEMP_MIN, TEMP_MAX):
            logger.warning(f"DHT11 temperature {temperature}C out of spec range")

        return {"humidity": humidity, "temperature": temperature}

    def _read_bits(self, input_dev) -> list | None:
        """Read 40 bits from DHT11 using GPIO bit-banging."""
        data = []

        for i in range(40):
            # Wait for bit start (LOW)
            if not input_dev.is_active:
                try:
                    input_dev.wait_for_active(timeout=0.001)
                except Exception:
                    return None

            # Measure HIGH duration
            start = time.monotonic()
            try:
                input_dev.wait_for_inactive(timeout=0.001)
            except Exception:
                return None
            duration = time.monotonic() - start

            # 28μs = bit 0, 70μs = bit 1 (threshold ~50μs)
            bit = 1 if duration > 0.000050 else 0
            data.append(bit)

        # Convert bits to bytes
        result = []
        for i in range(0, 40, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | data[i + j]
            result.append(byte)

        return result

    def get_humidity(self) -> float | None:
        """Return the last humidity reading."""
        return self._humidity

    def get_temperature(self) -> float | None:
        """Return the last temperature reading from DHT11."""
        return self._temperature

    @property
    def online(self) -> bool:
        return self._online

    def __repr__(self) -> str:
        hum = f"{self._humidity}%" if self._humidity is not None else "--"
        temp = f"{self._temperature}C" if self._temperature is not None else "--"
        mode = "mock" if self.use_mock else "real"
        return f"DHT11(loc={self.location}, hum={hum}, temp={temp}, mode={mode})"
