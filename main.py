#!/usr/bin/env python3
"""Reef Controller — main entry point.

Usage:
    python main.py              # Start the controller
    python main.py --validate   # Validate config only
    python main.py --version    # Show version
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

VERSION = "0.1.0"


def main():
    parser = argparse.ArgumentParser(description="Reef Tank Controller")
    parser.add_argument("--validate", action="store_true", help="Validate config and exit")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"Reef Controller v{VERSION}")
        return 0

    from config.loader import Config, ConfigError

    config = Config()
    try:
        config.load()
    except ConfigError as e:
        logger.error(f"Config error: {e}")
        return 1

    valid, errors = config.validate()
    if not valid:
        logger.error(f"Config validation failed ({len(errors)} errors):")
        for err in errors:
            logger.error(f"  - {err}")
        return 1

    logger.info(f"Config valid: {config}")

    if args.validate:
        logger.info("Configuration is valid. Exiting.")
        return 0

    logger.info(f"Starting Reef Controller v{VERSION}")
    port = config.get("dashboard.port", 8080)
    logger.info(f"Dashboard will be available at http://<Pi_IP>:{port}")
    logger.info("Control loop not yet implemented — see build phases for next steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
