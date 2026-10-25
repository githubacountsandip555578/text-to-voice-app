from flask import Flask, request, send_file, jsonify, send_from_directory
import edge_tts
import asyncio
import io
import os

app = Flask(__name__)

@app.route("/")
def home():
    folder = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(folder, "voice.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    voice = data.get("voice", "hi-IN-SwaraNeural")
    rate = data.get("rate", "+0%")
    pitch = data.get("pitch", "+0Hz")

    if not text:
        return jsonify({"error": "Pehle text likho"}), 400

    async def make_audio():
        communicate = edge_tts.Communicate(
            text, voice, rate=rate, pitch=pitch
        )
        audio = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
        return bytes(audio)

    try:
        audio = asyncio.run(make_audio())
        if not audio:
            return jsonify({"error": "Audio nahi bana"}), 502

        return send_file(
            io.BytesIO(audio),
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="my-voice.mp3"
        )
    except Exception as exc:
        app.logger.exception("MP3 generation failed")
        return jsonify({"error": str(exc)}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)