#!/usr/bin/env python3
"""Create all reef-controller-py project files on the Pi."""
import os
from pathlib import Path

BASE = Path.home() / "reef-controller-py"

for d in [
    BASE / "config",
    BASE / "sensors",
    BASE / "actuators" / "smart_plug",
    BASE / "core",
    BASE / "alerts",
    BASE / "logging",
    BASE / "camera",
    BASE / "web" / "routes",
    BASE / "web" / "templates",
    BASE / "data",
]:
    d.mkdir(parents=True, exist_ok=True)

def w(path, content):
    path.write_text(content)

# __init__.py files
for pkg in ["config", "sensors", "actuators", "actuators/smart_plug",
            "core", "alerts", "logging", "camera", "web", "web/routes"]:
    w(BASE / pkg / "__init__.py", f'"""{pkg} package."""\n')

w(BASE / "config/__init__.py", '"""Configuration package."""\nfrom config.loader import Config\n')
w(BASE / "sensors/__init__.py", '"""Sensors package."""\nfrom sensors.base import BaseSensor, SensorError\n')
w(BASE / "actuators/__init__.py", '"""Actuators package."""\nfrom actuators.base import BaseActuator, ActuatorError\n')
w(BASE / "actuators/smart_plug/__init__.py", '"""Smart plug package."""\nfrom actuators.smart_plug.base import BaseSmartPlug, SmartPlugError\n')

# .gitignore
w(BASE / ".gitignore", """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg

# Virtual env
venv/
.env

# Data
data/
*.db
*.log

# Config (contains secrets)
config.yaml

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
""")
