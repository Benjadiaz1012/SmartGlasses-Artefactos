
import os
import sys
import base64
import argparse
import subprocess
import tempfile
import time
import binascii

from pathlib import Path

import requests
import numpy as np

from PIL import Image, ImageOps
from dotenv import load_dotenv


# ==============================
# CONFIGURACION
# ==============================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

SERVER_URL = os.getenv(
    "GLASSES_SERVER", ""
).rstrip("/")

API_TOKEN = os.getenv("GLASSES_TOKEN", "")

TIMEOUT = float(
    os.getenv("GLASSES_TIMEOUT", "60")
)

BLUR_MIN = float(
    os.getenv("BLUR_MIN", "20")
)


# ==============================
# REPRODUCCION DE AUDIO
# ==============================

def play_audio(audio: bytes):

    with tempfile.TemporaryDirectory() as folder:

        audio_path = Path(folder) / "audio.wav"

        audio_path.write_bytes(audio)

        subprocess.run(
            ["paplay", str(audio_path)],
            check=True,
            timeout=180
        )


def speak_local(text: str):

    with tempfile.TemporaryDirectory() as folder:

        audio_path = Path(folder) / "local.wav"

        subprocess.run(
            [
                "espeak-ng",
                "-v", "es",
                "-s", "145",
                "-w", str(audio_path),
                text
            ],
            check=True,
            timeout=30
        )

        play_audio(audio_path.read_bytes())


# ==============================
# CAPTURA DE FOTOGRAFIAS
# ==============================

def capture(image_path: Path):

    print("[CAMARA] Capturando imagen...")

    subprocess.run(
        [
            "rpicam-still",
            "-n",
            "-t", "2000",
            "--width", "1600",
            "--height", "1200",
            "-o", str(image_path)
        ],
        check=True,
        timeout=30
    )

    print("[CAMARA] Imagen capturada.")


# ==============================
# EVALUACION DE NITIDEZ
# ==============================

def calculate_sharpness(image_path: Path):

    with Image.open(image_path) as image:

        gray = ImageOps.grayscale(image)

        pixels = np.asarray(
            gray,
            dtype=np.float32
        )

    laplacian = (
        -4 * pixels[1:-1, 1:-1]
        + pixels[:-2, 1:-1]
        + pixels[2:, 1:-1]
        + pixels[1:-1, :-2]
        + pixels[1:-1, 2:]
    )

    return float(np.var(laplacian))


# ==============================
# COMUNICACION CON EL SERVIDOR
# ==============================

def ask_server(image_path: Path, mode: str):

    print("[RED] Enviando imagen al servidor...")

    with image_path.open("rb") as image:

        response = requests.post(
            SERVER_URL + "/process",
            files={
                "file": (
                    "captura.jpg",
                    image,
                    "image/jpeg"
                )
            },
            data={"mode": mode},
            headers={"X-Token": API_TOKEN},
            timeout=TIMEOUT
        )

    response.raise_for_status()

    result = response.json()

    print("[RED] Respuesta recibida.")

    return result


# ==============================
# PROCESAMIENTO PRINCIPAL
# ==============================

def process_once(mode="leer", ignore_blur=False):

    start = time.monotonic()

    with tempfile.TemporaryDirectory() as folder:

        image_path = Path(folder) / "captura.jpg"

        # 1. Capturar fotografia
        capture(image_path)

        # 2. Evaluar nitidez
        sharpness = calculate_sharpness(image_path)

        print(f"[CAMARA] Nitidez: {sharpness:.2f}")

        if sharpness < BLUR_MIN and not ignore_blur:

            print("[AVISO] Imagen posiblemente borrosa.")

            speak_local(
                "La imagen está borrosa. "
                "Intenta apuntar nuevamente."
            )

            return

        # 3. Enviar al servidor
        try:

            result = ask_server(image_path, mode)

        except requests.RequestException as error:

            print(f"[ERROR] Servidor: {error}")

            speak_local(
                "No pude obtener una respuesta del servidor."
            )

            return

        # 4. Mostrar resultado
        print("\n--- RESULTADO ---")
        print(f"Modo: {result['mode']}")
        print(f"Texto: {result['text']}")
        print(f"Confianza: {result['conf'] * 100:.2f}%")
        print(f"Estado: {result['hint']}")

        # 5. Decodificar audio
        audio = base64.b64decode(
            result["audio"],
            validate=True
        )

        elapsed = time.monotonic() - start

        print(f"Tiempo hasta reproducción: {elapsed:.2f} s")

        # 6. Reproducir en audifonos
        print("[AUDIO] Reproduciendo respuesta...")

        play_audio(audio)

        print("[AUDIO] Reproduccion finalizada.")


# ==============================
# PUNTO DE ENTRADA
# ==============================

def main():

    parser = argparse.ArgumentParser(
        description="Smart Glasses"
    )

    parser.add_argument(
        "--once",
        choices=["leer", "billetes", "describir"],
        default="leer"
    )

    parser.add_argument(
        "--ignore-blur",
        action="store_true"
    )

    args = parser.parse_args()

    if not SERVER_URL or not API_TOKEN:

        print("[ERROR] Configura el archivo .env")

        return 1

    print("============================")
    print("     SMART GLASSES AI")
    print("============================")

    print(f"Servidor: {SERVER_URL}")
    print(f"Modo: {args.once}")

    try:

        process_once(
            args.once,
            args.ignore_blur
        )

    except (
        subprocess.SubprocessError,
        OSError,
        ValueError,
        KeyError,
        binascii.Error
    ) as error:

        print(f"[ERROR] {error}")

        return 1

    return 0


if __name__ == "__main__":

    sys.exit(main())
