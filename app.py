from flask import Flask, request, jsonify
from ocr_utils import is_barcode_or_label, extract_protein_info
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "OCR Service is up and running!", 200

@app.route("/check-label", methods=["POST"])
def check_label():
    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request"}), 400

    try:
        result = is_barcode_or_label(data["image_path"])
        return jsonify({"is_nutrition_label": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract-protein", methods=["POST"])
def extract_protein():
    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request"}), 400

    try:
        result = extract_protein_info(data["image_path"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
