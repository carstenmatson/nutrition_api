# app.py
from flask import Flask, request, jsonify
from ocr_utils import is_barcode_or_label, extract_protein_info
import requests
import tempfile

app = Flask(__name__)

@app.route("/")
def home():
    return "📦 Nutrition OCR API Ready", 200

@app.route("/analyze", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        if not data or "image_path" not in data:
            return jsonify({"error": "Missing 'image_path' in request"}), 400

        image_url = data["image_path"]
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

        protein_data = extract_protein_info(tmp_path)
        return jsonify({
            "type": "nutrition_label",
            "data": protein_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from gunicorn.app.base import BaseApplication

    class StandaloneApp(BaseApplication):
        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {}
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {
        "bind": "0.0.0.0:10000",
        "workers": 1
    }

    StandaloneApp(app, options).run()
