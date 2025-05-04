import subprocess
import tempfile
import os
import whisper

# Load Whisper model on first use
_model = None

def extract_audio_and_transcribe(video_path):
    """Extract audio using ffmpeg and transcribe with Whisper."""
    global _model
    # Lazy load model
    if _model is None:
        _model = whisper.load_model("small")

    # Create temp WAV file
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_wav.close()

    # Extract audio via ffmpeg CLI
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1", "-ar", "16000", temp_wav.name
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    result = _model.transcribe(temp_wav.name)

    os.remove(temp_wav.name)

    return result.get("text", "").strip()
