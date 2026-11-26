"""Base smart plug interface."""

import abc
import logging

logger = logging.getLogger(__name__)


class SmartPlugError(Exception):
    """Raised when a smart plug operation fails."""
    pass


class BaseSmartPlug(abc.ABC):
    """Abstract base for smart plug drivers."""

    def __init__(self, name: str, host: str, alias: str = ""):
        self.name = name
        self.host = host
        self.alias = alias or name
        self._online = False
        self._state = "unknown"

    @property
    def online(self) -> bool:
        return self._online

    @property
    def state(self) -> str:
        return self._state

    @abc.abstractmethod
    def initialize(self) -> bool:
        """Connect to the plug and verify it's reachable."""
        pass

    @abc.abstractmethod
    def get_state(self) -> bool:
        """Get current power state. True = on, False = off."""
        pass

    @abc.abstractmethod
    def set_state(self, on: bool) -> bool:
        """Set the power state."""
        pass

    def turn_on(self) -> bool:
        return self.set_state(True)

    def turn_off(self) -> bool:
        return self.set_state(False)

    def __repr__(self) -> str:
        status = "online" if self._online else "offline"
        return f"SmartPlug({self.alias}, host={self.host}, state={self._state}, status={status})"
