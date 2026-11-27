
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import pytesseract

from ocr import extract_text


app = FastAPI(
    title="Smart Glasses API",
    description="Servidor para lentes inteligentes con IA",
    version="0.3.0"
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024


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
        "ocr_engine": "tesseract"
    }


@app.post("/process")
def process_image(file: UploadFile = File(...)):

    # Recibir imagen
    contents = file.file.read(MAX_IMAGE_SIZE + 1)

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera los 10 MB"
        )

    # Validar imagen
    try:
        image = Image.open(BytesIO(contents))
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

    # Ejecutar OCR
    try:
        result = extract_text(image)

    except pytesseract.TesseractNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Tesseract no esta instalado o no esta en el PATH"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error durante el reconocimiento OCR"
        )

    # Determinar calidad de lectura
    if not result["text"]:
        hint = "no_text"

    elif result["conf"] < 0.60:
        hint = "low_conf"

    else:
        hint = "ok"

    # Devolver resultado
    return {
        "ok": True,
        "filename": file.filename,
        "format": image.format,
        "width": image.width,
        "height": image.height,
        "text": result["text"],
        "conf": result["conf"],
        "words": result["words"],
        "hint": hint
    }
