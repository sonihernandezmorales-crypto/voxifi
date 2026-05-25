from flask import Flask, render_template, request, send_file, jsonify
import os
import asyncio
import edge_tts
import time

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# -------------------------
# VOICE GENERATION (EDGE-TTS)
# -------------------------
async def generate_voice(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/audio", methods=["POST"])
def audio():
    text = request.form.get("text")
    voice = request.form.get("voice")

    if not text:
        return jsonify({"error": "Texto vacío"}), 400

    audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

    run_async(generate_voice(text, voice, audio_path))

    return jsonify({"ok": True})


@app.route("/audio-file")
def audio_file():
    audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

    if not os.path.exists(audio_path):
        return jsonify({"error": "Audio no encontrado"}), 404

    return send_file(audio_path)


@app.route("/download-audio")
def download_audio():
    audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

    if not os.path.exists(audio_path):
        return jsonify({"error": "Audio no encontrado"}), 404

    return send_file(audio_path, as_attachment=True)


@app.route("/upload", methods=["POST"])
def upload():

    # 🔥 IMPORT CORRECTO PARA RENDER (EVITA moviepy.editor ERROR)
    import moviepy.video.io.VideoFileClip as vfc
    import moviepy.audio.io.AudioFileClip as afc

    if "video" not in request.files:
        return jsonify({"error": "No hay video"}), 400

    video = request.files["video"]
    text = request.form.get("text")
    voice = request.form.get("voice")

    if video.filename == "":
        return jsonify({"error": "Video vacío"}), 400

    timestamp = int(time.time())

    video_path = os.path.join(UPLOAD_FOLDER, f"video_{timestamp}.mp4")
    audio_path = os.path.join(UPLOAD_FOLDER, f"audio_{timestamp}.mp3")
    output_path = os.path.join(OUTPUT_FOLDER, f"video_final_{timestamp}.mp4")

    video.save(video