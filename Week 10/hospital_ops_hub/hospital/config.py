"""Paths, model settings and hospital rules shared by every module."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEED_DIR = DATA_DIR / "seed"
STATE_DIR = DATA_DIR / "state"
REQUESTS_DIR = DATA_DIR / "requests"
REPORTS_DIR = PROJECT_ROOT / "reports"


def _load_env():
    """Load the nearest .env walking up from the project folder (the key never lives in code)."""
    for folder in [PROJECT_ROOT, *PROJECT_ROOT.parents]:
        env_file = folder / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return env_file
    return None


ENV_FILE = _load_env()
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Hospital rules
SHIFT_END_BUFFER_MIN = 30   # no doctor whose shift ends within 30 min (except ER cases)
MAX_DOCTOR_LOAD = 3         # a doctor becomes busy at this many patients
DEFAULT_SIM_CLOCK = "2026-10-02T08:00"

PRIORITY_RANK = {"emergency": 0, "urgent": 1, "routine": 2}
RESOURCE_ORDER = {"patient": 0, "bed": 1, "doctor": 2, "staff": 3}
