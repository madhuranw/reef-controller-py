"""Base sensor class — all sensors inherit from this."""

import abc
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SensorError(Exception):
    """Raised when a sensor operation fails."""
    pass


class BaseSensor(abc.ABC):
    """Abstract base for all sensor drivers."""

    def __init__(self, name: str, pin: str, enabled: bool = True):
        self.name = name
        self.pin = pin
        self.enabled = enabled
        self._online = False
        self._last_value = None
        self._last_read = None
        self._read_count = 0
        self._error_count = 0

    @property
    def online(self) -> bool:
        return self._online

    @property
    def last_value(self):
        return self._last_value

    @property
    def last_read(self):
        return self._last_read

    @abc.abstractmethod
    def initialize(self) -> bool:
        """Initialize the sensor. Returns True if successful."""
        pass

    @abc.abstractmethod
    def read(self) -> float:
        """Read the sensor value. Returns temp (C), humidity (%), etc."""
        pass

    def read_with_retry(self, retries: int = 3, delay: float = 1.0) -> float | None:
        """Read the sensor with retry logic. Returns value or None."""
        for attempt in range(retries):
            try:
                value = self.read()
                self._last_value = value
                self._last_read = datetime.now(timezone.utc)
                self._read_count += 1
                self._error_count = 0
                self._online = True
                return value
            except SensorError as e:
                self._error_count += 1
                logger.warning(f"Sensor {self.name} attempt {attempt+1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(delay)
        self._online = False
        logger.error(f"Sensor {self.name} failed after {retries} retries")
        return None

    def validate_reading(self, value: float, range_min: float = None,
                         range_max: float = None) -> bool:
        """Check if a reading is within expected range."""
        if range_min is not None and value < range_min:
            logger.warning(f"Sensor {self.name}: value {value} below min {range_min}")
            return False
        if range_max is not None and value > range_max:
            logger.warning(f"Sensor {self.name}: value {value} above max {range_max}")
            return False
        return True

    def __repr__(self) -> str:
        status = "online" if self._online else "offline"
        return f"Sensor({self.name}, pin={self.pin}, status={status}, errors={self._error_count})"
