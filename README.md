# Reef Tank Controller

Python-based reef tank controller for Raspberry Pi 4.

## Features

- Temperature monitoring via DS18B20 1-Wire sensor
- Automatic fan control (PWM speed modulation)
- Scheduled dosing pump control
- Kasa smart plug integration (heater, refugium light)
- Email + Telegram + buzzer alerts
- SQLite data logging
- Web dashboard with real-time sensor data
- Planned: water level, pH, salinity, camera monitoring

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Validate configuration
python main.py --validate

# Run the controller
python main.py
```

## Configuration

Edit `config.yaml` to customize sensors, actuators, alerts, and schedules.
See [System Architecture](../Projects/Reef%20Controller/System%20Architecture.md) for details.

## Build Phases

1. Config loader + file structure (current)
2. DS18B20 driver + sensor read
3. DHT11 driver + humidity sensor
4. SQLite logger
5. Fan PWM driver
6. Dashboard (static page)
7. Dashboard + live sensor data
8. Temperature control logic
9. Smart plug client (Kasa)
10. Dashboard + smart plug control
11. Dosing pump PWM driver
12. Alert system (email + Telegram)
13. Buzzer + Wi-Fi loss detection
14. HTTPS/TLS setup
15. systemd service + auto-restart
16+. Future: camera, water level, pH, salinity

## Hardware

- Raspberry Pi 4
- DS18B20 waterproof temperature probe (GPIO4, 1-Wire)
- PWM 4-Channel MOSFET board (GPIO18-20)
- 12V DC radial fan
- 12V dosing pumps x2
- Kasa smart plugs
- GPIO HAT (wiring convenience)
- 12V PSU + 5V buck converter

## Project Status

- **Phase:** 1 of 18 (config loader + file structure)
- **Language:** Python 3.13
- **Framework:** FastAPI
- **Platform:** Raspberry Pi 4 (Raspberry Pi OS)

## Repository

https://github.com/madhuranw/reef-controller-py
