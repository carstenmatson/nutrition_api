# server.py
from flask import Flask, request, jsonify
from ocr_utils import is_barcode_or_label, extract_protein_info
import os

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze_image():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)

    try:
        if is_barcode_or_label(file_path):
            result = extract_protein_info(file_path)
            return jsonify({"type": "nutrition_label", "data": result})
        else:
            return jsonify({"type": "food_image"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()