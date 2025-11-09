from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
from flask_cors import CORS
import tempfile
import os

app = Flask(__name__)
# Enable CORS for local frontend dev server
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# Initialize the Hugging Face Space client
client = Client("Gitanjaliyadav29/accento-ml-model")

@app.route("/api/predict", methods=["POST"])
def predict_accent():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    # Save uploaded file temporarily
    audio = request.files["audio"]

    # Validate file extension
    filename = audio.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".wav", ".mp3"]:
        return jsonify({"error": "Invalid file type. Only .wav or .mp3 allowed."}), 400

    # Save uploaded file temporarily, keep original extension
    temp_path = tempfile.mktemp(suffix=ext)
    audio.save(temp_path)

    try:
        result = client.predict(
            audio_file=handle_file(temp_path),
            api_name="/predict"
        )
        return jsonify({"prediction": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    app.run(debug=True)
