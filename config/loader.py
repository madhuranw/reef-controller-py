"""Configuration loader — reads config.yaml and validates values."""

import yaml
from pathlib import Path
from typing import Any, Dict, Tuple, List


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class Config:
    """Loads and validates config.yaml."""

    DEFAULT_PATH = Path(__file__).parent.parent / "config.yaml"

    def __init__(self, path: Path | None = None):
        self._path = path or self.DEFAULT_PATH
        self._data: Dict[str, Any] = {}
        self._errors: List[str] = []

    @property
    def data(self) -> Dict[str, Any]:
        """Return raw config dict."""
        return self._data

    def load(self) -> "Config":
        """Load config from YAML file."""
        if not self._path.exists():
            raise ConfigError(f"Config file not found: {self._path}")
        with open(self._path, "r") as f:
            self._data = yaml.safe_load(f) or {}
        return self

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate all config values. Returns (is_valid, errors)."""
        errors = []

        required_keys = ["sensor", "actuator", "alert", "dashboard", "logging"]
        for key in required_keys:
            if key not in self._data:
                errors.append(f"Missing required section: {key}")

        if "sensor" in self._data:
            errors.extend(self._validate_sensors())
        if "actuator" in self._data:
            errors.extend(self._validate_actuators())

        if "dashboard" in self._data:
            port = self._data["dashboard"].get("port", 8080)
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append(f"dashboard.port must be 1-65535, got {port}")

        self._errors = errors
        return len(errors) == 0, errors

    def _validate_sensors(self) -> List[str]:
        errors = []
        sensors = self._data.get("sensor", {})
        for name, conf in sensors.items():
            if not conf.get("enabled", False):
                continue
            if "pin" not in conf:
                errors.append(f"sensor.{name}: missing pin")
            interval = conf.get("interval_seconds", 0)
            if not isinstance(interval, int) or interval < 1:
                errors.append(f"sensor.{name}: interval_seconds must be >= 1")
        return errors

    def _validate_actuators(self) -> List[str]:
        errors = []
        actuators = self._data.get("actuator", {})
        for name, conf in actuators.items():
            if "pin" not in conf:
                errors.append(f"actuator.{name}: missing pin")
        return errors

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by dotted key path."""
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value if value is not None else default

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire config section."""
        return self._data.get(section, {})

    def __repr__(self) -> str:
        valid, errors = self.validate()
        status = "valid" if valid else f"invalid ({len(errors)} errors)"
        return f"Config(path={self._path}, status={status})"
