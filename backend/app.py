from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, handle_file
import tempfile, os

app = Flask(__name__)

# ✅ CORS configuration (allows frontend → backend communication)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://accento-prototype.netlify.app/"
        ]
    }
})

# ✅ Load your Hugging Face model
client = Client("Gitanjaliyadav29/accento-ml-model")


@app.route("/api/predict", methods=["POST"])
def predict_accent():
    # Check for file upload
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio = request.files["audio"]
    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in [".wav", ".mp3"]:
        return jsonify({"error": "Invalid file type. Please upload .wav or .mp3"}), 400

    # Save temp file for processing
    temp_path = tempfile.mktemp(suffix=ext)
    audio.save(temp_path)

    try:
        # Run prediction via Hugging Face Gradio Client
        result = client.predict(audio_file=handle_file(temp_path), api_name="/predict")
        return jsonify({"prediction": result})
    except Exception as e:
        print("❌ Prediction error:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/", methods=["GET"])
def index():
    # Optional: helpful homepage message for sanity check
    return jsonify({"message": "Accento Flask API is live!", "status": "OK"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
