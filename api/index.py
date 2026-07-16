import sys
import os

# Add backend directory to path so it can import app.main
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
