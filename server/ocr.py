
import pytesseract
from PIL import Image, ImageOps
from pytesseract import Output


def extract_text(image: Image.Image) -> dict:

    # Convertir la imagen a escala de grises
    image = ImageOps.grayscale(image)

    # Mejorar el contraste
    image = ImageOps.autocontrast(image)

    # Ejecutar el reconocimiento de texto
    data = pytesseract.image_to_data(
        image,
        lang="spa+eng",
        config="--oem 3 --psm 3",
        output_type=Output.DICT,
        timeout=20
    )

    words = []
    confidences = []

    # Recorrer las palabras reconocidas
    for i in range(len(data["text"])):

        word = data["text"][i].strip()
        confidence = float(data["conf"][i])

        if word and confidence >= 0:
            words.append(word)
            confidences.append(confidence)

    # Unir las palabras reconocidas
    text = " ".join(words)

    # Calcular confianza promedio
    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences else 0
    )

    return {
        "text": text,
        "conf": round(average_confidence / 100, 4),
        "words": len(words)
    }
