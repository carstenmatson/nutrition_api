# app.py
from flask import Flask, request, jsonify
from ocr_utils import is_barcode_or_label, extract_protein_info
import requests
import tempfile
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "\ud83d\udce6 Nutrition OCR API Ready", 200

@app.route("/analyze", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        if not data or "image_path" not in data:
            return jsonify({"error": "Missing 'image_path' in request"}), 400

        image_url = data["image_path"]
        user_id = data.get("user_id")  # Optional for Firebase

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Could not download image"}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        if not is_barcode_or_label(tmp_path):
            return jsonify({
                "type": "food",
                "message": "No nutrition label detected."
            })

        result = extract_protein_info(tmp_path, image_url=image_url, user_id=user_id)
        return jsonify({
            "type": "nutrition_label",
            "data": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
