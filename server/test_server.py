
import requests
import base64
import sys
import os

from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

SERVER_URL = os.getenv(
    "GLASSES_SERVER",
    "http://127.0.0.1:8000"
).rstrip("/") + "/process"

API_TOKEN = os.getenv("API_TOKEN", "")


def test_server(image_path, mode="leer"):

    image_path = Path(image_path)

    if not image_path.is_file():
        print("La imagen no existe.")
        return

    print("Enviando imagen al servidor...")

    try:

        with image_path.open("rb") as image:

            response = requests.post(
                SERVER_URL,
                files={"file": (image_path.name, image)},
                data={"mode": mode},
                headers={"X-Token": API_TOKEN},
                timeout=60
            )

    except requests.RequestException as error:

        print(f"Error de conexion: {error}")
        return

    if response.status_code != 200:

        print(f"Error HTTP: {response.status_code}")
        print(response.text)
        return

    result = response.json()

    print("\n--- RESULTADO ---")
    print(f"Modo: {result['mode']}")
    print(f"Texto: {result['text']}")
    print(f"Confianza: {result['conf'] * 100:.2f}%")
    print(f"Palabras: {result['words']}")
    print(f"Estado: {result['hint']}")

    audio_bytes = base64.b64decode(result["audio"])

    output = BASE_DIR / "respuesta.wav"

    output.write_bytes(audio_bytes)

    print(f"\nAudio guardado en: {output}")

    if sys.platform == "win32":

        import winsound

        winsound.PlaySound(
            str(output),
            winsound.SND_FILENAME
        )


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Uso: python test_server.py imagen.png leer")
        sys.exit(1)

    image_path = sys.argv[1]

    mode = sys.argv[2] if len(sys.argv) > 2 else "leer"

    test_server(image_path, mode)
