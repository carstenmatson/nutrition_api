# ocr_utils.py
import cv2
import numpy as np
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # ✅ Required for Docker slim images
import re
import os
import requests
import datetime
import json
import jwt
import time
import uuid
from google.auth.transport.requests import Request

# Firebase service account credentials (safe only if you're self-hosting securely)
SERVICE_ACCOUNT = {
  "type": "service_account",
  "project_id": "feastify-food-recipe-ap-xq4ggq",
  "private_key_id": "7752f7aa2a2e15b36603562222bdb434ae7bf9fe",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCstD8EdSDnDHEE\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@feastify-food-recipe-ap-xq4ggq.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token"
}

FIREBASE_API_URL = "https://firestore.googleapis.com/v1/projects/feastify-food-recipe-ap-xq4ggq/databases/(default)/documents"

def get_firebase_access_token():
    issued_at = int(time.time())
    expiry = issued_at + 3600

    payload = {
        "iss": SERVICE_ACCOUNT["client_email"],
        "scope": "https://www.googleapis.com/auth/datastore",
        "aud": SERVICE_ACCOUNT["token_uri"],
        "iat": issued_at,
        "exp": expiry
    }

    jwt_token = jwt.encode(payload, SERVICE_ACCOUNT["private_key"], algorithm='RS256')

    response = requests.post(
        SERVICE_ACCOUNT["token_uri"],
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token
        }
    )
    return response.json().get("access_token")

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

    return any(keyword.lower() in text.lower() for keyword in nutrition_keywords)

def extract_protein_info(img_path: str, image_url: str = None, user_id: str = None):
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)

    protein_match = re.search(r"Protein\s*:?\s*(\d+\.?\d*)\s*(g|G)", text)
    serving_size_match = re.search(r"Serving\s*size\s*(?:\S+\s*)?\(?\s*(\d+\.?\d*)\s*(g|ml|G|ML)\)?", text, re.IGNORECASE)
    servings_per_container_match = re.search(r"(\d+)\s*servings\s*per\s*container", text, re.IGNORECASE)

    protein_per_serving = float(protein_match.group(1)) if protein_match else None
    serving_size = float(serving_size_match.group(1)) if serving_size_match else None
    servings_per_container = int(servings_per_container_match.group(1)) if servings_per_container_match else None

    total_protein = protein_per_serving * servings_per_container if protein_per_serving and servings_per_container else None

    if image_url and user_id:
        access_token = get_firebase_access_token()
        now = datetime.datetime.utcnow().isoformat("T") + "Z"

        payload = {
            "fields": {
                "image_url": {"stringValue": image_url},
                "date": {"timestampValue": now},
                "protein_detected_g": {"integerValue": str(int(protein_per_serving or 0))},
                "consumption_percent": {"integerValue": "100"},
                "adjusted_protein_g": {"integerValue": str(int(total_protein or 0))},
                "created_at": {"timestampValue": now},
                "user_id": {
                    "referenceValue": f"projects/feastify-food-recipe-ap-xq4ggq/databases/(default)/documents/users/{user_id}"
                }
            }
        }

        requests.post(
            f"{FIREBASE_API_URL}/protein_logs",
            headers={"Authorization": f"Bearer {access_token}"},
            data=json.dumps(payload)
        )

    return {
        "protein_per_serving_g": protein_per_serving,
        "serving_size_g_or_ml": serving_size,
        "servings_per_container": servings_per_container,
        "total_protein_g": total_protein
    }

