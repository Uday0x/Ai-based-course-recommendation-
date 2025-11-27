from PIL import Image
import numpy as np
import cv2
import pytesseract
from typing import Dict, Any

def pil_to_cv2(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def cv2_to_pil(img: np.ndarray) -> Image.Image:
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

def preprocess_image(image: Image.Image, method: str = "none") -> Image.Image:
    """
    Simple preprocessing to improve OCR:
    - grayscale
    - binarize (Otsu)
    - denoise (median blur)
    """
    img = pil_to_cv2(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if method == "none":
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if method == "grayscale":
        return Image.fromarray(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB))
    if method == "binarize":
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(cv2.cvtColor(th, cv2.COLOR_GRAY2RGB))
    if method == "denoise":
        den = cv2.medianBlur(gray, 3)
        return Image.fromarray(cv2.cvtColor(den, cv2.COLOR_GRAY2RGB))
    # unknown method -> return original
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def run_ocr(image: Image.Image) -> Dict[str, Any]:
    """
    Runs Tesseract OCR and returns:
    - text: full text
    - words: list of {text,left,top,width,height,conf}
    """
    # Convert to RGB bytes for pytesseract
    img = image
    # full text
    text = pytesseract.image_to_string(img)
    # word-level data
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words = []
    n = len(data.get("text", []))
    for i in range(n):
        w = data["text"][i].strip()
        if not w:
            continue
        conf = int(float(data["conf"][i])) if data["conf"][i] not in (None, "", "-1") else -1
        words.append({
            "text": w,
            "left": int(data["left"][i]),
            "top": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "conf": conf
        })
    return {"text": text, "words": words}