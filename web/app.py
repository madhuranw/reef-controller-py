"""FastAPI web server — dashboard + REST API."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Reef Controller", version="0.1.0")

TEMPLATES_DIR = Path(__file__).parent / "templates"
if TEMPLATES_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(TEMPLATES_DIR)), name="static")


@app.get("/")
async def dashboard():
    """Serve the main dashboard page."""
    index = TEMPLATES_DIR / "dashboard.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "running", "dashboard": "templates not deployed"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Reef Controller is running"}


@app.get("/api/status")
async def status():
    """System health: CPU temp, uptime, process info."""
    import platform
    import psutil

    cpu_temp = None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            cpu_temp = float(f.read().strip()) / 1000.0
    except Exception:
        pass

    return {
        "platform": platform.node(),
        "cpu_temp_c": cpu_temp,
        "uptime_seconds": psutil.boot_time(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
