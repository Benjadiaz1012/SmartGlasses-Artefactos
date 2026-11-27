
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import pytesseract
import logging

from ocr import extract_text
from tts import generate_audio, audio_to_base64


app = FastAPI(
    title="Smart Glasses API",
    description="Servidor para lentes inteligentes con IA",
    version="0.4.0"
)

logger = logging.getLogger("uvicorn.error")

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MIN_CONF = 0.60


@app.get("/")
def root():
    return {
        "message": "Smart Glasses API funcionando"
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "Smart Glasses API",
        "ocr_engine": "tesseract",
        "tts_engine": "piper"
    }


@app.post("/process")
def process_image(
    file: UploadFile = File(...),
    mode: str = Form("leer")
):

    # 1. Recibir imagen
    contents = file.file.read(MAX_IMAGE_SIZE + 1)

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera los 10 MB"
        )

    # 2. Validar imagen
    try:
        image = Image.open(BytesIO(contents))

        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail="La resolucion de la imagen es demasiado grande"
            )

        image.load()

    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError
    ):
        raise HTTPException(
            status_code=400,
            detail="El archivo enviado no es una imagen valida"
        )

    # 3. Validar modo de funcionamiento
    if mode not in ("leer", "billetes", "describir"):
        raise HTTPException(
            status_code=400,
            detail="Modo no reconocido"
        )

    # 4. Procesar segun el modo
    if mode == "leer":

        try:
            result = extract_text(image)

        except pytesseract.TesseractNotFoundError:
            raise HTTPException(
                status_code=500,
                detail="Tesseract no esta instalado"
            )

        except Exception:
            logger.exception("Error durante el OCR")
            raise HTTPException(
                status_code=500,
                detail="Error durante el reconocimiento OCR"
            )

        text = result["text"]
        conf = result["conf"]
        words = result["words"]

        # Determinar el mensaje que escuchara el usuario
        if not text:
            hint = "no_text"
            speech = (
                "No encontré texto en la imagen. "
                "Intenta apuntar nuevamente."
            )

        elif conf < MIN_CONF:
            hint = "low_conf"
            speech = (
                "La lectura puede ser incorrecta. "
                + text
            )

        else:
            hint = "ok"
            speech = text

    else:
        # Modos pendientes de implementar
        text = ""
        conf = 0
        words = 0
        hint = "not_available"

        speech = (
            f"El modo {mode} todavía no está disponible."
        )

    # 5. Generar audio
    try:
        audio_bytes = generate_audio(speech)
        audio_base64 = audio_to_base64(audio_bytes)

    except Exception:
        logger.exception("Error durante la generacion de audio")
        raise HTTPException(
            status_code=500,
            detail="Error durante la generacion de audio"
        )

    # 6. Devolver resultado completo
    return {
        "ok": True,
        "mode": mode,
        "filename": file.filename,
        "format": image.format,
        "width": image.width,
        "height": image.height,
        "text": text,
        "conf": conf,
        "words": words,
        "hint": hint,
        "audio": audio_base64,
        "audio_format": "wav"
    }
