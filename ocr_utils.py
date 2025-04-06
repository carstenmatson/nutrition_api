# ocr_utils.py
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

def is_barcode_or_label(img_path: str) -> bool:
    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be read.")

    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)

    nutrition_keywords = [
        "Calories", "Protein", "Fat", "Sodium", "Carbohydrate",
        "Cholesterol", "Serving Size", "Amount per serving", "Servings Per Container"
    ]

    for keyword in nutrition_keywords:
        if keyword.lower() in text.lower():
            return True

    return False

def extract_protein_info(img_path: str):
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)

    protein_match = re.search(r"Protein\s*:?\s*(\d+\.?\d*)\s*(g|G)", text)
    serving_size_match = re.search(r"Serving\s*size\s*(?:\S+\s*)?\(?\s*(\d+\.?\d*)\s*(g|ml|G|ML)\)?", text, re.IGNORECASE)
    servings_per_container_match = re.search(r"(\d+)\s*servings\s*per\s*container", text, re.IGNORECASE)

    protein_per_serving = float(protein_match.group(1)) if protein_match else None
    serving_size = float(serving_size_match.group(1)) if serving_size_match else None
    servings_per_container = int(servings_per_container_match.group(1)) if servings_per_container_match else None

    total_protein = protein_per_serving * servings_per_container if protein_per_serving and servings_per_container else None

    return {
        "protein_per_serving_g": protein_per_serving,
        "serving_size_g_or_ml": serving_size,
        "servings_per_container": servings_per_container,
        "total_protein_g": total_protein
    }