from flask import Flask, render_template, request, send_file, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import asyncio
import edge_tts
import time

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


async def generate_voice(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/audio", methods=["POST"])
def audio():
    text = request.form.get("text")
    voice = request.form.get("voice")

    audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

    asyncio.run(generate_voice(text, voice, audio_path))

    return jsonify({"ok": True})


@app.route("/audio-file")
def audio_file():
    return send_file(os.path.join(UPLOAD_FOLDER, "audio.mp3"))


@app.route("/download-audio")
def download_audio():
    return send_file(os.path.join(UPLOAD_FOLDER, "audio.mp3"), as_attachment=True)


@app.route("/upload", methods=["POST"])
def upload():

    video = request.files["video"]
    text = request.form.get("text")
    voice = request.form.get("voice")

    timestamp = int(time.time())

    video_path = os.path.join(UPLOAD_FOLDER, f"video_{timestamp}.mp4")
    audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")
    output_path = os.path.join(OUTPUT_FOLDER, f"video_final_{timestamp}.mp4")

    video.save(video_path)

    asyncio.run(generate_voice(text, voice, audio_path))

    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    final = video_clip.set_audio(audio_clip)

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=24
    )

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)