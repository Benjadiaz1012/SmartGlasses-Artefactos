
import wave
import base64

from io import BytesIO
from pathlib import Path
from functools import lru_cache
from threading import Lock
from piper import PiperVoice


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "es_MX-claude-high.onnx"
)

voice_lock = Lock()


@lru_cache(maxsize=1)
def load_voice():
    return PiperVoice.load(str(MODEL_PATH))


def generate_audio(text: str) -> bytes:

    with voice_lock:

        voice = load_voice()

        buffer = BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        return buffer.getvalue()


def audio_to_base64(audio: bytes) -> str:

    return base64.b64encode(audio).decode("utf-8")


if __name__ == "__main__":

    text = (
        "Hola. Los lentes inteligentes "
        "están funcionando correctamente."
    )

    audio = generate_audio(text)

    output = Path(__file__).parent / "prueba.wav"
    output.write_bytes(audio)

    print("Audio generado correctamente.")
    print(f"Archivo: {output}")
