"""Elevator AI — Root Entrypoint.

Delegates directly to backend.app.main so Railway or Uvicorn running from root or backend
always executes the exact same FastAPI application and CORS configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent / "backend"
if backend_path.exists() and str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app  # noqa: F401

__all__ = ["app"]
