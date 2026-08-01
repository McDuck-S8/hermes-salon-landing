"""Launcher template for local API server integration.

Copy this to your project, adjust the app factory and env vars.

Pattern:
1. Set PYTHONPATH via sys.path.insert so imports work
2. Set env vars BEFORE importing the app (os.environ.setdefault)
3. Create the app instance with create_app()
4. Run with uvicorn via .venv python
"""

import os
import sys

# 1. Add project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 2. Enable features via env vars BEFORE app import
os.environ.setdefault("ENV", "DEV")  # Enable Swagger docs
# os.environ.setdefault("LOG_LEVEL", "DEBUG")

# 3. Import and create the app
import uvicorn
from everos.entrypoints.api.app import create_app

app = create_app()
print(f"App created, routes: {[r.path for r in app.routes]}", flush=True)

# 4. Run with uvicorn
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8111,
    factory=False,
    log_level="info",
)
