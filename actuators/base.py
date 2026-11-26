"""Base actuator class — all actuators inherit from this."""

import abc
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ActuatorError(Exception):
    """Raised when an actuator operation fails."""
    pass


class BaseActuator(abc.ABC):
    """Abstract base for all actuator drivers."""

    def __init__(self, name: str, pin: str, enabled: bool = True):
        self.name = name
        self.pin = pin
        self.enabled = enabled
        self._online = False
        self._state = "off"
        self._last_change = None

    @property
    def online(self) -> bool:
        return self._online

    @property
    def state(self):
        return self._state

    @abc.abstractmethod
    def initialize(self) -> bool:
        """Initialize the actuator. Returns True if successful."""
        pass

    @abc.abstractmethod
    def set(self, value) -> bool:
        """Set the actuator to a value."""
        pass

    def turn_on(self) -> bool:
        """Turn the actuator on."""
        return self.set("on")

    def turn_off(self) -> bool:
        """Turn the actuator off."""
        return self.set("off")

    def pulse(self, duration_seconds: float) -> bool:
        """Pulse the actuator on for a duration, then off."""
        if not self.turn_on():
            return False
        import time
        time.sleep(duration_seconds)
        return self.turn_off()

    def __repr__(self) -> str:
        status = "online" if self._online else "offline"
        return f"Actuator({self.name}, pin={self.pin}, state={self._state}, status={status})"
