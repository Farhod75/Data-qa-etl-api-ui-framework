import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3307)),   # keep your actual port
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "080675"),
}

# API base URL for tests to call FastAPI
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")