
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
from io import BytesIO

app = FastAPI(
    title="Smart Glasses API",
    description="Servidor para lentes inteligentes con IA",
    version="0.2.0"
)


@app.get("/")
def root():
    return {
        "message": "Smart Glasses API funcionando"
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "Smart Glasses API"
    }


@app.post("/process")
async def process_image(file: UploadFile = File(...)):

    # Leer los bytes de la imagen recibida
    contents = await file.read()

    # Verificar que sea una imagen válida
    try:
        image = Image.open(BytesIO(contents))
        image.load()

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="El archivo enviado no es una imagen valida"
        )

    # Obtener las dimensiones
    width, height = image.size

    # Devolver informacion de la imagen
    return {
        "ok": True,
        "message": "Imagen recibida correctamente",
        "filename": file.filename,
        "format": image.format,
        "width": width,
        "height": height
    }
