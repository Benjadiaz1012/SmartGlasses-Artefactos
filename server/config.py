
import os

from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


API_TOKEN = os.getenv("API_TOKEN", "").strip()

MIN_CONF = float(os.getenv("MIN_CONF", "0.60"))

MAX_IMAGE_SIZE = 10 * 1024 * 1024

MAX_IMAGE_PIXELS = 20_000_000


if not API_TOKEN or API_TOKEN == "replace_with_your_secure_token":
    raise RuntimeError(
        "Debes configurar un API_TOKEN valido en el archivo .env"
    )

if not 0 <= MIN_CONF <= 1:
    raise RuntimeError(
        "MIN_CONF debe estar entre 0 y 1"
    )
