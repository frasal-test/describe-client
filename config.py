import os
from pathlib import Path

# Base directory
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Temporary directory for storing images
TEMP_DIR = BASE_DIR / "temp"

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['file', 'console']
}

# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 3000